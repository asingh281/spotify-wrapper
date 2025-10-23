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
                CREATE TABLE IF NOT EXISTS tracks (
                    id TEXT PRIMARY KEY,
                    weight REAL NOT NULL,
                    info TEXT
                )
            ''')
            conn.commit()

    def get_weight(self, track_id: str) -> float:
        with self.get_connection() as conn:
            cur = conn.execute('SELECT weight FROM tracks WHERE id = ?', (track_id,))
            row = cur.fetchone()
            return max(row[0], 0) if row else 0

    def set_weight(self, track_id: str, weight: float):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO tracks (id, weight)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET weight=excluded.weight
            ''', (track_id, weight))
            conn.commit()
        
    def get_tracks(self) -> list[tuple[str, float, str]]:
        tracks = []
        with self.get_connection() as conn:
            cur = conn.execute('SELECT id, weight, info FROM tracks')
            for id, weight, info in cur.fetchall():
                tracks.append((id, weight, info))
        return tracks

    def get_random_track(self) -> str:
        with self.get_connection() as conn:
            cur = conn.execute('SELECT SUM(weight) FROM tracks')
            sum_weights = cur.fetchone()[0]
            r = random.random() * sum_weights
            cur = conn.execute("""
                SELECT id
                FROM (
                    SELECT id, weight, SUM(weight)
                    OVER (ORDER BY id) as cumulative_weight
                    FROM tracks
                )
                WHERE cumulative_weight >= ?
                ORDER BY id
                LIMIT 1;
            """, (r,))
            return cur.fetchone()[0]