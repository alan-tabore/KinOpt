"""Persistent local storage for sequential optimization jobs."""

from dataclasses import dataclass
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from enum import Enum
import json
from pathlib import Path
import sqlite3
from typing import List, Optional
from uuid import uuid4

from kinopt.src.optimization_runner import (
    OptimizationProgress,
    OptimizationRunConfig,
    OptimizationRunResult,
)
from kinopt.src.optimization_serialization import (
    deserialize_config,
    serialize_config,
)


DATABASE_SCHEMA_VERSION = 4
RESULT_SCHEMA_VERSION = 1


class JobStatus(str, Enum):
    """Lifecycle states displayed by the future batch interface."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"


_ALLOWED_TRANSITIONS = {
    JobStatus.PENDING: {JobStatus.RUNNING, JobStatus.CANCELLED},
    JobStatus.RUNNING: {
        JobStatus.COMPLETED,
        JobStatus.FAILED,
        JobStatus.CANCELLED,
        JobStatus.INTERRUPTED,
    },
    JobStatus.FAILED: {JobStatus.PENDING},
    JobStatus.CANCELLED: {JobStatus.PENDING},
    JobStatus.INTERRUPTED: {JobStatus.PENDING, JobStatus.CANCELLED},
    JobStatus.COMPLETED: set(),
}


@dataclass(frozen=True)
class OptimizationJob:
    """One persisted optimization and its current queue state."""

    identifier: str
    name: str
    config: OptimizationRunConfig
    status: JobStatus
    position: int
    created_at: str
    updated_at: str
    message: Optional[str]
    started_at: Optional[str]
    finished_at: Optional[str]
    result: Optional["StoredOptimizationResult"]
    group_identifier: Optional[str]
    group_name: Optional[str]
    group_kind: Optional[str]
    group_seed: Optional[int]
    progress_history: tuple


@dataclass(frozen=True)
class StoredOptimizationResult:
    """Small, JSON-safe summary needed to inspect and compare a run."""

    parameters: tuple
    cost: float
    elapsed_seconds: float
    solver_success: Optional[bool]
    solver_message: str
    iterations: Optional[int]
    evaluations: Optional[int]


@dataclass(frozen=True)
class StoredOptimizationProgress:
    """One persisted progress sample for a running or interrupted job."""

    evaluations: int
    best_cost: float
    elapsed_seconds: float
    estimated_remaining_seconds: Optional[float]
    best_parameters: tuple


def _serialize_progress_history(history):
    return json.dumps(
        [
            {
                "evaluations": int(point.evaluations),
                "best_cost": float(point.best_cost),
                "elapsed_seconds": float(point.elapsed_seconds),
                "estimated_remaining_seconds": (
                    None
                    if point.estimated_remaining_seconds is None
                    else float(point.estimated_remaining_seconds)
                ),
                "best_parameters": [
                    float(value) for value in point.best_parameters
                ],
            }
            for point in history
        ],
        allow_nan=False,
        separators=(",", ":"),
    )


def _deserialize_progress_history(serialized):
    if not serialized:
        return ()
    try:
        payload = json.loads(serialized)
        return tuple(
            StoredOptimizationProgress(
                evaluations=int(item["evaluations"]),
                best_cost=float(item["best_cost"]),
                elapsed_seconds=float(item["elapsed_seconds"]),
                estimated_remaining_seconds=(
                    None
                    if item["estimated_remaining_seconds"] is None
                    else float(item["estimated_remaining_seconds"])
                ),
                best_parameters=tuple(
                    float(value) for value in item["best_parameters"]
                ),
            )
            for item in payload
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid stored optimization progress: {error}") from error


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _optional_int(value):
    return None if value is None else int(value)


def _serialize_result(outcome):
    if not isinstance(outcome, OptimizationRunResult):
        raise TypeError("Expected an OptimizationRunResult.")
    result = outcome.result
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "parameters": [float(value) for value in result.x],
        "cost": float(result.fun),
        "elapsed_seconds": float(outcome.elapsed_seconds),
        "solver_success": (
            None if not hasattr(result, "success") else bool(result.success)
        ),
        "solver_message": str(getattr(result, "message", "")),
        "iterations": _optional_int(getattr(result, "nit", None)),
        "evaluations": _optional_int(getattr(result, "nfev", None)),
    }
    return json.dumps(
        payload,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _deserialize_result(serialized):
    if serialized is None:
        return None
    try:
        payload = json.loads(serialized)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid stored optimization result: {error}") from error
    if payload.get("schema_version") != RESULT_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported optimization result schema: "
            f"{payload.get('schema_version')!r}"
        )
    return StoredOptimizationResult(
        parameters=tuple(float(value) for value in payload["parameters"]),
        cost=float(payload["cost"]),
        elapsed_seconds=float(payload["elapsed_seconds"]),
        solver_success=payload["solver_success"],
        solver_message=str(payload["solver_message"]),
        iterations=_optional_int(payload["iterations"]),
        evaluations=_optional_int(payload["evaluations"]),
    )


class OptimizationQueue:
    """Store optimization jobs in one SQLite database."""

    def __init__(self, database_path):
        self.database_path = Path(database_path).expanduser().resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 5000")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize_database(self):
        with self._connect() as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version < 0 or version > DATABASE_SCHEMA_VERSION:
                raise ValueError(
                    f"Unsupported optimization queue schema: {version}"
                )
            connection.execute("PRAGMA journal_mode = WAL")
            if version == 0:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS optimization_jobs (
                        identifier TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        config_json TEXT NOT NULL,
                        status TEXT NOT NULL,
                        position INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        message TEXT,
                        started_at TEXT,
                        finished_at TEXT,
                        result_json TEXT,
                        group_identifier TEXT,
                        group_name TEXT,
                        group_kind TEXT,
                        group_seed INTEGER,
                        progress_json TEXT
                    )
                    """
                )
            if version == 1:
                connection.execute(
                    "ALTER TABLE optimization_jobs ADD COLUMN started_at TEXT"
                )
                connection.execute(
                    "ALTER TABLE optimization_jobs ADD COLUMN finished_at TEXT"
                )
                connection.execute(
                    "ALTER TABLE optimization_jobs ADD COLUMN result_json TEXT"
                )
            if 0 < version < 3:
                connection.execute(
                    "ALTER TABLE optimization_jobs "
                    "ADD COLUMN group_identifier TEXT"
                )
                connection.execute(
                    "ALTER TABLE optimization_jobs ADD COLUMN group_name TEXT"
                )
                connection.execute(
                    "ALTER TABLE optimization_jobs ADD COLUMN group_kind TEXT"
                )
                connection.execute(
                    "ALTER TABLE optimization_jobs ADD COLUMN group_seed INTEGER"
                )
            if 0 < version < 4:
                connection.execute(
                    "ALTER TABLE optimization_jobs ADD COLUMN progress_json TEXT"
                )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS optimization_jobs_position
                ON optimization_jobs(position)
                """
            )
            if version < DATABASE_SCHEMA_VERSION:
                connection.execute(
                    f"PRAGMA user_version = {DATABASE_SCHEMA_VERSION}"
                )

    @staticmethod
    def _row_to_job(row):
        return OptimizationJob(
            identifier=row["identifier"],
            name=row["name"],
            config=deserialize_config(row["config_json"]),
            status=JobStatus(row["status"]),
            position=row["position"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            message=row["message"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            result=_deserialize_result(row["result_json"]),
            group_identifier=row["group_identifier"],
            group_name=row["group_name"],
            group_kind=row["group_kind"],
            group_seed=(
                None if row["group_seed"] is None else int(row["group_seed"])
            ),
            progress_history=_deserialize_progress_history(row["progress_json"]),
        )

    def add(self, config, name=None):
        """Append an immutable configuration to the queue."""
        return self.add_many((config,), (name,))[0]

    def add_many(
        self,
        configs,
        names=None,
        *,
        group_name=None,
        group_kind=None,
        group_seed=None,
    ):
        """Atomically append several immutable configurations to the queue."""
        configs = tuple(configs)
        if not configs:
            raise ValueError("At least one optimization configuration is required.")
        if names is None:
            names = (None,) * len(configs)
        else:
            names = tuple(names)
        if len(names) != len(configs):
            raise ValueError("Provide one name for each optimization configuration.")

        group_values = (group_name, group_kind, group_seed)
        if any(value is not None for value in group_values):
            normalized_group_kind = str(group_kind or "").strip()
            if not normalized_group_kind:
                raise ValueError("A grouped batch requires a group kind.")
            normalized_group_name = str(group_name or "").strip()
            if not normalized_group_name:
                normalized_group_name = "Optimization group"
            if isinstance(group_seed, bool) or (
                group_seed is not None and not isinstance(group_seed, int)
            ):
                raise TypeError("A group seed must be an integer or None.")
            if group_seed is not None and group_seed < 0:
                raise ValueError("A group seed must be zero or positive.")
            group_identifier = str(uuid4())
        else:
            normalized_group_name = None
            normalized_group_kind = None
            group_identifier = None

        serialized_configs = tuple(serialize_config(config) for config in configs)
        identifiers = tuple(str(uuid4()) for _ in configs)
        timestamp = _utc_now()
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT COALESCE(MAX(position), 0) + 1 FROM optimization_jobs"
            ).fetchone()
            first_position = int(row[0])
            for offset, (identifier, name, serialized) in enumerate(
                zip(identifiers, names, serialized_configs)
            ):
                position = first_position + offset
                job_name = str(name).strip() if name is not None else ""
                if not job_name:
                    job_name = f"Optimization {position:03d}"
                connection.execute(
                    """
                    INSERT INTO optimization_jobs (
                        identifier, name, config_json, status, position,
                        created_at, updated_at, message, group_identifier,
                        group_name, group_kind, group_seed
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?)
                    """,
                    (
                        identifier,
                        job_name,
                        serialized,
                        JobStatus.PENDING.value,
                        position,
                        timestamp,
                        timestamp,
                        group_identifier,
                        normalized_group_name,
                        normalized_group_kind,
                        group_seed,
                    ),
                )
        return [self.get(identifier) for identifier in identifiers]

    def record_completed(self, config, outcome, name=None):
        """Atomically add an optimization that already finished elsewhere."""
        serialized_config = serialize_config(config)
        serialized_result = _serialize_result(outcome)
        elapsed_seconds = float(outcome.elapsed_seconds)
        if elapsed_seconds < 0:
            raise ValueError("Optimization duration cannot be negative.")

        identifier = str(uuid4())
        finished_at = datetime.now(timezone.utc)
        started_at = finished_at - timedelta(seconds=elapsed_seconds)
        timestamp = finished_at.isoformat(timespec="microseconds")
        message = str(getattr(outcome.result, "message", "")) or None

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT COALESCE(MAX(position), 0) + 1 FROM optimization_jobs"
            ).fetchone()
            position = int(row[0])
            job_name = str(name).strip() if name is not None else ""
            if not job_name:
                job_name = f"Completed optimization {position:03d}"
            connection.execute(
                """
                INSERT INTO optimization_jobs (
                    identifier, name, config_json, status, position,
                    created_at, updated_at, message, started_at, finished_at,
                    result_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier,
                    job_name,
                    serialized_config,
                    JobStatus.COMPLETED.value,
                    position,
                    timestamp,
                    timestamp,
                    message,
                    started_at.isoformat(timespec="microseconds"),
                    timestamp,
                    serialized_result,
                ),
            )
        return self.get(identifier)

    def get(self, identifier):
        """Return one job or raise a clear error for an unknown identifier."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM optimization_jobs WHERE identifier = ?",
                (identifier,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Unknown optimization job: {identifier}")
        return self._row_to_job(row)

    def list_jobs(self) -> List[OptimizationJob]:
        """Return every job in queue order."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM optimization_jobs ORDER BY position, created_at"
            ).fetchall()
        return [self._row_to_job(row) for row in rows]

    def duplicate(self, identifier, name=None):
        """Append a new pending job with a selected job's configuration."""
        source = self.get(identifier)
        duplicate_name = str(name).strip() if name is not None else ""
        if not duplicate_name:
            duplicate_name = f"{source.name} copy"
        return self.add(source.config, duplicate_name)

    def move_pending(self, identifier, direction):
        """Move a pending job before or after the nearest pending job."""
        if direction not in (-1, 1):
            raise ValueError("direction must be -1 or 1.")
        comparison = "<" if direction < 0 else ">"
        ordering = "DESC" if direction < 0 else "ASC"
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT status, position FROM optimization_jobs
                WHERE identifier = ?
                """,
                (identifier,),
            ).fetchone()
            if row is None:
                raise KeyError(f"Unknown optimization job: {identifier}")
            if JobStatus(row["status"]) is not JobStatus.PENDING:
                raise ValueError("Only pending jobs can be reordered.")
            neighbour = connection.execute(
                f"""
                SELECT identifier, position FROM optimization_jobs
                WHERE status = ? AND position {comparison} ?
                ORDER BY position {ordering}, created_at {ordering}
                LIMIT 1
                """,
                (JobStatus.PENDING.value, row["position"]),
            ).fetchone()
            if neighbour is not None:
                timestamp = _utc_now()
                connection.execute(
                    """
                    UPDATE optimization_jobs
                    SET position = CASE identifier
                        WHEN ? THEN ?
                        WHEN ? THEN ?
                    END,
                    updated_at = ?
                    WHERE identifier IN (?, ?)
                    """,
                    (
                        identifier,
                        neighbour["position"],
                        neighbour["identifier"],
                        row["position"],
                        timestamp,
                        identifier,
                        neighbour["identifier"],
                    ),
                )
        return self.get(identifier)

    def delete(self, identifier):
        """Delete an inactive job and compact the remaining queue positions."""
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT status FROM optimization_jobs WHERE identifier = ?",
                (identifier,),
            ).fetchone()
            if row is None:
                raise KeyError(f"Unknown optimization job: {identifier}")
            if JobStatus(row["status"]) is JobStatus.RUNNING:
                raise ValueError("A running job cannot be deleted.")
            connection.execute(
                "DELETE FROM optimization_jobs WHERE identifier = ?",
                (identifier,),
            )
            remaining = connection.execute(
                """
                SELECT identifier FROM optimization_jobs
                ORDER BY position, created_at
                """
            ).fetchall()
            connection.executemany(
                """
                UPDATE optimization_jobs SET position = ?
                WHERE identifier = ?
                """,
                (
                    (position, job["identifier"])
                    for position, job in enumerate(remaining, start=1)
                ),
            )

    def set_status(self, identifier, status, message=None):
        """Apply one valid lifecycle transition and persist its message."""
        requested_status = JobStatus(status)
        if requested_status is JobStatus.COMPLETED:
            raise ValueError("Use complete() to store a completed job result.")
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT status, started_at, finished_at, result_json, progress_json
                FROM optimization_jobs WHERE identifier = ?
                """,
                (identifier,),
            ).fetchone()
            if row is None:
                raise KeyError(f"Unknown optimization job: {identifier}")
            current_status = JobStatus(row["status"])
            if requested_status not in _ALLOWED_TRANSITIONS[current_status]:
                raise ValueError(
                    f"Cannot change job {identifier} from "
                    f"{current_status.value} to {requested_status.value}."
                )
            timestamp = _utc_now()
            started_at = row["started_at"]
            finished_at = row["finished_at"]
            result_json = row["result_json"]
            progress_json = row["progress_json"]
            if requested_status is JobStatus.RUNNING:
                started_at = timestamp
                finished_at = None
                progress_json = None
            elif requested_status in {
                JobStatus.FAILED,
                JobStatus.CANCELLED,
                JobStatus.INTERRUPTED,
            }:
                finished_at = timestamp
            elif requested_status is JobStatus.PENDING:
                started_at = None
                finished_at = None
                result_json = None
                progress_json = None
            cursor = connection.execute(
                """
                UPDATE optimization_jobs
                SET status = ?, updated_at = ?, message = ?,
                    started_at = ?, finished_at = ?, result_json = ?,
                    progress_json = ?
                WHERE identifier = ? AND status = ?
                """,
                (
                    requested_status.value,
                    timestamp,
                    None if message is None else str(message),
                    started_at,
                    finished_at,
                    result_json,
                    progress_json,
                    identifier,
                    current_status.value,
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    f"Optimization job {identifier} changed concurrently."
                )
        return self.get(identifier)

    def peek_next_pending(self):
        """Return the first pending job without changing its state."""
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM optimization_jobs
                WHERE status = ?
                ORDER BY position, created_at
                LIMIT 1
                """,
                (JobStatus.PENDING.value,),
            ).fetchone()
        return None if row is None else self._row_to_job(row)

    def claim_next_pending(self, expected_identifier=None):
        """Atomically mark and return the first pending job.

        ``expected_identifier`` lets a resource-aware scheduler inspect the
        next job before claiming it while still detecting a concurrent queue
        change.
        """
        timestamp = _utc_now()
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT identifier FROM optimization_jobs
                WHERE status = ?
                ORDER BY position, created_at
                LIMIT 1
                """,
                (JobStatus.PENDING.value,),
            ).fetchone()
            if row is None:
                return None
            identifier = row["identifier"]
            if (
                expected_identifier is not None
                and identifier != expected_identifier
            ):
                return None
            cursor = connection.execute(
                """
                UPDATE optimization_jobs
                SET status = ?, updated_at = ?, started_at = ?,
                    finished_at = NULL, message = NULL, result_json = NULL,
                    progress_json = NULL
                WHERE identifier = ? AND status = ?
                """,
                (
                    JobStatus.RUNNING.value,
                    timestamp,
                    timestamp,
                    identifier,
                    JobStatus.PENDING.value,
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    f"Optimization job {identifier} was claimed concurrently."
                )
        return self.get(identifier)

    def update_progress(self, identifier, progress):
        """Append a finite progress point while a job is running."""
        if not isinstance(progress, OptimizationProgress):
            raise TypeError("progress must be OptimizationProgress.")
        point = StoredOptimizationProgress(
            evaluations=int(progress.evaluations),
            best_cost=float(progress.best_cost),
            elapsed_seconds=float(progress.elapsed_seconds),
            estimated_remaining_seconds=(
                None
                if progress.estimated_remaining_seconds is None
                else float(progress.estimated_remaining_seconds)
            ),
            best_parameters=tuple(progress.best_parameters),
        )
        serialized_point = _serialize_progress_history((point,))
        # Validate all values before entering the write transaction.
        json.loads(serialized_point)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT status, progress_json FROM optimization_jobs "
                "WHERE identifier = ?",
                (identifier,),
            ).fetchone()
            if row is None:
                raise KeyError(f"Unknown optimization job: {identifier}")
            if JobStatus(row["status"]) is not JobStatus.RUNNING:
                return self.get(identifier)
            history = list(_deserialize_progress_history(row["progress_json"]))
            if not history or (
                history[-1].evaluations != point.evaluations
                or history[-1].best_cost != point.best_cost
            ):
                history.append(point)
            else:
                history[-1] = point
            history = history[-200:]
            connection.execute(
                "UPDATE optimization_jobs SET progress_json = ?, updated_at = ? "
                "WHERE identifier = ? AND status = ?",
                (
                    _serialize_progress_history(history),
                    _utc_now(),
                    identifier,
                    JobStatus.RUNNING.value,
                ),
            )
        return self.get(identifier)

    def complete(self, identifier, outcome):
        """Persist a finite solver result and mark its running job completed."""
        serialized_result = _serialize_result(outcome)
        timestamp = _utc_now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE optimization_jobs
                SET status = ?, updated_at = ?, finished_at = ?,
                    message = ?, result_json = ?
                WHERE identifier = ? AND status = ?
                """,
                (
                    JobStatus.COMPLETED.value,
                    timestamp,
                    timestamp,
                    str(getattr(outcome.result, "message", "")) or None,
                    serialized_result,
                    identifier,
                    JobStatus.RUNNING.value,
                ),
            )
            if cursor.rowcount != 1:
                raise ValueError(
                    f"Only a running job can be completed: {identifier}"
                )
        return self.get(identifier)

    def recover_interrupted_jobs(self):
        """Mark jobs left running by a stopped application as interrupted."""
        timestamp = _utc_now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE optimization_jobs
                SET status = ?, updated_at = ?, finished_at = ?, message = ?
                WHERE status = ?
                """,
                (
                    JobStatus.INTERRUPTED.value,
                    timestamp,
                    timestamp,
                    "The application stopped while this optimization was running.",
                    JobStatus.RUNNING.value,
                ),
            )
            return cursor.rowcount
