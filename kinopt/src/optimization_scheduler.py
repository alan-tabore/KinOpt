"""Execute persisted optimization jobs sequentially or in child processes."""

from dataclasses import dataclass
from multiprocessing import get_context
import os
import time
from typing import Callable, List, Optional

from kinopt.src.optimization_queue import (
    JobStatus,
    OptimizationJob,
    OptimizationQueue,
)
from kinopt.src.optimization_runner import (
    OptimizationCancelled,
    run_optimization,
)
from kinopt.src.optimization_serialization import (
    deserialize_config,
    serialize_config,
)


def optimization_process_cost(config, cpu_count=None):
    """Estimate the global process budget consumed by one configuration."""
    available_cpus = max(1, int(cpu_count or os.cpu_count() or 1))
    options = config.global_options or {}
    workers = options.get("workers", 1)
    if isinstance(workers, bool) or not isinstance(workers, int):
        return 1
    if workers == -1:
        return available_cpus
    return max(1, abs(workers))


def _optimization_process_entry(
    identifier,
    serialized_config,
    cancellation_event,
    result_connection,
):
    """Run one serialized configuration in a spawn-safe child process."""
    try:
        config = deserialize_config(serialized_config)
        progress_callback = lambda progress: result_connection.send(
            (identifier, "progress", progress)
        )
        if config.exploratory_fraction is None:
            outcome = run_optimization(
                config,
                is_cancelled=cancellation_event.is_set,
                progress_callback=progress_callback,
            )
        else:
            from kinopt.src.optimization_strategies import (
                run_exploratory_then_full,
            )
            outcome = run_exploratory_then_full(
                config,
                fraction=config.exploratory_fraction,
                budget_fraction=config.exploratory_budget_fraction,
                is_cancelled=cancellation_event.is_set,
                progress_callback=progress_callback,
            )
        result_connection.send((identifier, "completed", outcome))
    except OptimizationCancelled:
        result_connection.send(
            (identifier, "cancelled", "Optimization cancelled.")
        )
    except Exception as error:
        result_connection.send(
            (identifier, "failed", f"{type(error).__name__}: {error}")
        )
    finally:
        result_connection.close()


@dataclass
class _ActiveProcess:
    job: OptimizationJob
    process: object
    cancellation_event: object
    result_connection: object
    process_cost: int


class SequentialOptimizationScheduler:
    """Run at most one queued optimization at a time."""

    def __init__(self, queue, runner=run_optimization):
        if not isinstance(queue, OptimizationQueue):
            raise TypeError("queue must be an OptimizationQueue.")
        self.queue = queue
        self.runner = runner

    def run_next(
        self,
        progress_callback: Optional[Callable] = None,
        cancellation_requested: Optional[Callable[[OptimizationJob], bool]] = None,
    ) -> Optional[OptimizationJob]:
        """Claim and finish one pending job, isolating solver failures."""
        job = self.queue.claim_next_pending()
        if job is None:
            return None

        callback = None
        if progress_callback is not None:
            def callback(*args, **kwargs):
                return progress_callback(job, *args, **kwargs)

        is_cancelled = None
        if cancellation_requested is not None:
            is_cancelled = lambda: cancellation_requested(job)

        try:
            outcome = self.runner(
                job.config,
                callback=callback,
                is_cancelled=is_cancelled,
            )
            return self.queue.complete(job.identifier, outcome)
        except OptimizationCancelled:
            return self.queue.set_status(
                job.identifier,
                JobStatus.CANCELLED,
                "Optimization cancelled.",
            )
        except Exception as error:
            return self.queue.set_status(
                job.identifier,
                JobStatus.FAILED,
                f"{type(error).__name__}: {error}",
            )

    def run_pending(
        self,
        progress_callback: Optional[Callable] = None,
        cancellation_requested: Optional[Callable[[OptimizationJob], bool]] = None,
        should_continue: Optional[Callable[[], bool]] = None,
        job_finished: Optional[Callable[[OptimizationJob], None]] = None,
    ) -> List[OptimizationJob]:
        """Run jobs in order until the queue is empty or launching is paused."""
        completed_jobs = []
        while should_continue is None or should_continue():
            job = self.run_next(
                progress_callback=progress_callback,
                cancellation_requested=cancellation_requested,
            )
            if job is None:
                break
            completed_jobs.append(job)
            if job_finished is not None:
                job_finished(job)
        return completed_jobs


