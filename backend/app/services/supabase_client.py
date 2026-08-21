"""Optional Supabase connection used for tracker result persistence.

The API deliberately remains usable without Supabase credentials so the SIH
demo can run locally. Set SUPABASE_URL and the server-only SUPABASE_KEY to
enable writes.
"""

import logging
import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


@lru_cache(maxsize=1)
def get_supabase() -> Any | None:
    """Return a configured supabase-py client, or None in demo mode."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key or "your-project" in url or "your-server" in key:
        return None

    try:
        from supabase import create_client

        return create_client(url, key)
    except Exception:  # pragma: no cover - depends on remote configuration
        logger.exception("Supabase client could not be initialized; using demo mode.")
        return None


def insert_row(table: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    """Insert a row when Supabase is configured; never break calculations on a write failure."""
    client = get_supabase()
    if client is None:
        return None
    try:
        response = client.table(table).insert(payload).execute()
        return response.data[0] if response.data else None
    except Exception:  # pragma: no cover - depends on remote configuration
        logger.exception("Supabase insert into %s failed; continuing without persistence.", table)
        return None
