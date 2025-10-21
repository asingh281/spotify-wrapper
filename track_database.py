from typing import Callable
import random
import sqlite3

DB_PATH = 'track_weights.db'
MAX_WEIGHT = 1.0

# DATABASE UTILITY FUNCTIONS
def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS track_weights (
                track_id TEXT PRIMARY KEY,
                weight REAL NOT NULL
            )
        ''')
        conn.commit()

def get_weight(track_id: str) -> float:
    with get_connection() as conn:
        cur = conn.execute('SELECT weight FROM track_weights WHERE track_id = ?', (track_id,))
        row = cur.fetchone()
        return max(row[0], 0) if row else 0

def set_weight(track_id: str, weight: float):
    with get_connection() as conn:
        conn.execute('''
            INSERT INTO track_weights (track_id, weight)
            VALUES (?, ?)
            ON CONFLICT(track_id) DO UPDATE SET weight=excluded.weight
        ''', (track_id, weight))
        conn.commit()

# APPLICATION FUNCTIONS
def like_track(track_id: str):
    current_weight = get_weight(track_id)
    new_weight = current_weight + (MAX_WEIGHT - current_weight) / 2
    set_weight(track_id, new_weight)
    return new_weight

def dislike_track(track_id: str):
    current_weight = get_weight(track_id)
    new_weight = current_weight / 2
    set_weight(track_id, new_weight)
    return new_weight
        
def view_tracks(get_track_info: (Callable[[str], str] | None)=None):
    with get_connection() as conn:
        cur = conn.execute('SELECT track_id, weight FROM track_weights')
        for track_id, weight in cur.fetchall():
            info = get_track_info(track_id) if get_track_info else ""
            print(track_id, f'weight={weight:.2f}', info)

def choose_track() -> str:
    with get_connection() as conn:
        cur = conn.execute('SELECT SUM(weight) FROM track_weights')
        sum_weights = cur.fetchone()[0]
        r = random.random() * sum_weights
        print(r)
        cur = conn.execute("""
            SELECT track_id
            FROM (
                SELECT track_id, weight, SUM(weight)
                OVER (ORDER BY track_id) as cumulative_weight
                FROM track_weights
            )
            WHERE cumulative_weight >= ?
            ORDER BY track_id
            LIMIT 1;
        """, (r,))
        track = cur.fetchone()[0]
        print(track)
    return track