"""
Diabetes Prediction System - Flask Web Application
Predicts diabetes risk using multiple machine learning models.
Stores prediction history in MySQL and provides dashboard analytics with PDF reports.
"""

import math
import os
import pickle
from io import BytesIO

import pandas as pd
from flask import Flask, flash, redirect, render_template, request, send_file, url_for

import database as db
from pdf_report import generate_prediction_pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "diabetes_model.pkl")

app = Flask(__name__)
app.secret_key = "diabetes-prediction-secret-key"

model_artifact = None
MODEL_OPTIONS = []
MODEL_ACCURACIES = {}
DEFAULT_MODEL = "Logistic Regression"
MODEL_ACCURACY = "N/A"


def _rebuild_model_artifact():
    """Recreate the model artifact if the stored pickle is invalid or stale."""
    import train_model

    train_model.MODEL_PATH = MODEL_PATH
    train_model.train_and_save_model()
    with open(MODEL_PATH, "rb") as file:
        return pickle.load(file)


def load_model():
    """Load the pickled model artifact from disk and rebuild it if needed."""
    global model_artifact, MODEL_OPTIONS, MODEL_ACCURACIES, DEFAULT_MODEL, MODEL_ACCURACY

    try:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Model file not found. Please run train_model.py first.")

        with open(MODEL_PATH, "rb") as file:
            model_artifact = pickle.load(file)

        if not isinstance(model_artifact, dict) or "models" not in model_artifact:
            raise ValueError("Model artifact is missing required data.")

        for name, entry in model_artifact["models"].items():
            if not isinstance(entry, dict) or "model" not in entry:
                raise ValueError(f"Model entry '{name}' is malformed.")

            model = entry["model"]
            if not hasattr(model, "predict"):
                raise ValueError(f"Model '{name}' is invalid: missing predict().")

            if name != "Linear Regression" and not hasattr(model, "predict_proba"):
                raise ValueError(f"Model '{name}' is invalid: missing predict_proba().")

    except Exception:
        model_artifact = _rebuild_model_artifact()

    MODEL_OPTIONS = list(model_artifact["models"].keys())
    MODEL_ACCURACIES = {
        name: round(model_artifact["models"][name]["accuracy"], 2)
        for name in MODEL_OPTIONS
    }

    if DEFAULT_MODEL not in MODEL_OPTIONS:
        DEFAULT_MODEL = MODEL_OPTIONS[0]

    MODEL_ACCURACY = MODEL_ACCURACIES.get(DEFAULT_MODEL, "N/A")


# Validation rules: (min, max, label)
FIELD_RULES = {
    "pregnancies": (0, 20, "Pregnancies"),
    "glucose": (1, 300, "Glucose"),
    "blood_pressure": (1, 180, "Blood Pressure"),
    "skin_thickness": (1, 100, "Skin Thickness"),
    "insulin": (1, 900, "Insulin"),
    "bmi": (1, 70, "BMI"),
    "diabetes_pedigree": (0.0, 3.0, "Diabetes Pedigree Function"),
    "age": (1, 120, "Age"),
}


def validate_form(data):
    """Validate patient input and return (errors, cleaned_values, patient_name)."""
    errors = []
    cleaned = {}

    patient_name = data.get("patient_name", "").strip()
    if not patient_name:
        errors.append("Patient name is required.")
    elif len(patient_name) > 100:
        errors.append("Patient name must be 100 characters or fewer.")

    sex = data.get("sex", "").strip()
    if not sex:
        errors.append("Sex is required.")
    elif sex not in {"Male", "Female", "Other"}:
        errors.append("Please select a valid sex option.")
    else:
        cleaned["sex"] = sex

    for field, (min_val, max_val, label) in FIELD_RULES.items():
        raw_value = data.get(field, "").strip()

        if not raw_value:
            errors.append(f"{label} is required.")
            continue

        try:
            value = float(raw_value)
            if field in ("pregnancies", "age"):
                value = int(value)
        except ValueError:
            errors.append(f"{label} must be a valid number.")
            continue

        if value < min_val or value > max_val:
            errors.append(f"{label} must be between {min_val} and {max_val}.")

        cleaned[field] = value

    return errors, cleaned, patient_name


