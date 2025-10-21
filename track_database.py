from typing import Callable
import os
import random
import sqlite3

class TrackDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        if not os.path.exists(db_path):
            self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS track_weights (
                    track_id TEXT PRIMARY KEY,
                    weight REAL NOT NULL
                )
            ''')
            conn.commit()

    def get_weight(self, track_id: str) -> float:
        with self.get_connection() as conn:
            cur = conn.execute('SELECT weight FROM track_weights WHERE track_id = ?', (track_id,))
            row = cur.fetchone()
            return max(row[0], 0) if row else 0

    def set_weight(self, track_id: str, weight: float):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO track_weights (track_id, weight)
                VALUES (?, ?)
                ON CONFLICT(track_id) DO UPDATE SET weight=excluded.weight
            ''', (track_id, weight))
            conn.commit()
        
    def get_tracks(self, get_track_info: (Callable[[str], str] | None)=None):
        tracks = []
        with self.get_connection() as conn:
            cur = conn.execute('SELECT track_id, weight FROM track_weights')
            for track_id, weight in cur.fetchall():
                info = get_track_info(track_id) if get_track_info else ""
                tracks.append((track_id, weight, info))
        return tracks

    def get_random_track(self) -> str:
        with self.get_connection() as conn:
            cur = conn.execute('SELECT SUM(weight) FROM track_weights')
            sum_weights = cur.fetchone()[0]
            r = random.random() * sum_weights
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
            return cur.fetchone()[0]