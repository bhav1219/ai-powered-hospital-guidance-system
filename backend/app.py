
import os
import re
import sqlite3
import fitz

from flask import Flask, send_from_directory, request, jsonify
from werkzeug.utils import secure_filename
from utils.gemini import ask_gemini

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

FRONTEND_FOLDER = os.path.join(BASE_DIR, "frontend")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATABASE_PATH = os.path.join(
    BACKEND_DIR, "database", "hospital.db"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- DATABASE HELPERS ----------------

def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def get_hospital_departments():
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT department_name, floor, category
            FROM hospital_floor_departments
            ORDER BY CAST(floor AS INTEGER), department_name
        """).fetchall()
    finally:
        conn.close()


def find_department_location(department_name):
    """Return only floor data stored in the verified CSV table."""

    aliases = {
        "general internal medicine": "GENERAL MEDICINE",
        "general medicine": "GENERAL MEDICINE",
        "internal medicine": "GENERAL MEDICINE",
        "cardiology": "CARDIOLOGY",
        "pulmonology": "PULMONOLOGY",
        "neurology": "NEUROSCIENCES",
        "neurosciences": "NEUROSCIENCES",
        "pediatrics": "PAEDIATRICS & NEONATOLOGY",
        "paediatrics": "PAEDIATRICS & NEONATOLOGY",
        "emergency department": "URGENT CARE",
        "emergency medicine": "URGENT CARE",
    }

    requested = department_name.strip().casefold()
    canonical = aliases.get(requested, department_name.strip()).upper()

    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT department_name, floor, category
            FROM hospital_floor_departments
            WHERE UPPER(department_name) = ?
            LIMIT 1
        """, (canonical,)).fetchone()
        return row
    finally:
        conn.close()


def add_location_to_answer(answer):
    """Append a floor only if the recommended department can be matched."""

    if not answer:
        return answer

    match = re.search(
        r"Recommended Department:\s*(.+)",
        answer,
        re.IGNORECASE
    )

    if not match:
        return answer

    recommended = match.group(1).strip().splitlines()[0]
    recommended = recommended.strip(" -*`")

    location = find_department_location(recommended)

    if not location:
        return (
            answer.strip()
            + "\n\nHospital Location:\n"
              "The exact department location is not available "
              "in the current hospital floor-plan data."
        )

    department, floor, category = location

    return (
        answer.strip()
        + "\n\nHospital Location:\n"
        + f"Department: {department}\n"
        + f"Floor: {floor} (Floor {floor})\n"
        + "Specific block or room: Not available in the current floor-plan data."
    )


def department_context():
    rows = get_hospital_departments()
    return "\n".join(
        f"- {name} | Floor {floor} | {category}"
        for name, floor, category in rows
    )


# ---------------- HOME & FRONTEND ----------------

@app.route("/")
def home():
    return send_from_directory(FRONTEND_FOLDER, "index.html")


@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_FOLDER, filename)


# ---------------- HOSPITAL CHAT ----------------

@app.route("/hospital-chat", methods=["POST"])
def hospital_chat():
    try:
        data = request.get_json(silent=True) or {}
        question = data.get("question", "").strip()

        if not question:
            return jsonify({
                "answer": "Hi! 😊 What would you like to know about the hospital?"
            })

        departments = department_context()

        prompt = f"""
You are MedGuide AI, a friendly and helpful hospital information assistant
for GKNM Integrated Out-Patient Centre (iOP).

The user asks:
{question}

Verified hospital information:
{departments}

Conversation rules:
1. Respond naturally to the user's actual question.
2. Greet the user warmly when they greet you.
3. Answer general questions in clear, simple language.
4. If asked what a medical department does, briefly explain its general purpose.
5. If asked where a department is, use ONLY the verified floor information above.
6. If asked what departments are available, list departments from the data.
7. Never invent room numbers, blocks, doctors, timings, fees or facilities.
8. If the exact location is not listed, say that the exact location is not available.
9. Do not diagnose diseases or prescribe medicines.
10. For symptom or health concerns, provide general guidance and advise appropriate
    professional medical evaluation. For severe or potentially urgent symptoms,
    advise immediate emergency medical care.
11. Do not force a department name into unrelated answers.
12. If the question is unrelated to the hospital, politely explain that you mainly
    help with hospital information.
13. Keep the answer relevant and conversational.

Answer the user's question directly.
"""

        answer = ask_gemini(prompt)

        if not answer:
            answer = "Sorry, I couldn't generate an answer right now."

        return jsonify({"answer": answer.strip()})

    except Exception as e:
        print("Hospital chat error:", str(e))
        return jsonify({
            "answer": "Sorry, the hospital assistant is temporarily unavailable."
        }), 500


# ---------------- REPORT UPLOAD & ANALYSIS ----------------

@app.route("/upload-report", methods=["POST"])
def upload_report():
    report = request.files.get("report")

    if not report or not report.filename:
        return "Please select a PDF report."

    filename = secure_filename(report.filename)

    if not filename.lower().endswith(".pdf"):
        return "Please upload a PDF file."

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        report.save(file_path)

        with fitz.open(file_path) as document:
            report_text = "\n".join(
                page.get_text() for page in document
            ).strip()

        if not report_text:
            return (
                "Could not extract text from this PDF. "
                "Please use a text-based PDF report."
            )

        departments = department_context()

        prompt = f"""
You are MedGuide AI, a hospital guidance assistant.

Review the following report only to suggest an appropriate department.
Do not diagnose the patient or prescribe treatment.

Available hospital departments and floors:
{departments}

Report text:
{report_text[:12000]}

Choose ONE relevant medical department from the available hospital data.
Use the department's exact name as listed above.
If the report does not provide enough information, say so rather than guessing.

Return this format:
Recommended Department: <exact department name or Unable to determine>
Reason: <one short sentence>

AI provides recommendations only; doctors make the final diagnosis.
"""

        result = ask_gemini(prompt)

        if not result:
            return "Sorry, report analysis did not return a result."

        return add_location_to_answer(result)

    except Exception as e:
        print("Report analysis error:", str(e))
        return "Sorry, the report could not be analyzed right now."


# ---------------- SYMPTOM ANALYSIS ----------------

@app.route("/analyze-symptoms", methods=["POST"])
def analyze_symptoms():
    symptoms = request.form.get("symptoms", "").strip()

    if not symptoms:
        return "Please enter your symptoms."

    departments = department_context()

    prompt = f"""
You are MedGuide AI, a hospital guidance assistant.

User's symptoms:
{symptoms}

Available hospital departments:
{departments}

Choose ONE relevant medical department from the available data.
Use its exact name as listed.
Do not invent departments or locations.
Do not diagnose a disease or prescribe treatment.
If there is not enough information, say that the user should seek
professional medical evaluation.

Return exactly:
Recommended Department: <exact department name or Unable to determine>
Reason: <one short sentence>

AI provides recommendations only; doctors make the final diagnosis.
If symptoms suggest a possible emergency, advise immediate emergency care.
"""

    try:
        result = ask_gemini(prompt)

        if not result:
            return "Sorry, symptom analysis did not return a result."

        return add_location_to_answer(result)

    except Exception as e:
        print("Symptom analysis error:", str(e))
        return "Sorry, symptom analysis is temporarily unavailable."


# ---------------- STARTUP ----------------

def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department TEXT NOT NULL,
                floor TEXT NOT NULL,
                location TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


init_db()


if __name__ == "__main__":
    app.run(debug=True)