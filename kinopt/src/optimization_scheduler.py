"""Sequentially execute persisted optimization jobs."""

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
