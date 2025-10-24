import os
import random
import sqlite3
import ast
from spotify_utils import Track

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
                    name TEXT NOT NULL,
                    artists TEXT NOT NULL
                )
            ''')
            conn.commit()
        
    def num_tracks(self):
        with self.get_connection() as conn:
            cur = conn.execute('SELECT COUNT(*) FROM tracks')
            return cur.fetchone()[0]

    def get_weight(self, track_id: str) -> float | None:
        with self.get_connection() as conn:
            cur = conn.execute('SELECT weight FROM tracks WHERE id = ?', (track_id,))
            row = cur.fetchone()
            if row:
                return max(row[0], 0)
            else:
                return None
    
    def add_track(self, track: Track, weight: float = 0, ):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO tracks (id, weight, name, artists)
                VALUES (?, ?, ?, ?)
            ''', (track.id, weight, track.name, str(track.artists)))
            conn.commit()

    def set_weight(self, track_id: str, weight: float):
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE tracks
                SET weight = ?
                WHERE id = ?
            ''', (weight, track_id))
            conn.commit()
        
    def get_tracks(self) -> list[tuple[Track, float]]:
        tracks = []
        with self.get_connection() as conn:
            cur = conn.execute('SELECT id, weight, name, artists FROM tracks')
            for id, weight, name, artists in cur.fetchall():
                t = Track(id, name, ast.literal_eval(artists))
                tracks.append((t, weight))
        return tracks

    def get_random_track(self) -> Track:
        with self.get_connection() as conn:
            cur = conn.execute('SELECT SUM(weight) FROM tracks')
            sum_weights = cur.fetchone()[0]
            r = random.random() * sum_weights
            cur = conn.execute("""
                SELECT id, name, artists
                FROM (
                    SELECT id, name, artists, weight, SUM(weight)
                    OVER (ORDER BY id) as cumulative_weight
                    FROM tracks
                )
                WHERE cumulative_weight >= ?
                ORDER BY id
                LIMIT 1;
            """, (r,))
            row = cur.fetchone()
            id = row[0]
            name = row[1]
            artists = ast.literal_eval(row[2])
            return Track(id, name, artists)
    
    def fill_db(self, tracks: list[Track], MAX_WEIGHT: float):
        increment = MAX_WEIGHT / len(tracks)
        for i, track in enumerate(tracks):
            self.add_track(track, MAX_WEIGHT - increment * i)