from typing import Callable
import sqlite3

DB_PATH = 'track_weights.db'
MAX_WEIGHT = 40.0

# DATABASE UTILITY FUNCTIONS
def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS track_weights (
                track_id TEXT PRIMARY KEY,
                weight REAL NOT NULL,
                last_decay TIMESTAMP NOT NULL
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
            INSERT INTO track_weights (track_id, weight, last_decay)
            VALUES (?, ?, current_date)
            ON CONFLICT(track_id) DO UPDATE SET weight=excluded.weight
        ''', (track_id, weight))
        conn.commit()

# TRACK WEIGHT FUNCTIONS
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

def decay_weights():
    with get_connection() as conn:
        conn.execute('''
            UPDATE track_weights
            SET weight = weight - (julianday(current_date) - julianday(last_decay)), last_decay = current_date
        ''')
        conn.commit()
        
def view_tracks(get_track_info: Callable[[str], str]):
    with get_connection() as conn:
        cur = conn.execute('SELECT track_id, weight, last_decay FROM track_weights')
        for track_id, weight, last_decay in cur.fetchall():
            try:
                info = get_track_info(track_id)
            except Exception as e:
                info = f'(error fetching info: {e})'
            print(track_id, f'weight={weight:.2f}', last_decay, info)