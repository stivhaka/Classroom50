import secrets
import string

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from classroom50.db import get_db
from classroom50.views.auth import login_required, teacher_only

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    """Show classrooms and their information."""

    db = get_db()

    # Query classrooms
    classrooms = db.execute(
        "SELECT c.id, c.name, c.description, c.subject"
        "  FROM classrooms AS c"
        "  JOIN members AS m"
        "    ON m.classroom_id = c.id"
        " WHERE m.user_id = ?"
        " ORDER BY c.name",
        (g.user["id"],)
    ).fetchall()

    return render_template("main/index.html", classrooms=classrooms)


@main_bp.route("/create", methods=["GET", "POST"])
@login_required
@teacher_only
def create():
    """Create new classroom."""

    db = get_db()

    if request.method == "POST":

        # Get user input
        name = request.form.get("name")
        description = request.form.get("description")
        subject = request.form.get("subject")

        error = None

        # Validate user input
        if not name or name.isspace():
            error = "Missing classroom name!"

        # If validation succeeds
        if error is None:

            # Generate classroom code
            code = generate_code()

            # Remove leading and trailing whitespace from name, description and subject if any
            name = name.strip()
            description = description.strip()
            subject = subject.strip()

            # Insert the new classroom into the database
            db.execute(
                "INSERT INTO classrooms (owner_id, name, description, subject, code) VALUES(?, ?, ?, ?, ?)",
                (g.user["id"], name, description, subject, code)
            )
            db.commit()

            # Query classroom id
            classroom_id = db.execute(
                "SELECT id FROM classrooms WHERE code = ?", (code,)
            ).fetchone()["id"]

            # Insert owner into members
            db.execute(
                "INSERT INTO members (classroom_id, user_id) VALUES(?, ?)",
                (classroom_id, g.user["id"])
            )
            db.commit()

            flash("Classroom created!", "success")
            return redirect(url_for("main.index"))

        # If validation fails, show the error to the user
        flash(error, "error")
        return redirect(url_for("main.create"))
    else:
        return render_template("main/create.html")


@main_bp.route("/join", methods=["GET", "POST"])
@login_required
def join():
    """Join classroom."""

    db = get_db()

    if request.method == "POST":

        # Get user input
        code = request.form.get("code")

        error = None

        # Query classroom id
        classroom = db.execute(
            "SELECT id FROM classrooms WHERE code = ?", (code,)
        ).fetchone()

        # Validate user input
        if not code or code.isspace():
            error = "Missing classroom code!"
        elif classroom is None:
            error = "Invalid classroom code!"
        else:
            member = db.execute(
                "SELECT 1 FROM members WHERE classroom_id = ? AND user_id = ?",
                (classroom["id"], g.user["id"])
            ).fetchone()

            if member:
                error = "You are already part of this classroom!"

        # If validation succeeds
        if error is None:

            # Add the user to the classroom members
            db.execute(
                "INSERT INTO members (classroom_id, user_id) VALUES(?, ?)",
                (classroom["id"], g.user["id"])
            )
            db.commit()

            flash("Classroom joined!", "success")
            return redirect(url_for("main.index"))

        # If validation fails, show the error to the user
        flash(error, "error")
        return redirect(url_for("main.join"))
    else:
        return render_template("main/join.html")


def generate_code():
    """Generate classroom code."""

    db = get_db()

    while True:

        # Generate a random 8 character alphanumeric code
        alphabet = string.ascii_letters + string.digits
        code = ''.join(secrets.choice(alphabet) for i in range(8))

        # Check if code already exists
        classroom = db.execute(
            "SELECT 1 FROM classrooms WHERE code = ?", (code,)
        ).fetchone()

        if classroom is None:
            break

    return code