from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from classroom50.db import get_db
from classroom50.views.auth import login_required

home_bp = Blueprint("home", __name__)


@home_bp.route("/home")
@login_required
def home(classroom_id):
    """Show classroom information, posts and comments."""

    db = get_db()

    # Query classroom
    classroom = db.execute(
        "SELECT name, description, subject FROM classrooms WHERE id = ?",
        (classroom_id,)
    ).fetchone()

    # Query posts
    posts = db.execute(
        "SELECT p.id, p.author_id, p.timestamp, p.title, p.body, u.name AS author"
        "  FROM posts AS p"
        "  JOIN users AS u"
        "    ON u.id = p.author_id"
        " WHERE p.classroom_id = ?"
        " ORDER BY p.timestamp DESC",
        (classroom_id,)
    ).fetchall()

    # Query comments
    comments = db.execute(
        "SELECT c.id, c.post_id, c.author_id, c.timestamp, c.body, u.name AS author"
        "  FROM comments AS c"
        "  JOIN users AS u"
        "    ON u.id = c.author_id"
        " WHERE c.classroom_id = ?"
        " ORDER BY c.timestamp DESC",
        (classroom_id,)
    ).fetchall()

    return render_template("classroom/home.html", classroom_id=classroom_id, classroom=classroom, comments=comments, posts=posts)


@home_bp.route("/post", methods=["GET", "POST"])
@login_required
def post(classroom_id):
    """Create new post."""

    if request.method == "POST":

        # Get user input
        title = request.form.get("title")
        body = request.form.get("body")

        db = get_db()
        error = None

        # Validate user input
        if not title or title.isspace():
            error = "Missing post title!"
        elif not body or body.isspace():
            error = "Missing post body!"

        # If validation succeeds
        if error is None:

            # Remove leading and trailing whitespace from title and body if any
            title = title.strip()
            body = body.strip()

            # Add the new post to the database
            db.execute(
                "INSERT INTO posts (classroom_id, author_id, title, body) VALUES(?, ?, ?, ?)",
                (classroom_id, g.user["id"], title, body)
            )
            db.commit()

            flash("Post created!", "success")
            return redirect(url_for("classroom.home.home", classroom_id=classroom_id))


        # If validation fails, show the error to the user
        flash(error, "error")
        return redirect(url_for("classroom.home.post", classroom_id=classroom_id))
    else:
        return render_template("classroom/post.html", classroom_id=classroom_id)


@home_bp.route("/delete-post/<int:post_id>", methods=["POST"])
@login_required
def delete_post(classroom_id, post_id):
    """Delete post."""

    db = get_db()
    error = None

    # Query post author id
    post = db.execute(
        "SELECT author_id FROM posts WHERE id = ? AND classroom_id = ?",
        (post_id, classroom_id)
    ).fetchone()

    # Validate user input
    if post is None:
        error = "Post not found!"
    elif g.user["id"] != post["author_id"] and g.user["id"] != g.classroom_owner_id:
        error = "Invalid action!"

    # If validation succeeds
    if error is None:

        # Delete post and comments
        db.execute(
            "DELETE FROM comments WHERE post_id = ?", (post_id,)
        )
        db.commit()

        db.execute(
            "DELETE FROM posts WHERE id = ?", (post_id,)
        )
        db.commit()

        flash("Post deleted!", "success")

    # If validation fails
    else:

        # Show the error to the user
        flash(error, "error")

    return redirect(url_for("classroom.home.home", classroom_id=classroom_id))


@home_bp.route("/comment/<int:post_id>", methods=["POST"])
@login_required
def comment(classroom_id, post_id):
    """Create new comment."""

    # Get user input
    body = request.form.get("body")

    db = get_db()
    error = None

    # Check if post exists
    post = db.execute(
        "SELECT 1 FROM posts WHERE id = ? AND classroom_id = ?",
        (post_id, classroom_id)
    ).fetchone()

    # Validate user input
    if post is None:
        error = "Post not found!"
    elif not body or body.isspace():
        error = "Missing comment!"

    # If validation succeeds
    if error is None:

        # Remove leading and trailing whitespace from body
        body = body.strip()

        # Add the new comment to the database
        db.execute(
            "INSERT INTO comments (classroom_id, post_id, author_id, body) VALUES(?, ?, ?, ?)",
            (classroom_id, post_id, g.user["id"], body)
        )
        db.commit()

        flash("Comment created!", "success")

    # If validation fails
    else:

        # Show the error to the user
        flash(error, "error")

    return redirect(url_for("classroom.home.home", classroom_id=classroom_id))


@home_bp.route("/delete-comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(classroom_id, comment_id):
    """Delete comment."""

    db = get_db()
    error = None

    # Query comment author id
    comment = db.execute(
        "SELECT author_id FROM comments WHERE id = ? AND classroom_id = ?",
        (comment_id, classroom_id)
    ).fetchone()

    # Validate user input
    if comment is None:
        error = "Comment not found!"
    elif g.user["id"] != comment["author_id"] and g.user["id"] != g.classroom_owner_id:
        error = "Invalid action!"

    # If validation succeeds
    if error is None:

        # Delete comment
        db.execute(
            "DELETE FROM comments WHERE id = ?", (comment_id,)
        )
        db.commit()

        flash("Comment deleted!", "success")

    # If validation fails
    else:

        # Show the error to the user
        flash(error, "error")

    return redirect(url_for("classroom.home.home", classroom_id=classroom_id))