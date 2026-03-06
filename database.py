import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "clinic.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()
    conn.close()


# ── Patients ──────────────────────────────────────────────────────────────────

def search_patients(query: str):
    conn = get_connection()
    cursor = conn.cursor()
    like = f"%{query}%"
    cursor.execute(
        "SELECT id, name, iden_type, iden_info, phone_number FROM patients "
        "WHERE name LIKE ? OR iden_info LIKE ? OR phone_number LIKE ?",
        (like, like, like),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_patient(name, citizen, iden_type, iden_info, birthdate, gender, married, phone_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO patients (name, citizen, iden_type, iden_info, birthdate, gender, married, phone_number) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (name, citizen, iden_type, iden_info, birthdate, gender, married, phone_number),
    )
    conn.commit()
    patient_id = cursor.lastrowid
    conn.close()
    return patient_id


# ── Liquid Medicine ───────────────────────────────────────────────────────────

def get_all_liquid_medicines():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM liquid_medicine ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_liquid_medicine(name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO liquid_medicine (name) VALUES (?)", (name,))
    conn.commit()
    medicine_id = cursor.lastrowid
    conn.close()
    return medicine_id
