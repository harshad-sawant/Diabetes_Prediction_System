"""
PDF report generator for diabetes prediction results.
"""

import os
from io import BytesIO

from fpdf import FPDF

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class PredictionReport(FPDF):
    """Custom PDF document for prediction reports."""

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(13, 110, 253)
        self.cell(0, 10, "Diabetes Prediction System - Patient Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_prediction_pdf(record, model_name, model_accuracy):
    """Generate a PDF report for a prediction record and return bytes."""
    pdf = PredictionReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 8, "Patient Information", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 11)
    info_rows = [
        ("Patient Name", record["patient_name"]),
        ("Sex", record.get("sex", "Unknown")),
        ("Report Date & Time", record["created_at"]),
        ("Report ID", f"#{record['id']}"),
    ]
    for label, value in info_rows:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 7, f"{label}:")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Prediction Result", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    is_positive = record["result"] == "Positive"
    if is_positive:
        pdf.set_text_color(220, 53, 69)
        result_text = "The patient is DIABETIC (Positive)"
    else:
        pdf.set_text_color(25, 135, 84)
        result_text = "The patient is NOT DIABETIC (Negative)"

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, result_text, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(31, 41, 55)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"Confidence: {record['probability']}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Selected Model: {model_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Model Accuracy: {model_accuracy}%", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Health Metrics", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    metrics = [
        ("Pregnancies", record["pregnancies"]),
        ("Glucose (mg/dL)", record["glucose"]),
        ("Blood Pressure (mm Hg)", record["blood_pressure"]),
        ("Skin Thickness (mm)", record["skin_thickness"]),
        ("Insulin (mu U/ml)", record["insulin"]),
        ("BMI", record["bmi"]),
        ("Diabetes Pedigree Function", record["diabetes_pedigree"]),
        ("Age (years)", record["age"]),
    ]

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(232, 241, 255)
    pdf.cell(90, 8, "Parameter", border=1, fill=True)
    pdf.cell(90, 8, "Value", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    for label, value in metrics:
        pdf.cell(90, 8, label, border=1)
        pdf.cell(90, 8, str(value), border=1, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)

    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