def predict_diabetes(patient_data, model_name=None):
    """Run prediction and return (is_diabetic, probability, accuracy)."""
    selected_model = model_name or DEFAULT_MODEL
    model_entry = model_artifact["models"].get(selected_model)
    if not model_entry:
        raise ValueError(f"Unknown model: {selected_model}")

    feature_columns = model_artifact["feature_columns"]

    input_df = pd.DataFrame(
        [
            {
                "Pregnancies": patient_data["pregnancies"],
                "Glucose": patient_data["glucose"],
                "BloodPressure": patient_data["blood_pressure"],
                "SkinThickness": patient_data["skin_thickness"],
                "Insulin": patient_data["insulin"],
                "BMI": patient_data["bmi"],
                "DiabetesPedigreeFunction": patient_data["diabetes_pedigree"],
                "Age": patient_data["age"],
            }
        ]
    )

    scaled_input = model_artifact["scaler"].transform(input_df[feature_columns])
    model = model_entry["model"]

    if selected_model == "Linear Regression":
        raw_score = model.predict(scaled_input)[0]
        probability = 1 / (1 + math.exp(-raw_score))
        prediction = 1 if raw_score >= 0.5 else 0
    else:
        probability = model.predict_proba(scaled_input)[0][1]
        prediction = model.predict(scaled_input)[0]

    is_diabetic = bool(prediction)
    return is_diabetic, round(probability * 100, 2), round(model_entry["accuracy"], 2)


@app.route("/")
def index():
    """Home page with patient details form."""
    return render_template(
        "index.html",
        accuracy=MODEL_ACCURACY,
        model_options=MODEL_OPTIONS,
        model_accuracies=MODEL_ACCURACIES,
        selected_model=DEFAULT_MODEL,
    )


@app.route("/predict", methods=["POST"])
def predict():
    """Handle form submission, save to DB, and show prediction result."""
    errors, patient_data, patient_name = validate_form(request.form)

    if errors:
        for error in errors:
            flash(error, "danger")
        return redirect(url_for("index"))

    selected_model = request.form.get("model_name", DEFAULT_MODEL).strip()
    is_diabetic, probability, selected_accuracy = predict_diabetes(patient_data, selected_model)
    result_label = "Positive" if is_diabetic else "Negative"
    result_text = "The patient is Diabetic" if is_diabetic else "The patient is Not Diabetic"

    prediction_id = db.save_prediction(
        patient_name,
        patient_data,
        result_label,
        probability,
        selected_model,
    )

    return render_template(
        "result.html",
        result=result_text,
        is_diabetic=is_diabetic,
        probability=probability,
        patient_data=patient_data,
        patient_name=patient_name,
        prediction_id=prediction_id,
        selected_model=selected_model,
        model_accuracy=selected_accuracy,
        accuracy=selected_accuracy,
        model_options=MODEL_OPTIONS,
        model_accuracies=MODEL_ACCURACIES,
    )


@app.route("/dashboard")
def dashboard():
    """Analytics dashboard with stats and charts."""
    stats = db.get_dashboard_stats()
    chart_data = db.get_chart_data()
    return render_template(
        "dashboard.html",
        stats=stats,
        chart_data=chart_data,
        accuracy=MODEL_ACCURACY,
        model_options=MODEL_OPTIONS,
        model_accuracies=MODEL_ACCURACIES,
        selected_model=DEFAULT_MODEL,
    )


@app.route("/history")
def history():
    """Prediction history table."""
    predictions = db.get_all_predictions()
    return render_template(
        "history.html",
        predictions=predictions,
        accuracy=MODEL_ACCURACY,
        model_options=MODEL_OPTIONS,
        model_accuracies=MODEL_ACCURACIES,
        selected_model=DEFAULT_MODEL,
    )


@app.route("/report/<int:prediction_id>")
def download_report(prediction_id):
    """Generate and download PDF report for a prediction."""
    record = db.get_prediction_by_id(prediction_id)
    if not record:
        flash("Report not found.", "danger")
        return redirect(url_for("history"))

    model_name = record.get("model_name", DEFAULT_MODEL)
    model_accuracy = MODEL_ACCURACIES.get(model_name, MODEL_ACCURACY)
    pdf_bytes = generate_prediction_pdf(record, model_name, model_accuracy)
    safe_name = record["patient_name"].replace(" ", "_")
    filename = f"Diabetes_Report_{safe_name}_{prediction_id}.pdf"

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@app.route("/about")
def about():
    """About page with project information."""
    return render_template(
        "about.html",
        accuracy=MODEL_ACCURACY,
        model_options=MODEL_OPTIONS,
        model_accuracies=MODEL_ACCURACIES,
        selected_model=DEFAULT_MODEL,
    )


@app.route("/about-diabetes")
def about_diabetes():
    """Educational page about diabetes."""
    return render_template(
        "about_diabetes.html",
        accuracy=MODEL_ACCURACY,
        model_options=MODEL_OPTIONS,
        model_accuracies=MODEL_ACCURACIES,
        selected_model=DEFAULT_MODEL,
    )


# Initialize database and model when the app starts
db.init_db()
load_model()

if __name__ == "__main__":
    app.run(debug=True)
