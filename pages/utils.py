import sqlite3
import pandas as pd
from datetime import datetime
import re

DB = "cliniq.db"

def get_db_connection():
    return sqlite3.connect(DB)

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY,
            name TEXT, phone TEXT, dept TEXT, token TEXT UNIQUE,
            score INTEGER, arrival TEXT, status TEXT DEFAULT 'waiting',
            service_start TEXT, service_end TEXT
            )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY,
            name TEXT, phone TEXT, dept TEXT, slot TEXT UNIQUE,
            booked_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_appt_slot ON appointments (slot);')
    conn.commit()
    conn.close()

# —————————————————————— PHONE VALIDATION ——————————————————————
def validate_phone(phone: str, country: str = "Other") -> bool:
    """
    Validate phone number based on country.
    Returns True if valid.
    """
    # Clean input: remove spaces, dashes, parentheses, +, etc.
    cleaned = re.sub(r"[^\d]", "", phone.strip())

    if country == "India":
        pattern = r"^[6-9]\d{9}$"
        return bool(re.match(pattern, cleaned))
    elif country == "Japan":
        pattern = r"^0\d{9,10}$"
        return bool(re.match(pattern, cleaned))
    else:  # International fallback
        return 7 <= len(cleaned) <= 15 and cleaned.isdigit()

# —————————————————————— DATABASE OPERATIONS ——————————————————————
def add_patient(name, phone, dept, token, score):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO patients (name, phone, dept, token, score, arrival) VALUES (?, ?, ?, ?, ?, ?)",
        (name, phone, dept, token, score, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_queue(dept=None):
    conn = get_db_connection()
    query = "SELECT * FROM patients WHERE status='waiting'"
    if dept:
        query += f" AND dept='{dept}'"
    query += " ORDER BY score DESC, arrival ASC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def call_next(dept):
    conn = get_db_connection()
    df = pd.read_sql_query(
        f"SELECT * FROM patients WHERE dept='{dept}' AND status='waiting' ORDER BY score DESC, arrival ASC LIMIT 1",
        conn
    )
    if not df.empty:
        pid = df.iloc[0]['id']
        conn.execute("UPDATE patients SET status='called', service_start=? WHERE id=?", 
                     (datetime.now().isoformat(), pid))
    conn.commit()
    conn.close()

def book_appointment(name, phone, dept, slot):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE dept=? AND slot=?", (dept, slot))
    if cursor.fetchone():
        conn.close()
        return False
    conn.execute("INSERT INTO appointments (name, phone, dept, slot) VALUES (?, ?, ?, ?)", 
                 (name, phone, dept, slot))
    conn.commit()
    conn.close()
    return True

def get_appointments(dept=None):
    conn = get_db_connection()
    query = "SELECT * FROM appointments"
    if dept:
        query += f" WHERE dept='{dept}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df