# backend/db.py
"""
Postgres helpers for real-time intents:
- get_user_latest_zone
- get_locations_by_category
- get_security_locations
- get_recent_scan_count (for crowd estimation)
- get_reader_coords
"""

import psycopg2
import psycopg2.extras
from typing import List, Dict, Tuple, Optional
from config import PG_DSN, DEBUG

def _get_conn():
    if not PG_DSN:
        raise RuntimeError("PG_DSN not set in environment (.env).")
    return psycopg2.connect(PG_DSN)

def get_user_latest_zone(user_uid: str) -> Optional[int]:
    """
    Return the last_seen_zone for a user if present in users table,
    otherwise look up latest rfid_activity for that user.
    """
    q1 = "SELECT last_seen_zone FROM users WHERE user_uid = %s"
    q2 = "SELECT zone FROM rfid_activity WHERE user_uid = %s ORDER BY created_at DESC LIMIT 1"

    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(q1, (user_uid,))
            r = cur.fetchone()
            if r and r[0] is not None:
                return r[0]

            # fallback to rfid_activity
            cur.execute(q2, (user_uid,))
            r2 = cur.fetchone()
            if r2:
                return r2[0]
    finally:
        conn.close()
    return None

def get_locations_by_category(category: str) -> List[Dict]:
    """
    Returns locations rows matching category. Columns: id,name,category,latitude,longitude
    """
    query = "SELECT id, name, category, latitude, longitude FROM locations WHERE category = %s"
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(query, (category,))
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()

def get_security_locations() -> List[Dict]:
    return get_locations_by_category("security")

def get_recent_scan_count(zone: int, minutes: int = 5) -> int:
    """
    Count scans in a zone in last 'minutes' minutes — used for crowd check.
    """
    # Use string formatting for INTERVAL since it's a SQL keyword, not a parameter
    query = f"SELECT COUNT(*) FROM rfid_activity WHERE zone = %s AND created_at >= now() - INTERVAL '{minutes} minutes'"
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, (zone,))
            cnt = cur.fetchone()[0]
            return int(cnt)
    finally:
        conn.close()

def get_reader_coords(reader_id: int) -> Optional[Tuple[float, float]]:
    """
    Return (x,y) coordinates for a reader_id if available in rfid_readers.
    """
    q = "SELECT x, y FROM rfid_readers WHERE id = %s"
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(q, (reader_id,))
            r = cur.fetchone()
            if r:
                return (float(r[0]), float(r[1]))
    finally:
        conn.close()
    return None

def get_zone_center(zone: int) -> Optional[Tuple[float, float]]:
    """
    Get the center coordinates (x, y) of a zone based on its RFID readers.
    Returns the coordinates of the first reader in the zone as a proxy.
    """
    q = "SELECT x, y FROM rfid_readers WHERE zone = %s LIMIT 1"
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(q, (zone,))
            r = cur.fetchone()
            if r:
                return (float(r[0]), float(r[1]))
    finally:
        conn.close()
    return None
