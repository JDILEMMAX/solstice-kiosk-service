CREATE TABLE attendees (
    id INTEGER PRIMARY KEY,
    qr_code TEXT UNIQUE,
    full_name TEXT,
    email TEXT,
    ticket_type TEXT,
    status TEXT DEFAULT 'UNREGISTERED',
    print_job_id TEXT,
    checked_in_at TIMESTAMP
);

CREATE TABLE print_jobs (
    id TEXT PRIMARY KEY,
    qr_code TEXT,
    status TEXT,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
