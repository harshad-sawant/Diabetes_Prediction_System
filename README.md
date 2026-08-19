Diabetes Prediction System

A web-based Diabetes Prediction System developed using Python and Flask. The application uses multiple Machine Learning classification models to predict whether a patient is likely to have diabetes based on health-related information.

The system also provides prediction history, an analytics dashboard, interactive charts, model accuracy information, and downloadable PDF reports.

Features

- Login-free web application
- Patient name and sex input
- Health parameter-based diabetes prediction
- Multiple Machine Learning models
- Model selection from the web interface
- Model accuracy display
- Prediction probability/confidence
- Prediction result display
- MySQL database for prediction history
- Prediction history page
- Analytics dashboard
- Total, positive, and negative prediction statistics
- BMI distribution chart
- Glucose distribution chart
- Diabetes vs. non-diabetes chart
- PDF prediction report generation
- Patient details included in PDF reports
- About Diabetes educational page
- About Project page
- Input validation
- Automatic database and table creation

Technologies Used

Category| Technologies
Backend| Python, Flask
Frontend| HTML5, CSS3, Bootstrap 5, Bootstrap Icons
Machine Learning| Scikit-learn
Data Processing| Pandas, NumPy
Database| MySQL
Charts| Chart.js
PDF Reports| FPDF2
Model Storage| Pickle

Machine Learning

The project uses the Pima Indians Diabetes Dataset for training.

Four Machine Learning models are trained:

1. Linear Regression
2. Logistic Regression
3. K-Nearest Neighbors (KNN)
4. Support Vector Classifier (SVC)

The default model used by the application is Logistic Regression.

Before training, invalid zero values in medical measurements such as Glucose, Blood Pressure, Skin Thickness, Insulin, and BMI are replaced with the corresponding column median.

The trained models, scaler, feature columns, and accuracy values are stored together in:

diabetes_model.pkl

The model can be trained again using:

python train_model.py

The training script uses an 80/20 train-test split with stratification and StandardScaler preprocessing.

Input Parameters

The prediction system uses the following health parameters:

Parameter| Description
Pregnancies| Number of pregnancies
Glucose| Plasma glucose concentration
Blood Pressure| Diastolic blood pressure
Skin Thickness| Triceps skin fold thickness
Insulin| 2-Hour serum insulin
BMI| Body Mass Index
Diabetes Pedigree Function| Diabetes hereditary risk score
Age| Patient age
Sex| Patient sex

The patient's name and sex are also stored with each prediction record.

Project Structure

Diabetes_Prediction_System/
│
├── app.py
├── database.py
├── pdf_report.py
├── train_model.py
├── diabetes.csv
├── diabetes_model.pkl
├── predictions.db
├── requirements.txt
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── dashboard.html
│   ├── history.html
│   ├── about.html
│   └── about_diabetes.html
│
└── static/
    ├── style.css
    └── logo.png

«Note: "predictions.db" is present in the local project folder from previous development, but the current application uses MySQL for storing prediction history. The README therefore documents MySQL as the database used by the application.»

Database

The application uses MySQL to store prediction history.

When the Flask application starts, it automatically:

- Connects to MySQL
- Creates the database if it does not exist
- Creates the "predictions" table if it does not exist
- Adds required columns when necessary

The prediction records contain:

- Patient name
- Sex
- Health parameters
- Prediction result
- Prediction probability
- Selected Machine Learning model
- Prediction date and time

Default MySQL Configuration

The application reads database settings from environment variables:

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=20102004
DB_PORT=3306
DB_NAME=diabetes_prediction_db

For security, it is recommended to configure the database password using environment variables rather than storing credentials directly in source code.

Setup Instructions

1. Clone the Repository

git clone <your-github-repository-url>
cd Diabetes_Prediction_System

2. Create a Virtual Environment

python -m venv venv

3. Activate the Virtual Environment

For Windows:

venv\Scripts\activate

For macOS/Linux:

source venv/bin/activate

4. Install Dependencies

pip install -r requirements.txt

5. Configure MySQL

Make sure MySQL Server is installed and running.

Create/configure a MySQL user that the application can use.

The application will automatically create the database:

diabetes_prediction_db

You can also configure the connection using environment variables.

6. Train the Machine Learning Models

python train_model.py

This creates/updates:

diabetes_model.pkl

The training script prints the accuracy of each trained model in the terminal.

7. Run the Flask Application

python app.py

Open the application in your browser:

http://127.0.0.1:5000

Application Pages

Page| URL| Description
Home| "/"| Patient information and prediction form
Result| "/predict"| Prediction result and PDF report option
Dashboard| "/dashboard"| Statistics and interactive charts
History| "/history"| Previous prediction records
PDF Report| "/report/<id>"| Generates a PDF report for a prediction
About Diabetes| "/about-diabetes"| Educational information about diabetes
About Project| "/about"| Project information

Dashboard

The analytics dashboard provides:

- Total predictions
- Positive predictions
- Negative predictions
- BMI distribution
- Glucose distribution
- Diabetes vs. non-diabetes comparison

The charts are generated using Chart.js.

PDF Reports

After a prediction is generated, the application stores the result in MySQL and provides an option to generate a PDF report.

The report includes:

- Patient name
- Sex
- Report date and time
- Report ID
- Prediction result
- Prediction confidence/probability
- Selected Machine Learning model
- Model accuracy
- Patient health parameters

Input Validation

The application validates the submitted patient information before making a prediction.

Validation includes:

- Required patient name
- Valid sex selection
- Numeric health parameters
- Acceptable ranges for medical input values
- Required form fields

Invalid inputs are rejected and an appropriate error message is displayed to the user.

Requirements

The main Python dependencies are:

Flask
Pandas
NumPy
Scikit-learn
FPDF2
Gunicorn
MySQL Connector/Python

They can be installed using:

pip install -r requirements.txt

Disclaimer

This project is developed for educational and internship demonstration purposes only.

The prediction generated by this application is not a medical diagnosis and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Users should consult a qualified healthcare professional for medical decisions.

Author

Harshad Sawant

Internship Project — 2026
