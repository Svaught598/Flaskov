import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import 
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(test_config=None):
    # create, configure, and db
    app = Flask(__name__, instance_relative_config=True)
    if test_config:
        app.config.from_object(test_config)
    else:
        app.config.from_object(DefaultConfig())

    # initialize plugins
    db.app = app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

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
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig:
    SECRET_KEY = 'dev'
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.sqlite"
    USERNAME = "username"
    PASSWORD = "password"
    EMAIL = "JohnDoe@gmail.com"
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False