
import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "departments.csv"
DB_FILE = BASE_DIR / "database" / "hospital.db"

if not CSV_FILE.exists():
    raise FileNotFoundError(f"CSV file not found: {CSV_FILE}")

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()

try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospital_floor_departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT UNIQUE NOT NULL,
            floor TEXT NOT NULL,
            category TEXT
        )
    """)

    with open(CSV_FILE, "r", encoding="utf-8-sig") as file:
        lines = (line for line in file if line.strip())
        reader = csv.DictReader(lines)

        print("CSV columns found:", reader.fieldnames)

        required = {"floor", "department_name", "category"}
        headers = {
            name.strip().lower(): name
            for name in (reader.fieldnames or [])
        }

        if not required.issubset(headers):
            raise ValueError("CSV header mismatch.")

        imported = 0

        for row in reader:
            department = row[headers["department_name"]].strip()
            floor = row[headers["floor"]].strip()
            category = row[headers["category"]].strip()

            if not department or not floor:
                continue

            cursor.execute("""
                INSERT INTO hospital_floor_departments
                    (department_name, floor, category)
                VALUES (?, ?, ?)
                ON CONFLICT(department_name) DO UPDATE SET
                    floor = excluded.floor,
                    category = excluded.category
            """, (department, floor, category))

            imported += 1

    cursor.execute(
        "SELECT COUNT(*) FROM hospital_floor_departments"
    )
    total = cursor.fetchone()[0]

    connection.commit()
    print(f"Import successful! Rows processed: {imported}")
    print(f"Total entries in database: {total}")

except Exception as error:
    connection.rollback()
    print("Import failed:", error)

finally:
    connection.close()