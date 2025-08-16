import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate_csrf():
    token_form = request.form.get("csrf_token")
    token_sess = session.get("csrf_token")
    return token_form and token_sess and token_form == token_sess

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not validate_csrf():
            flash("Invalid or missing CSRF token.", "danger")
            return redirect(url_for("auth.register"))

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not username or not email or not password:
            flash("All fields are required.", "warning")
            return render_template("register.html")
        if not EMAIL_RE.match(email):
            flash("Please enter a valid email address.", "warning")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "warning")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "warning")
            return render_template("register.html")
        if User.query.filter_by(username=username).first():
            flash("Username is already taken.", "danger")
            return render_template("register.html")
        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return render_template("register.html")

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not validate_csrf():
            flash("Invalid or missing CSRF token.", "danger")
            return redirect(url_for("auth.login"))

        username_or_email = request.form.get("username_or_email", "").strip().lower()
        password = request.form.get("password", "")

        user = (
            User.query.filter((User.email == username_or_email) | (User.username == username_or_email)).first()
        )

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("dashboard"))
        else:
            flash("Invalid credentials.", "danger")

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))
