import os
import sqlite3
from datetime import datetime, timedelta

DB_FILENAME = "akuntansi.db"


def init_db_if_needed():
    need_init = not os.path.exists(DB_FILENAME)
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()

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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS akun (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            no_akun TEXT UNIQUE NOT NULL,
            nama_akun TEXT NOT NULL,
            tipe TEXT NOT NULL
        )
    """)

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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS adjusting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            akun_debit TEXT NOT NULL,
            akun_kredit TEXT NOT NULL,
            debit REAL DEFAULT 0,
            kredit REAL DEFAULT 0,
            keterangan TEXT
        )
    """)

    conn.commit()
    conn.close()
    return need_init


def get_conn():
    if not os.path.exists(DB_FILENAME):
        init_db_if_needed()
    return sqlite3.connect(DB_FILENAME)
from .db_users import (
    user_exists,
    register_user_with_otp,
    verify_activation_otp,
    verify_password_and_active,
)
