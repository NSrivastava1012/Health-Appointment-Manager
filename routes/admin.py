from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash

from extensions import db
from models.user import User
from models.doctor import Doctor
from models.doctor_leave import DoctorLeave


admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# =========================================================
# ADMIN AUTHORIZATION
# =========================================================

def admin_required():

    if "user_id" not in session:
        return False

    if session.get("user_role") != "admin":
        return False

    return True


# =========================================================
# MANAGE DOCTORS
# =========================================================

@admin.route("/doctors")
def doctors():

    if not admin_required():
        return "Access Denied", 403

    doctors = Doctor.query.all()

    return render_template(
        "admin/doctors.html",
        doctors=doctors
    )


# =========================================================
# ADD DOCTOR
# =========================================================

@admin.route("/doctors/add", methods=["GET", "POST"])
def add_doctor():

    if not admin_required():
        return "Access Denied", 403

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        specialization = request.form["specialization"]
        working_start = request.form["working_start"]
        working_end = request.form["working_end"]
        slot_duration = request.form["slot_duration"]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return "Email already registered!"

        # ---------------------------------------------
        # Create doctor login account
        # ---------------------------------------------

        doctor_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role="doctor"
        )

        db.session.add(doctor_user)

        db.session.flush()

        # ---------------------------------------------
        # Create doctor profile
        # ---------------------------------------------

        doctor = Doctor(
            user_id=doctor_user.id,
            specialization=specialization,
            working_start=working_start,
            working_end=working_end,
            slot_duration=int(slot_duration)
        )

        db.session.add(doctor)

        db.session.commit()

        return redirect(
            url_for("admin.doctors")
        )

    return render_template(
        "admin/add_doctor.html"
    )


# =========================================================
# EDIT DOCTOR
# =========================================================

@admin.route(
    "/doctors/<int:doctor_id>/edit",
    methods=["GET", "POST"]
)
def edit_doctor(doctor_id):

    if not admin_required():
        return "Access Denied", 403

    # Get doctor profile
    doctor = Doctor.query.get_or_404(
        doctor_id
    )

    # Get associated user account
    doctor_user = User.query.get_or_404(
        doctor.user_id
    )

    # ---------------------------------------------
    # UPDATE DOCTOR
    # ---------------------------------------------

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        specialization = request.form["specialization"].strip()
        working_start = request.form["working_start"]
        working_end = request.form["working_end"]
        slot_duration = request.form["slot_duration"]

        # -----------------------------------------
        # Check email belongs to another user
        # -----------------------------------------

        existing_user = User.query.filter(
            User.email == email,
            User.id != doctor_user.id
        ).first()

        if existing_user:

            return "Email already registered by another user!"

        # -----------------------------------------
        # Update User information
        # -----------------------------------------

        doctor_user.name = name
        doctor_user.email = email

        # -----------------------------------------
        # Update Doctor information
        # -----------------------------------------

        doctor.specialization = specialization
        doctor.working_start = working_start
        doctor.working_end = working_end
        doctor.slot_duration = int(slot_duration)

        db.session.commit()

        return redirect(
            url_for("admin.doctors")
        )

    # ---------------------------------------------
    # Display Edit Doctor page
    # ---------------------------------------------

    return render_template(
        "admin/edit_doctor.html",
        doctor=doctor,
        doctor_user=doctor_user
    )


# =========================================================
# ADD DOCTOR LEAVE
# =========================================================

@admin.route(
    "/doctors/<int:doctor_id>/leave",
    methods=["GET", "POST"]
)
def add_leave(doctor_id):

    if not admin_required():
        return "Access Denied", 403

    doctor = Doctor.query.get_or_404(
        doctor_id
    )

    if request.method == "POST":

        leave_date = request.form["leave_date"]

        existing_leave = DoctorLeave.query.filter_by(
            doctor_id=doctor_id,
            leave_date=leave_date
        ).first()

        if existing_leave:

            return (
                "Doctor is already marked on leave "
                "for this date."
            )

        leave = DoctorLeave(
            doctor_id=doctor_id,
            leave_date=leave_date
        )

        db.session.add(leave)

        db.session.commit()

        return redirect(
            url_for("admin.doctors")
        )

    return render_template(
        "admin/add_leave.html",
        doctor=doctor
    )