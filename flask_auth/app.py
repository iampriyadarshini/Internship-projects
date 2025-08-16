import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# ---------------------- App Factory ----------------------
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # SECRET_KEY should be set via environment for production
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-change-me"),
        DATABASE=os.path.join(app.instance_path, "database.db")
    )

    if test_config is not None:
        app.config.update(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # ----------- DB Helpers -----------
    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(
                app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_db(e=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    app.teardown_appcontext(close_db)

    def init_db():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        db.commit()

    @app.cli.command("init-db")
    def init_db_command():
        """Initialize the database tables."""
        init_db()
        print("Initialized the database.")

    # Initialize database if missing
    with app.app_context():
        init_db()

    # --------- Auth Utilities ---------
    def login_required(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
            return view(**kwargs)
        return wrapped_view

    # ------------------- Routes -------------------
    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("home"))
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            confirm = request.form.get("confirm_password") or ""

            # Basic validations
            if not username or not password:
                flash("Username and password are required.", "danger")
                return render_template("register.html")
            if len(username) < 3:
                flash("Username must be at least 3 characters.", "danger")
                return render_template("register.html")
            if password != confirm:
                flash("Passwords do not match.", "danger")
                return render_template("register.html")
            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return render_template("register.html")

            hashed = generate_password_hash(password)
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed),
                )
                db.commit()
            except sqlite3.IntegrityError:
                flash("Username already exists. Choose another.", "danger")
                return render_template("register.html")

            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""

            db = get_db()
            user = db.execute(
                "SELECT id, username, password FROM users WHERE username = ?",
                (username,)
            ).fetchone()

            if user is None or not check_password_hash(user["password"], password):
                flash("Invalid username or password.", "danger")
                return render_template("login.html")

            # Success
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("home"))

        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @app.route("/home")
    @login_required
    def home():
        return render_template("home.html", username=session.get("username"))

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
