import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'solstice.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def seed_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(SCHEMA_PATH, 'r') as f:
        cursor.executescript(f.read())
        
    attendees = [
        ('QR-ALICE-101', 'Alice Smith', 'alice@example.com', 'VIP', 'UNREGISTERED'),
        ('QR-BOB-202', 'Bob Jones', 'bob@example.com', 'General', 'CHECKED_IN'),
        ('QR-CHARLIE-303', 'Charlie Brown', 'charlie@example.com', 'Speaker', 'UNREGISTERED')
    ]
    
    cursor.executemany(
        '''
        INSERT INTO attendees (qr_code, full_name, email, ticket_type, status)
        VALUES (?, ?, ?, ?, ?)
        ''', attendees
    )
    
    conn.commit()
    conn.close()
    print("Database seeded successfully with test attendees.")

if __name__ == "__main__":
    seed_db()
