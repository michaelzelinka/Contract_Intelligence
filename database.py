import os
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid


def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS extractions (
                    id UUID PRIMARY KEY,
                    filename TEXT,
                    result JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS api_keys (
                    key TEXT PRIMARY KEY,
                    name TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
        conn.commit()


def save_extraction(filename: str, result: dict) -> str:
    extraction_id = str(uuid.uuid4())
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO extractions (id, filename, result) VALUES (%s, %s, %s)",
                (extraction_id, filename, psycopg2.extras.Json(result))
            )
        conn.commit()
    return extraction_id


def get_extraction(extraction_id: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, filename, result, created_at FROM extractions WHERE id = %s",
                (extraction_id,)
            )
            row = cur.fetchone()
    if not row:
        return None
    return {
        "id": str(row["id"]),
        "filename": row["filename"],
        "result": row["result"],
        "created_at": row["created_at"].isoformat(),
    }


def is_valid_api_key(key: str) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM api_keys WHERE key = %s", (key,))
            return cur.fetchone() is not None
