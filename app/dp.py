import sqlite3, os
from .config import *

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

def connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    con = connect()
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            redeemed_count INTEGER DEFAULT 0,
            premium_until INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS keys (
            key TEXT PRIMARY KEY,
            days INTEGER,
            used_by INTEGER DEFAULT NULL
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        INSERT OR IGNORE INTO settings(key, value) VALUES ('free_unlimited', '0');
    """)
    con.commit()
    con.close()

def get_setting(key):
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT value FROM settings WHERE key=?", (key,))
    val = cur.fetchone()
    con.close()
    return val[0] if val else None

def set_setting(key, value):
    con = connect()
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO settings(key, value) VALUES(?, ?)", (key, value))
    con.commit()
    con.close()
