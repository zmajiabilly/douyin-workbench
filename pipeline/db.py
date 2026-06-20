# 抖音工作台 — 数据管理（SQLite）
import sqlite3, time, json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "database.db"

def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    _init(conn)
    return conn

def _init(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT UNIQUE,
            url TEXT,
            title TEXT,
            author TEXT,
            like_count INTEGER DEFAULT 0,
            video_path TEXT,
            audio_path TEXT,
            screenshot_path TEXT,
            transcript TEXT,
            summary TEXT,
            tags TEXT,
            status TEXT DEFAULT 'parsed',
            created_at INTEGER,
            updated_at INTEGER
        )
    """)
    conn.commit()

def add_item(video_id, url, title="", author="", like_count=0):
    conn = get_db()
    now = int(time.time())
    conn.execute("""
        INSERT OR IGNORE INTO items 
        (video_id, url, title, author, like_count, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (video_id, url, title, author, like_count, now, now))
    conn.commit()
    row = conn.execute("SELECT * FROM items WHERE video_id=?", (video_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_item(video_id, **kw):
    conn = get_db()
    sets = ", ".join(f"{k}=?" for k in kw)
    vals = list(kw.values()) + [int(time.time())]
    conn.execute(f"UPDATE items SET {sets}, updated_at=? WHERE video_id=?", (*vals, video_id))
    conn.commit()
    conn.close()

def get_item(item_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_items(limit=50, offset=0):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM items ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_item(item_id):
    conn = get_db()
    conn.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
