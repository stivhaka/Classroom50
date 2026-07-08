import os

from flask import Flask
from flask_session import Session


def create_app():
    """Create and configure the app."""

    app = Flask(__name__)

    app.config.from_mapping(
        DATABASE = os.path.join(app.instance_path, "classroom50.db"),
        MAX_CONTENT_LENGTH = 1000 ** 3,
        SESSION_PERMANENT = False,
        SESSION_TYPE = "filesystem",
        UPLOAD_FOLDER = os.getcwd() + "/uploads/"
    )

    Session(app)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Ensure the upload folder exists
    try:
        os.makedirs(os.getcwd() + "/uploads/")
    except OSError:
        pass

    from classroom50 import db

    db.init_app(app)

    from classroom50.views import auth, classroom, main, profile

    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(classroom.classroom_bp)
    app.register_blueprint(main.main_bp)
    app.register_blueprint(profile.profile_bp)

    app.add_url_rule('/', endpoint="index")

    return app