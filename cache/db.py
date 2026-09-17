import sqlite3
import json
import time
from config import CACHE_DIR

DB_PATH = CACHE_DIR / "cache.db"
TTL = 3600 * 6


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT,
            mode TEXT,
            value TEXT,
            timestamp REAL,
            PRIMARY KEY (key, mode)
        )
    """)
    conn.commit()
    return conn


def get_cached(key: str, mode: str) -> dict | None:
    conn = _get_conn()
    row = conn.execute(
        "SELECT value, timestamp FROM cache WHERE key = ? AND mode = ?",
        (key, mode),
    ).fetchone()
    conn.close()

    if row and (time.time() - row[1]) < TTL:
        return json.loads(row[0])
    return None


def set_cached(key: str, mode: str, value: dict):
    conn = _get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO cache (key, mode, value, timestamp) VALUES (?, ?, ?, ?)",
        (key, mode, json.dumps(value), time.time()),
    )
    conn.commit()
    conn.close()
