from datetime import datetime, timedelta, timezone
import os
import shutil

from flask import Blueprint, current_app, flash, g, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from classroom50.db import get_db
from classroom50.views.auth import login_required, student_only, teacher_only

assignments_bp = Blueprint("assignments", __name__, url_prefix="/assignments")


@assignments_bp.route("/list")
@login_required
def assignments(classroom_id):
    """Show classroom assignments."""

    db = get_db()

    # Query assignments
    assignments = db.execute(
        "SELECT a.id, a.author_id, a.timestamp, a.title, a.deadline, u.name AS author"
        "  FROM assignments AS a"
        "  JOIN users AS u"
        "    ON u.id = a.author_id"
        " WHERE a.classroom_id = ?"
        " ORDER BY a.timestamp DESC",
        (classroom_id,)
    ).fetchall()

    # Query submissions
    submissions = db.execute(
        "SELECT id, assignment_id, filename, grade FROM submissions WHERE classroom_id = ? AND author_id = ?",
        (classroom_id, g.user["id"])
    ).fetchall()

    # Get current date and time
    datetime_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    return render_template("classroom/assignments.html", classroom_id=classroom_id, assignments=assignments, datetime_now=datetime_now, submissions=submissions)


@assignments_bp.route("/create", methods=["GET", "POST"])
@login_required
@teacher_only
def create(classroom_id):
    """Create new assignment."""

    if request.method == "POST":

        # Get user input
        title = request.form.get("title")
        date = request.form.get("date")
        time = request.form.get("time")

        db = get_db()
        error = None

        # Validate user input
        if not title or title.isspace():
            error = "Missing assignment title!"
        elif date and not time:
            error = "Missing deadline time!"
        elif time and not date:
            error = "Missing deadline date!"

        # Construct deadline
        deadline = None
        if date and time:
            deadline = date + ' ' + time

        if deadline:

            # Get current date and time
            datetime_now = (datetime.now(timezone.utc) + timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M")

            if deadline < datetime_now:
                error = "Invalid deadline!"

        # If validation succeeds
        if error is None:

            # Remove leading and trailing whitespace from title if any
            title = title.strip()

            # Add the new assignment to the database
            db.execute(
                "INSERT INTO assignments (classroom_id, author_id, title, deadline) VALUES(?, ?, ?, ?)",
                (classroom_id, g.user["id"], title, deadline)
            )
            db.commit()

            flash("Assignment created!", "success")
            return redirect(url_for("classroom.assignments.assignments", classroom_id=classroom_id))

        # If validation fails, show the error to the user
        flash(error, "error")
        return redirect(url_for("classroom.assignments.create", classroom_id=classroom_id))
    else:

        # Get current date
        date_now = (datetime.now(timezone.utc) + timedelta(minutes=20)).strftime("%Y-%m-%d")

        return render_template("classroom/create_assignment.html", classroom_id=classroom_id, date_now=date_now)


@assignments_bp.route("/<int:assignment_id>/delete", methods=["POST"])
@login_required
@teacher_only
def delete_assignment(classroom_id, assignment_id):
    """Delete assignment."""

    db = get_db()
    error = None

    # Query assignment author id
    assignment = db.execute(
        "SELECT author_id FROM assignments WHERE id = ? AND classroom_id = ?",
        (assignment_id, classroom_id)
    ).fetchone()

    # Validate user input
    if assignment is None:
        error = "Assignment not found!"
    elif g.user["id"] != assignment["author_id"] and g.user["id"] != g.classroom_owner_id:
        error = "Invalid action!"

    # If validation succeeds
    if error is None:

        # Delete assignment and submissions from the database
        db.execute(
            "DELETE FROM submissions WHERE assignment_id = ?", (assignment_id,)
        )
        db.commit()

        db.execute(
            "DELETE FROM assignments WHERE id = ?", (assignment_id,)
        )
        db.commit()

        # Delete assignment folder and it's contents
        relative_path = "classroom" + str(classroom_id) + "/assignment" + str(assignment_id)
        if os.path.isdir(os.path.join(current_app.config["UPLOAD_FOLDER"], relative_path)):
            shutil.rmtree(os.path.join(current_app.config["UPLOAD_FOLDER"], relative_path))

        flash("Assignment deleted!", "success")

    # If validation fails
    else:

        # Show the error to the user
        flash(error, "error")

    return redirect(url_for("classroom.assignments.assignments", classroom_id=classroom_id))


@assignments_bp.route("/<int:assignment_id>/submissions")
@login_required
@teacher_only
def submissions(classroom_id, assignment_id):
    """Show assignment submissions."""

    db = get_db()

    # Query assignment
    assignment = db.execute(
        "SELECT id, title FROM assignments WHERE id = ? AND classroom_id = ? AND author_id = ?",
        (assignment_id, classroom_id, g.user["id"])
    ).fetchone()

    # If assignment exists
    if assignment:

        # Query submissions
        submissions = db.execute(
            "SELECT s.id, s.filename, s.grade, u.name AS author"
            "  FROM submissions AS s"
            "  JOIN users AS u"
            "    ON u.id = s.author_id"
            " WHERE s.assignment_id = ?",
            (assignment_id,)
        ).fetchall()

        return render_template("classroom/submissions.html", classroom_id=classroom_id, assignment=assignment, submissions=submissions)

    # If assignment does not exist, show an error to the user
    flash("Assignment not found!", "error")
    return redirect(url_for("classroom.assignments.assignments", classroom_id=classroom_id))


@assignments_bp.route("/<int:assignment_id>/submit", methods=["POST"])
@login_required
@student_only
def submit(classroom_id, assignment_id):
    """Submit assignment."""

    db = get_db()
    error = None

    # Get user input
    file = request.files.get("file")

    # Query assignment
    assignment = db.execute(
        "SELECT id, deadline FROM assignments WHERE id = ? AND classroom_id = ?",
        (assignment_id, classroom_id)
    ).fetchone()

    # Validate user input
    if file.filename == "":
        error = "No selected file!"
    elif assignment is None:
        error = "Assignment not found!"
    elif assignment["deadline"]:

        # Get current date and time
        datetime_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

        if assignment["deadline"] <= datetime_now:
            error = "Assignment is overdue!"

    # Query submission
    submission = db.execute(
        "SELECT id, filename FROM submissions WHERE assignment_id = ? AND author_id = ?",
        (assignment_id, g.user["id"])
    ).fetchone()

    # If validation succeeds
    if error is None:

        relative_path = "classroom" + str(classroom_id) + "/assignment" + str(assignment_id) + "/user" + str(g.user["id"]) + "/"
        abs_path = os.path.join(current_app.config["UPLOAD_FOLDER"], relative_path)

        # Create directories if they do not exist
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

        if file:

            # Secure filename
            filename = secure_filename(file.filename)

            # If the user has not submitted this assigment
            if submission is None:

                # Add the new submission to the database
                db.execute(
                    "INSERT INTO submissions (classroom_id, assignment_id, author_id, filename, folder_path) VALUES(?, ?, ?, ?, ?)",
                    (classroom_id, assignment_id, g.user["id"], filename, relative_path)
                )
                db.commit()

            # If the user has submitted this assignment
            else:

                # Remove previous file
                os.remove(os.path.join(abs_path, submission["filename"]))

                # Update submission
                db.execute(
                    "UPDATE submissions SET filename = ?, grade = NULL WHERE id = ?",
                    (filename, submission["id"])
                )
                db.commit()

            # Save file
            file.save(os.path.join(abs_path, filename))

        flash("File submitted!", "success")

    # If validation fails
    else:

        # Show the error to the user
        flash(error, "error")

    return redirect(url_for("classroom.assignments.assignments", classroom_id=classroom_id))


@assignments_bp.route("/<int:assignment_id>/submissions/<int:submission_id>/delete", methods=["POST"])
@login_required
@student_only
def delete_submission(classroom_id, assignment_id, submission_id):
    """Delete submission."""

    db = get_db()

    # Query submission folder path
    submission = db.execute(
        "SELECT folder_path FROM submissions WHERE id = ? AND classroom_id = ? AND assignment_id = ? AND author_id = ?",
        (submission_id, classroom_id, assignment_id, g.user["id"])
    ).fetchone()

    # If submission exists
    if submission:

        # Delete user folder and submission file
        shutil.rmtree(os.path.join(current_app.config["UPLOAD_FOLDER"], submission["folder_path"]))

        # Delete submission from the database
        db.execute("DELETE FROM submissions WHERE id = ?", (submission_id,))
        db.commit()

        flash("Submission deleted!", "success")

    # If submission does not exist
    else:

        # Show an error to the user
        flash("Submission not found!", "error")

    return redirect(url_for("classroom.assignments.assignments", classroom_id=classroom_id))


@assignments_bp.route("/<int:assignment_id>/submissions/<int:submission_id>/download")
@login_required
@teacher_only
def download(classroom_id, assignment_id, submission_id):
    """Download submission."""

    db = get_db()
    error = None

    # Check if assignment exists
    assignment = db.execute(
        "SELECT 1 FROM assignments WHERE id = ? AND classroom_id = ? AND author_id = ?",
        (assignment_id, classroom_id, g.user["id"])
    ).fetchone()

    # Query submission
    submission = db.execute(
        "SELECT filename, folder_path FROM submissions WHERE id = ? AND classroom_id = ? AND assignment_id = ?",
        (submission_id, classroom_id, assignment_id)
    ).fetchone()

    # Validate user input
    if assignment is None:
        flash("Assignment not found!", "error")
        return redirect(url_for("classroom.assignments.assignments", classroom_id=classroom_id))
    elif submission is None:
        error = "Submission not found!"

    # If validation succeeds
    if error is None:

        # Download submission
        return send_from_directory(os.path.join(current_app.config["UPLOAD_FOLDER"], submission["folder_path"]), submission["filename"], as_attachment=True)

    # If validation fails, show the error to the user
    flash(error, "error")
    return redirect(url_for("classroom.assignments.submissions", classroom_id=classroom_id, assignment_id=assignment_id))


@assignments_bp.route("/<int:assignment_id>/submissions/<int:submission_id>/grade", methods=["POST"])
@login_required
@teacher_only
def grade(classroom_id, assignment_id, submission_id):
    """Grade submission."""

    # Get user input
    grade = request.form.get("grade")

    db = get_db()
    error = None

    # Check if assignment exists
    assignment = db.execute(
        "SELECT 1 FROM assignments WHERE id = ? AND classroom_id = ? AND author_id = ?",
        (assignment_id, classroom_id, g.user["id"])
    ).fetchone()

    # Check if submission exists
    submission = db.execute(
        "SELECT 1 FROM submissions WHERE id = ? AND classroom_id = ? AND assignment_id = ?",
        (submission_id, classroom_id, assignment_id)
    ).fetchone()

    # Validate user input
    if assignment is None:
        flash("Assignment not found", "error")
        return redirect(url_for("classroom.assignments.assignments", classroom_id=classroom_id))
    elif submission is None:
        error = "Submission not found!"
    elif not grade in ["A", "B", "C", "D", "E", "F"]:
        error = "Invalid grade!"

    # If validation succeeds
    if error is None:

        # Grade submission
        db.execute(
            "UPDATE submissions SET grade = ? WHERE id = ?",
            (grade, submission_id)
        )
        db.commit()

        flash("Submission graded!", "success")

    # If validation fails
    else:

        # Show the error to the user
        flash(error, "error")

    return redirect(url_for("classroom.assignments.submissions", classroom_id=classroom_id, assignment_id=assignment_id))