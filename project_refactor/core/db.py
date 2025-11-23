import sqlite3
import os
import time

# Import konfigurasi DB
from core.config import DB_FILENAME, DB_RETRY_BACKOFF, DB_MAX_RETRIES


class DBHelper:
    def __init__(self, filename=DB_FILENAME):
        self.filename = filename
        # Ensure DB file exists + schema
        self.init_db_if_needed()

    def connect(self):
        # each operation creates its own connection; superior for multi-threading
        return sqlite3.connect(self.filename, timeout=30, check_same_thread=False)

    def _retry_execute(self, func, *args, **kwargs):
        backoff = DB_RETRY_BACKOFF
        for attempt in range(1, DB_MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempt < DB_MAX_RETRIES:
                    time.sleep(backoff)
                    backoff *= 1.8
                    continue
                raise

    def init_db_if_needed(self):
        need_init = not os.path.exists(self.filename)

        with self.connect() as conn:
            cur = conn.cursor()

            # users
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active INTEGER DEFAULT 0,
                    otp TEXT,
                    otp_expiry TEXT
                )
            """)

            # akun
            cur.execute("""
                CREATE TABLE IF NOT EXISTS akun (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    no_akun TEXT UNIQUE NOT NULL,
                    nama_akun TEXT NOT NULL,
                    tipe TEXT NOT NULL,
                    starting_balance REAL DEFAULT 0
                )
            """)

            # jurnal
            cur.execute("""
                CREATE TABLE IF NOT EXISTS jurnal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT NOT NULL,
                    akun_debit TEXT NOT NULL,
                    akun_kredit TEXT NOT NULL,
                    debit REAL DEFAULT 0,
                    kredit REAL DEFAULT 0,
                    keterangan TEXT
                )
            """)

            # adjusting
            cur.execute("""
                CREATE TABLE IF NOT EXISTS adjusting (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT NOT NULL,
                    akun_debit TEXT NOT NULL,
                    akun_kredit TEXT NOT NULL,
                    debit REAL DEFAULT 0,
                    kredit REAL DEFAULT 0,
                    keterangan TEXT,
                    applied INTEGER DEFAULT 0
                )
            """)

            conn.commit()

        return need_init

    # Generic helpers
    def execute(self, sql, params=(), commit=False):
        def _do():
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute(sql, params)
                if commit:
                    conn.commit()
                return cur

        return self._retry_execute(_do)

    def fetchall(self, sql, params=()):
        def _do():
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute(sql, params)
                return cur.fetchall()

        return self._retry_execute(_do)

    def fetchone(self, sql, params=()):
        def _do():
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute(sql, params)
                return cur.fetchone()

        return self._retry_execute(_do)


# Global DB instance
_db = DBHelper(DB_FILENAME)


def get_db():
    return _db
