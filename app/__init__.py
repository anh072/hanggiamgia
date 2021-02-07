from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

from config import config


db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{os.environ.get('DATABASE_USERNAME')}:{os.environ.get('DATABASE_PASSWORD')}"
        f"@{os.environ.get('DATABASE_HOST')}:5432/{os.environ.get('DATABASE_NAME')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    config[config_name].init_app(app)

    db.init_app(app)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api/v1")

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app