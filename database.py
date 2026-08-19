"""
MySQL database module for storing prediction history.
"""

import os
from datetime import datetime

import mysql.connector

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.environ.get("DB_NAME", "diabetes_prediction_db")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

DB_PORT = int(os.environ.get("DB_PORT", "3306"))


def get_connection(use_database=True):
    """Return a MySQL database connection."""
    config = {
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "port": DB_PORT,
        "autocommit": True,
    }
    if use_database:
        config["database"] = DB_NAME

    conn = mysql.connector.connect(**config)
    return conn


def init_db():
    """Create the database and predictions table if they do not exist."""
    root_conn = get_connection(use_database=False)
    cursor = root_conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.close()
    root_conn.close()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_name VARCHAR(100) NOT NULL,
            pregnancies INT NOT NULL,
            glucose DOUBLE NOT NULL,
            blood_pressure DOUBLE NOT NULL,
            skin_thickness DOUBLE NOT NULL,
            insulin DOUBLE NOT NULL,
            bmi DOUBLE NOT NULL,
            diabetes_pedigree DOUBLE NOT NULL,
            age INT NOT NULL,
            sex VARCHAR(20) NOT NULL DEFAULT 'Unknown',
            result VARCHAR(20) NOT NULL,
            probability DOUBLE NOT NULL,
            model_name VARCHAR(50) NOT NULL,
            created_at DATETIME NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )

    migrations = [
        ("sex", "VARCHAR(20) NOT NULL DEFAULT 'Unknown'"),
        ("model_name", "VARCHAR(50) NOT NULL DEFAULT 'Unknown'"),
        ("created_at", "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"),
    ]

    for column_name, definition in migrations:
        cursor.execute("SHOW COLUMNS FROM predictions LIKE %s", (column_name,))
        if cursor.fetchone() is None:
            cursor.execute(f"ALTER TABLE predictions ADD COLUMN {column_name} {definition}")

    cursor.close()
    conn.close()


def save_prediction(patient_name, patient_data, result, probability, model_name):
    """Save a prediction record and return the new record ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO predictions (
            patient_name, pregnancies, glucose, blood_pressure,
            skin_thickness, insulin, bmi, diabetes_pedigree, age, sex,
            result, probability, model_name, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            patient_name.strip(),
            int(patient_data["pregnancies"]),
            float(patient_data["glucose"]),
            float(patient_data["blood_pressure"]),
            float(patient_data["skin_thickness"]),
            float(patient_data["insulin"]),
            float(patient_data["bmi"]),
            float(patient_data["diabetes_pedigree"]),
            int(patient_data["age"]),
            patient_data.get("sex", "Unknown"),
            result,
            float(probability),
            model_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    prediction_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return prediction_id


def get_prediction_by_id(prediction_id):
    """Fetch a single prediction by ID."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM predictions WHERE id = %s", (prediction_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_all_predictions():
    """Return all predictions ordered by newest first."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM predictions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_dashboard_stats():
    """Return total, positive, and negative prediction counts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE result = 'Positive'")
    positive = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE result = 'Negative'")
    negative = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return {"total": total, "positive": positive, "negative": negative}


def get_chart_data():
    """Return data for dashboard charts."""
    predictions = get_all_predictions()

    bmi_labels = ["Underweight (<18.5)", "Normal (18.5-24.9)", "Overweight (25-29.9)", "Obese (30+)"]
    bmi_counts = [0, 0, 0, 0]

    glucose_labels = ["Normal (<100)", "Prediabetes (100-125)", "High (126-180)", "Very High (>180)"]
    glucose_counts = [0, 0, 0, 0]

    for record in predictions:
        bmi = record["bmi"]
        if bmi < 18.5:
            bmi_counts[0] += 1
        elif bmi < 25:
            bmi_counts[1] += 1
        elif bmi < 30:
            bmi_counts[2] += 1
        else:
            bmi_counts[3] += 1

        glucose = record["glucose"]
        if glucose < 100:
            glucose_counts[0] += 1
        elif glucose <= 125:
            glucose_counts[1] += 1
        elif glucose <= 180:
            glucose_counts[2] += 1
        else:
            glucose_counts[3] += 1

    stats = get_dashboard_stats()

    return {
        "bmi_labels": bmi_labels,
        "bmi_counts": bmi_counts,
        "glucose_labels": glucose_labels,
        "glucose_counts": glucose_counts,
        "result_labels": ["Diabetic (Positive)", "Non-Diabetic (Negative)"],
        "result_counts": [stats["positive"], stats["negative"]],
    }
