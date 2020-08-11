import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(test_config=None):
    # create, configure, and db
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(DefaultConfig())

    # initialize plugins
    db.app = app
    db.init_app(app)
    login_manager.init_app(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register blueprints for routes
    from src.flaskov.routes import main, auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app


class DefaultConfig:
    SECRET_KEY = 'dev'
    SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite"


class TestConfig:
    SECRET_KEY = 'dev'
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.sqlite"
    USERNAME = "username"
    PASSWORD = "password"
    EMAIL = "JohnDoe@gmail.com"
    TESTING = True