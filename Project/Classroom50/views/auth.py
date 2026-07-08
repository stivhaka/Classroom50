import re

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

from classroom50.db import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    if request.method == "POST":

        # Get user input
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        role = request.form.get("role")

        db = get_db()
        error = None

        # Validate user input
        if not name or name.isspace():
            error = "Missing name!"
        elif not re.search("^(?!.*\s).{4,}$", username):
            error = "Missing or invalid username!"
        elif not re.search("^(?=.*[A-Za-z])(?=.*\d)(?=.*\W)(?!.*\s).{8,}$", password):
            error = "Missing or invalid password!"
        elif password != confirmation:
            error = "Passwords do not match!"
        elif not role in ["student", "teacher"]:
            error = "Missing or invalid role!"

        # If validation succeeds
        if error is None:
            try:

                # Remove leading and trailing whitespace from full name if any
                name = name.strip()

                # Insert the new user into the database
                db.execute(
                    "INSERT INTO users (name, username, password, role) VALUES(?, ?, ?, ?)",
                    (name, username, generate_password_hash(password), role)
                )
                db.commit()

            # If the username already exists, show an error to the user
            except db.IntegrityError:
                error = f"Username {username} is taken!"

            # If the user was successfully registered
            else:

                # Redirect the user to the login page
                flash("You have registered for Classroom50!", "success")
                return redirect(url_for("auth.login"))

        # If validation fails, show the error to the user
        flash(error, "error")
        return redirect(url_for("auth.register"))
    else:
        return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # Forget any user
    [session.pop(key) for key in list(session.keys()) if key != "_flashes"]

    if request.method == "POST":

        # Get user input
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        error = None

        # Query user
        user = db.execute(
            "SELECT id, password FROM users WHERE username = ?", (username,)
        ).fetchone()

        # Validate user input
        if user is None:
            error = "Incorrect username!"
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password!"

        # If validation succeeds
        if error is None:

            # Remember user and redirect to the index page
            session["user_id"] = user["id"]
            return redirect(url_for("main.index"))

        # If validation fails, show the error to the user
        flash(error, "error")
        return redirect(url_for("auth.login"))
    else:
        return render_template("auth/login.html")


@auth_bp.before_app_request
def load_logged_in_user():
    """Load a user before every subsequent request."""

    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()


@auth_bp.route("/logout")
def logout():
    """Log user out."""

    session.clear()
    return redirect(url_for("auth.login"))


def login_required(f):
    """Check if a user is loaded."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def teacher_only(f):
    """Check if user is a teacher."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user["role"] == "student":
            flash("You are not allowed to access this page!", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated_function


def student_only(f):
    """Check if user is a student."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user["role"] == "teacher":
            classroom_id = re.findall("\d+", request.path)[0]
            flash("You are not allowed to access this page!", "error")
            return redirect(url_for("classroom.assignments.assignments", classroom_id=classroom_id))
        return f(*args, **kwargs)
    return decorated_function


def owner_only(f):
    """Check if user is the owner of the classroom."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user["id"] != g.classroom_owner_id:
            classroom_id = re.findall("\d+", request.path)[0]
            flash("You are not allowed to access this page!", "error")
            return redirect(url_for("classroom.home.home", classroom_id=classroom_id))
        return f(*args, **kwargs)
    return decorated_function