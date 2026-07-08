import re
import os
import shutil

from flask import Blueprint, current_app, flash, redirect, render_template, url_for

from classroom50.db import get_db
from classroom50.views.auth import login_required, owner_only
from classroom50.views.main import generate_code

manage_bp = Blueprint("manage", __name__, url_prefix="/manage")


@manage_bp.route("/settings")
@login_required
@owner_only
def settings(classroom_id):
    """Show classroom settings."""

    # Query classroom code
    code = get_db().execute(
        "SELECT code FROM classrooms WHERE id = ?", (classroom_id,)
    ).fetchone()["code"]

    return render_template("classroom/settings.html", classroom_id=classroom_id, code=code)


@manage_bp.route("/reset-code", methods=["POST"])
@login_required
@owner_only
def reset_code(classroom_id):
    """Reset classroom code."""

    db = get_db()

    # Generate new code
    code = generate_code()

    # Update code
    db.execute(
        "UPDATE classrooms SET code = ? WHERE id = ?",
        (code, classroom_id)
    )
    db.commit()

    return redirect(url_for("classroom.manage.settings", classroom_id=classroom_id))


@manage_bp.route("/delete-classroom", methods=["POST"])
@login_required
@owner_only
def delete_classroom(classroom_id):
    """Delete classroom and all of it's data."""

    db = get_db()

    # Delete posts and comments
    db.execute(
        "DELETE FROM comments WHERE classroom_id = ?", (classroom_id,)
    )
    db.commit()

    db.execute(
        "DELETE FROM posts WHERE classroom_id = ?", (classroom_id,)
    )
    db.commit()

    # Delete assignments and submissions
    db.execute(
        "DELETE FROM assignments WHERE classroom_id = ?", (classroom_id,)
    )
    db.commit()

    db.execute(
        "DELETE FROM submissions WHERE classroom_id = ?", (classroom_id,)
    )
    db.commit()

    # Delete classroom files
    if os.path.exists(os.path.join(current_app.config["UPLOAD_FOLDER"], "classroom" + str(classroom_id) + "/")):
        shutil.rmtree(os.path.join(current_app.config["UPLOAD_FOLDER"], "classroom" + str(classroom_id) + "/"))

    # Delete members
    db.execute(
        "DELETE FROM members WHERE classroom_id = ?", (classroom_id,)
    )
    db.commit()

    # Delete classroom
    db.execute(
        "DELETE FROM classrooms WHERE id = ?", (classroom_id,)
    )
    db.commit()

    flash("Classroom deleted!", "success")
    return redirect(url_for("main.index"))