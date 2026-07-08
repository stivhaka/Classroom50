from flask import Blueprint, flash, g, redirect, render_template, url_for

from classroom50.views.auth import login_required, owner_only
from classroom50.db import get_db

members_bp = Blueprint("members", __name__)


@members_bp.route("/members")
@login_required
def members(classroom_id):
    """Show classroom members."""

    db = get_db()

    # Query owner
    owner = db.execute(
        "SELECT u.name"
        "  FROM users AS u"
        "  JOIN classrooms AS c"
        "    ON c.owner_id = u.id"
        " WHERE c.id = ?",
        (classroom_id,)
    ).fetchone()

    # Query teachers
    teachers = db.execute(
        "SELECT u.id, u.name"
        "  FROM users AS u"
        "  JOIN members AS m"
        "    ON m.user_id = u.id"
        " WHERE m.classroom_id = ?"
        "   AND u.role = 'teacher'"
        "   AND NOT u.id = ?"
        " ORDER BY u.name",
        (classroom_id, g.classroom_owner_id)
    ).fetchall()

    # Query students
    students = db.execute(
        "SELECT u.id, u.name"
        "  FROM users AS u"
        "  JOIN members AS m"
        "    ON m.user_id = u.id"
        " WHERE m.classroom_id = ?"
        "   AND u.role = 'student'"
        " ORDER BY u.name",
        (classroom_id,)
    ).fetchall()

    return render_template("classroom/members.html", classroom_id=classroom_id, owner=owner, students=students, teachers=teachers)


@members_bp.route("/remove-user/<int:user_id>", methods=["POST"])
@login_required
@owner_only
def remove(classroom_id, user_id):
    """Remove user from classroom."""

    db = get_db()
    error = None

    # Check if user is a member
    member = db.execute(
        "SELECT 1 FROM members WHERE classroom_id = ? AND user_id = ? ",
        (classroom_id, user_id)
    ).fetchone()

    # Validate user input
    if member is None:
        error = "User not found!"
    elif user_id == g.classroom_owner_id:
        error = "You cannot remove yourself!"

    # If validation succeeds
    if error is None:

        # Remove user from classroom
        db.execute(
            "DELETE FROM members WHERE classroom_id = ? AND user_id = ?",
            (classroom_id, user_id)
        )
        db.commit()

        flash("User removed!", "success")

    # If validation fails
    else:

        # Show the error to the user
        flash(error, "error")

    return redirect(url_for("classroom.members.members", classroom_id=classroom_id))