# Diabetes Prediction System

A login-free web application that predicts whether a patient is diabetic using **Logistic Regression** machine learning. Includes prediction history, analytics dashboard, charts, and PDF report generation.

## Features

- Login-free web application with Bootstrap UI and icons
- Patient name on every prediction and report
- SQL database stores prediction history (name, date/time, positive/negative)
- Analytics dashboard with total, positive, and negative case counts
- Interactive charts: BMI distribution, Glucose distribution, Diabetes vs Non-diabetes
- PDF report download with full patient details
- About Diabetes page (symptoms, causes, prevention, precautions)
- Input validation and model accuracy display

## Technologies

| Category | Tools |
|----------|-------|
| Backend | Python, Flask, SQLite |
| Frontend | HTML5, Bootstrap 5, Bootstrap Icons, Chart.js |
| ML / Data | Pandas, NumPy, Scikit-learn, Pickle |
| Reports | FPDF2 (PDF generation) |

## Project Structure

```
Diabetes_Prediction_System/
├── app.py                 # Flask web application
├── database.py            # SQL prediction storage
├── pdf_report.py          # PDF report generator
├── train_model.py         # Model training script
├── diabetes.csv           # Pima Indians Diabetes dataset
├── diabetes_model.pkl     # Trained model (generated)
├── predictions.db         # Prediction history (auto-created)
├── requirements.txt
├── templates/
│   ├── base.html          # Bootstrap layout
│   ├── index.html         # Patient form (with name)
│   ├── result.html        # Prediction result + PDF download
│   ├── dashboard.html     # Stats and charts
│   ├── history.html       # Prediction history table
│   ├── about.html         # About project
│   └── about_diabetes.html
├── static/
│   ├── style.css
│   └── logo.png
└── README.md
```

## Setup Instructions

### 1. Create virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Train the model

```bash
python train_model.py
```

### 4. Run the application

```bash
python app.py
```

Open your browser at: **http://127.0.0.1:5000**

## Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Patient name + health details form |
| Result | `/predict` | Prediction outcome + PDF download |
| Dashboard | `/dashboard` | Stats and charts |
| History | `/history` | All past predictions |
| About Diabetes | `/about-diabetes` | Health information |
| About Project | `/about` | Project details |

## Disclaimer

This project is for **educational and demonstration purposes only**. It is not a substitute for professional medical advice, diagnosis, or treatment.

## Author

Internship Project — 2026
