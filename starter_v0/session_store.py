from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any


_SECRET_PATTERN = re.compile(
    r"\b(?:password|passwd|token|api[ _-]?key|mfa|otp|recovery[ _-]?code)"
    r"(?:\s*[:=]\s*|\s+(?:is|la|là)\s+)\S+",
    re.IGNORECASE,
)


class PostgresSessionStore:
    """Persist sanitized chat messages in PostgreSQL, partitioned by user and session."""

    def __init__(self, dsn: str | None = None) -> None:
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("Install PostgreSQL support first: pip install 'psycopg[binary]'") from exc

        self._psycopg = psycopg
        dsn_value = dsn or os.getenv("DATABASE_URL")
        if not dsn_value:
            raise RuntimeError("Set DATABASE_URL to a PostgreSQL connection string before starting chat.")
        if "change-me" in dsn_value.casefold():
            raise RuntimeError("Replace the placeholder DATABASE_URL credentials before starting chat.")
        try:
            self._connection = psycopg.connect(dsn_value)
        except (psycopg.OperationalError, psycopg.ProgrammingError) as exc:
            raise RuntimeError(
                "Invalid or unusable DATABASE_URL. Check its format, database existence, "
                "role/password, and pg_hba.conf authentication rules."
            ) from exc
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS helpdesk_sessions (
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    provider TEXT,
                    model TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (user_id, session_id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS helpdesk_messages (
                    id BIGSERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    FOREIGN KEY (user_id, session_id)
                        REFERENCES helpdesk_sessions (user_id, session_id)
                        ON DELETE CASCADE
                )
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS helpdesk_messages_session_idx "
                "ON helpdesk_messages (user_id, session_id, id)"
            )
        self._connection.commit()

    def start_session(self, user_id: str, session_id: str, *, provider: str, model: str | None) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO helpdesk_sessions (user_id, session_id, provider, model)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, session_id) DO UPDATE SET
                    provider = EXCLUDED.provider,
                    model = EXCLUDED.model,
                    updated_at = NOW()
                """,
                (user_id, session_id, provider, model),
            )
        self._connection.commit()

    def load_messages(self, user_id: str, session_id: str) -> list[dict[str, str]]:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT role, content
                FROM helpdesk_messages
                WHERE user_id = %s AND session_id = %s
                ORDER BY id
                """,
                (user_id, session_id),
            )
            return [{"role": role, "content": content} for role, content in cursor.fetchall()]

    def list_sessions(self, user_id: str) -> list[dict[str, Any]]:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT session_id, provider, model, created_at, updated_at
                FROM helpdesk_sessions
                WHERE user_id = %s
                ORDER BY updated_at DESC
                """,
                (user_id,),
            )
            return [
                {
                    "session_id": session_id,
                    "provider": provider,
                    "model": model,
                    "created_at": created_at.isoformat(),
                    "updated_at": updated_at.isoformat(),
                }
                for session_id, provider, model, created_at, updated_at in cursor.fetchall()
            ]

    def append_message(self, user_id: str, session_id: str, role: str, content: str) -> None:
        if role not in {"user", "assistant"}:
            raise ValueError(f"Unsupported persisted message role: {role}")
        sanitized = _SECRET_PATTERN.sub("[REDACTED]", content or "")
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO helpdesk_messages (user_id, session_id, role, content)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, session_id, role, sanitized),
            )
            cursor.execute(
                """
                UPDATE helpdesk_sessions
                SET updated_at = %s
                WHERE user_id = %s AND session_id = %s
                """,
                (datetime.now(timezone.utc), user_id, session_id),
            )
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "PostgresSessionStore":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
