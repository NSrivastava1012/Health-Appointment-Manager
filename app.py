from flask import Flask, render_template, session, redirect, url_for

from config import Config
from extensions import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Import models
from models.user import User
from models.doctor import Doctor
from models.appointment import Appointment
from models.symptom import Symptom
from models.prescription import Prescription
from models.notification import Notification
from models.doctor_leave import DoctorLeave
from models.ai_summary import AISummary

# Import routes
from routes.auth import auth
from routes.admin import admin
from routes.appointments import appointments


app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(appointments)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/patient/dashboard")
def patient_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "patient":
        return "Access Denied"

    return render_template(
        "patient_dashboard.html",
        name=session.get("user_name")
    )


@app.route("/doctor/dashboard")
def doctor_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "doctor":
        return "Access Denied"

    return render_template(
        "doctor_dashboard.html",
        name=session.get("user_name")
    )


@app.route("/admin/dashboard")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Access Denied"

    return render_template(
        "admin_dashboard.html",
        name=session.get("user_name")
    )


if __name__ == "__main__":
    app.run(debug=True)