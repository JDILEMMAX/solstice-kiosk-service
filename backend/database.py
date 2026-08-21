import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'solstice.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_attendee_by_qr(qr_code: str) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendees WHERE qr_code = ?", (qr_code,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_attendee_status(qr_code: str, status: str, print_job_id: str = None) -> None:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    cursor.execute(
        "UPDATE attendees SET status = ?, print_job_id = ?, checked_in_at = ? WHERE qr_code = ?",
        (status, print_job_id, now, qr_code)
    )
    conn.commit()
    conn.close()

def get_all_attendees() -> list:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendees")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
