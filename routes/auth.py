from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models.user import User

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered!"

        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["user_role"] = user.role
            session["user_name"] = user.name

            if user.role == "patient":
                return redirect(url_for("patient_dashboard"))

            elif user.role == "doctor":
                return redirect(url_for("doctor_dashboard"))

            elif user.role == "admin":
                return redirect(url_for("admin_dashboard"))

        return "Invalid email or password"

    return render_template("login.html")


@auth.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))