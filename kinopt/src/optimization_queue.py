"""Persistent local storage for sequential optimization jobs."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
import sqlite3
from typing import List, Optional
from uuid import uuid4

from kinopt.src.optimization_runner import OptimizationRunConfig
from kinopt.src.optimization_serialization import (
    deserialize_config,
    serialize_config,
)


DATABASE_SCHEMA_VERSION = 1


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


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


class OptimizationQueue:
    """Store optimization jobs in one SQLite database."""

    def __init__(self, database_path):
        self.database_path = Path(database_path).expanduser().resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self):
        with self._connect() as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, DATABASE_SCHEMA_VERSION):
                raise ValueError(
                    f"Unsupported optimization queue schema: {version}"
                )
            connection.execute("PRAGMA journal_mode = WAL")
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
                    message TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS optimization_jobs_position
                ON optimization_jobs(position)
                """
            )
            if version == 0:
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
        )

    def add(self, config, name=None):
        """Append an immutable configuration to the queue."""
        serialized = serialize_config(config)
        identifier = str(uuid4())
        timestamp = _utc_now()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COALESCE(MAX(position), 0) + 1 FROM optimization_jobs"
            ).fetchone()
            position = int(row[0])
            job_name = str(name).strip() if name is not None else ""
            if not job_name:
                job_name = f"Optimization {position:03d}"
            connection.execute(
                """
                INSERT INTO optimization_jobs (
                    identifier, name, config_json, status, position,
                    created_at, updated_at, message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
                """,
                (
                    identifier,
                    job_name,
                    serialized,
                    JobStatus.PENDING.value,
                    position,
                    timestamp,
                    timestamp,
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

    def set_status(self, identifier, status, message=None):
        """Apply one valid lifecycle transition and persist its message."""
        requested_status = JobStatus(status)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT status FROM optimization_jobs WHERE identifier = ?",
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
            cursor = connection.execute(
                """
                UPDATE optimization_jobs
                SET status = ?, updated_at = ?, message = ?
                WHERE identifier = ? AND status = ?
                """,
                (
                    requested_status.value,
                    _utc_now(),
                    None if message is None else str(message),
                    identifier,
                    current_status.value,
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    f"Optimization job {identifier} changed concurrently."
                )
        return self.get(identifier)

    def recover_interrupted_jobs(self):
        """Mark jobs left running by a stopped application as interrupted."""
        timestamp = _utc_now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE optimization_jobs
                SET status = ?, updated_at = ?, message = ?
                WHERE status = ?
                """,
                (
                    JobStatus.INTERRUPTED.value,
                    timestamp,
                    "The application stopped while this optimization was running.",
                    JobStatus.RUNNING.value,
                ),
            )
            return cursor.rowcount