class ConcurrentOptimizationScheduler:
    """Run queued jobs in isolated child processes within global limits."""

    def __init__(
        self,
        queue,
        max_concurrent_jobs=1,
        process_budget=None,
        *,
        process_context=None,
        process_target=_optimization_process_entry,
        poll_interval=0.02,
    ):
        if not isinstance(queue, OptimizationQueue):
            raise TypeError("queue must be an OptimizationQueue.")
        if isinstance(max_concurrent_jobs, bool) or max_concurrent_jobs < 1:
            raise ValueError("max_concurrent_jobs must be a positive integer.")
        available_cpus = max(1, os.cpu_count() or 1)
        if process_budget is None:
            process_budget = available_cpus
        if isinstance(process_budget, bool) or process_budget < 1:
            raise ValueError("process_budget must be a positive integer.")
        if poll_interval <= 0:
            raise ValueError("poll_interval must be positive.")

        self.queue = queue
        self.max_concurrent_jobs = int(max_concurrent_jobs)
        self.process_budget = int(process_budget)
        self.process_context = process_context or get_context("spawn")
        self.process_target = process_target
        self.poll_interval = float(poll_interval)
        self._active = {}

    @property
    def active_job_identifiers(self):
        """Return identifiers currently owned by live child processes."""
        return tuple(self._active)

    def cancel(self, identifier):
        """Request cooperative cancellation of one active job."""
        active = self._active.get(identifier)
        if active is None:
            return False
        active.cancellation_event.set()
        return True

    def _can_start(self, job):
        if len(self._active) >= self.max_concurrent_jobs:
            return False
        required = optimization_process_cost(job.config)
        used = sum(item.process_cost for item in self._active.values())
        return not self._active or used + required <= self.process_budget

    def _start_next(self):
        candidate = self.queue.peek_next_pending()
        if candidate is None or not self._can_start(candidate):
            return False
        job = self.queue.claim_next_pending(candidate.identifier)
        if job is None:
            return True

        cancellation_event = self.process_context.Event()
        result_connection, child_connection = self.process_context.Pipe(False)
        process = self.process_context.Process(
            target=self.process_target,
            args=(
                job.identifier,
                serialize_config(job.config),
                cancellation_event,
                child_connection,
            ),
            name=f"kinopt-job-{job.identifier[:8]}",
        )
        try:
            process.start()
        except Exception as error:
            child_connection.close()
            result_connection.close()
            self.queue.set_status(
                job.identifier,
                JobStatus.FAILED,
                f"Could not start optimization process: {error}",
            )
            return True
        child_connection.close()
        self._active[job.identifier] = _ActiveProcess(
            job=job,
            process=process,
            cancellation_event=cancellation_event,
            result_connection=result_connection,
            process_cost=optimization_process_cost(job.config),
        )
        return True

    def _finish(self, active, status, payload):
        active.process.join()
        active.process.close()
        active.result_connection.close()
        if status == "completed":
            return self.queue.complete(active.job.identifier, payload)
        if status == "cancelled":
            return self.queue.set_status(
                active.job.identifier,
                JobStatus.CANCELLED,
                str(payload),
            )
        return self.queue.set_status(
            active.job.identifier,
            JobStatus.FAILED,
            str(payload),
        )

    def _collect_finished(self, progress_callback=None):
        finished = []
        for identifier, active in tuple(self._active.items()):
            message = None
            while active.result_connection.poll():
                candidate = active.result_connection.recv()
                if candidate[1] == "progress":
                    if progress_callback is not None:
                        progress_callback(active.job, candidate[2])
                    continue
                message = candidate
                break
            if message is None and not active.process.is_alive():
                active.process.join()
                while active.result_connection.poll():
                    candidate = active.result_connection.recv()
                    if candidate[1] == "progress":
                        if progress_callback is not None:
                            progress_callback(active.job, candidate[2])
                    else:
                        message = candidate
                        break
                if message is None:
                    message = (
                        identifier,
                        "failed",
                        "Optimization process stopped without returning a result "
                        f"(exit code {active.process.exitcode}).",
                    )
            if message is None:
                continue
            returned_identifier, status, payload = message
            if returned_identifier != identifier:
                status = "failed"
                payload = "Optimization process returned an unexpected job identifier."
            self._active.pop(identifier)
            finished.append(self._finish(active, status, payload))
        return finished

    def run_pending(
        self,
        cancellation_requested: Optional[
            Callable[[OptimizationJob], bool]
        ] = None,
        should_continue: Optional[Callable[[], bool]] = None,
        job_finished: Optional[Callable[[OptimizationJob], None]] = None,
        active_jobs_changed: Optional[Callable[[tuple], None]] = None,
        progress_callback: Optional[Callable] = None,
    ) -> List[OptimizationJob]:
        """Process pending jobs until drained or new claims are paused."""
        completed_jobs = []
        accepting_jobs = True
        while True:
            if accepting_jobs and should_continue is not None:
                accepting_jobs = bool(should_continue())

            started = False
            while accepting_jobs and self._start_next():
                started = True
                if active_jobs_changed is not None:
                    active_jobs_changed(self.active_job_identifiers)
                if len(self._active) >= self.max_concurrent_jobs:
                    break

            if cancellation_requested is not None:
                for active in tuple(self._active.values()):
                    if cancellation_requested(active.job):
                        active.cancellation_event.set()

            finished = self._collect_finished(progress_callback)
            completed_jobs.extend(finished)
            if finished and active_jobs_changed is not None:
                active_jobs_changed(self.active_job_identifiers)
            if job_finished is not None:
                for job in finished:
                    job_finished(job)

            next_job = self.queue.peek_next_pending() if accepting_jobs else None
            if not self._active and next_job is None:
                break
            if not started and not finished:
                time.sleep(self.poll_interval)
        return completed_jobs
