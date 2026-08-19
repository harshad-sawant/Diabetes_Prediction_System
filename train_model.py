"""
Train multiple diabetes prediction models on the Pima Indians Diabetes dataset.
Run this script once before starting the Flask app to generate diabetes_model.pkl.
"""

import os
import pickle

import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "diabetes.csv")
MODEL_PATH = os.path.join(BASE_DIR, "diabetes_model.pkl")

# Feature columns used for prediction (matches the web form)
FEATURE_COLUMNS = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
]


def load_and_prepare_data():
    """Load CSV and replace invalid zero values in medical readings with column medians."""
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()

    zero_cols = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
    for col in zero_cols:
        median_val = df[col].replace(0, pd.NA).median()
        df[col] = df[col].replace(0, median_val)

    X = df[FEATURE_COLUMNS]
    y = df["Outcome"]
    return X, y


def train_and_save_model():
    """Train four models, print accuracy for each, and save them to disk."""
    X, y = load_and_prepare_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model_specs = {
        "Linear Regression": LinearRegression(),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
        "Support Vector Classifier": SVC(kernel="rbf", probability=True, random_state=42),
    }

    model_results = {}
    for name, model in model_specs.items():
        model.fit(X_train_scaled, y_train)
        if name == "Linear Regression":
            y_pred = (model.predict(X_test_scaled) >= 0.5).astype(int)
        else:
            y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        model_results[name] = {
            "model": model,
            "accuracy": round(accuracy * 100, 2),
        }
        print(f"{name}: {accuracy * 100:.2f}%")

    artifact = {
        "feature_columns": FEATURE_COLUMNS,
        "scaler": scaler,
        "models": model_results,
    }

    with open(MODEL_PATH, "wb") as file:
        pickle.dump(artifact, file)

    print(f"Model artifact saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_and_save_model()
