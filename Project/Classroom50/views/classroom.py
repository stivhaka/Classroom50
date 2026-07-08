import re

from flask import Blueprint, flash, g, redirect, request, session, url_for

from classroom50.db import get_db
from classroom50.views import assignments, home, manage, members
from classroom50.views.auth import login_required

classroom_bp = Blueprint("classroom", __name__, url_prefix="/classroom/<int:classroom_id>")

classroom_bp.register_blueprint(assignments.assignments_bp)
classroom_bp.register_blueprint(home.home_bp)
classroom_bp.register_blueprint(manage.manage_bp)
classroom_bp.register_blueprint(members.members_bp)


@classroom_bp.before_request
@login_required
def load_classroom():
    """Check if user is allowed to access classroom and load owner id if allowed."""

    db = get_db()

    # Get classroom id from URL
    classroom_id = re.findall("\d+", request.path)[0]

    # Check if user is a member
    member = db.execute(
        "SELECT 1 FROM members WHERE classroom_id = ? AND user_id = ? ",
        (classroom_id, session["user_id"])
    ).fetchone()

    # If user is a member
    if member:

        # Load owner id into g
        owner_id = db.execute(
            "SELECT owner_id FROM classrooms WHERE id = ?", (classroom_id,)
        ).fetchone()["owner_id"]
        g.classroom_owner_id = owner_id

    # If user is not a member or classroom does not exist
    else:
        flash("Classroom not found!", "error")
        return redirect(url_for("main.index"))