import re

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from classroom50.views.auth import login_required
from classroom50.db import get_db

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Show user data and allow user to change their password."""

    if request.method == "POST":

        # Get user input
        password = request.form.get("password")

        db = get_db()
        error = None

        # Query old password
        old_password = db.execute(
            "SELECT password FROM users WHERE id = ?", (g.user["id"],)
        ).fetchone()["password"]

        # Validate user input
        if not re.search("^(?=.*[A-Za-z])(?=.*\d)(?=.*\W)(?!.*\s).{8,}$", password):
            error = "Invalid password!"
        elif check_password_hash(old_password, password):
            error = "New password can't be the same as the old one!"

        # If validation succeeds
        if error is None:

            # Update password
            db.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (generate_password_hash(password), g.user["id"])
            )
            db.commit()

            flash("Your password has been changed!", "success")

        # If validation fails
        else:

            # Show the error to the user
            flash(error, "error")

        return redirect(url_for("profile.profile"))
    else:
        return render_template("profile/profile.html")