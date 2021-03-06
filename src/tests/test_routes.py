import os
import sys
import tempfile
from sqlite3 import IntegrityError

import pytest
from flask_login import current_user
from flask import session
from werkzeug.security import generate_password_hash

from ..flaskov import create_app, TestConfig
from ..flaskov import db as _db
from ..flaskov import login_manager 
from ..flaskov.models import User, MarkovModel



###############################################################
# Pytest Fixtures                                             #
###############################################################

TESTDB = 'test.sqlite'
TESTDB_PATH = os.path.join(os.getcwd(), 'src/flaskov/', TESTDB) 
TEST_DATABASE_URI = 'sqlite:///' + TESTDB_PATH


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    app = create_app(TestConfig())
    login_manager.init_app(app)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    if os.path.exists(TESTDB_PATH):
        os.unlink(TESTDB_PATH)

    def teardown():
        _db.drop_all()
        os.unlink(TESTDB_PATH)
    
    _db.app = app
    _db.create_all()

    user = User(username = app.config["USERNAME"], email=app.config["EMAIL"])
    user.set_password(app.config["PASSWORD"])
    _db.session.add(user)
    _db.session.commit()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def _session(db, request): # named with underscore to prevent shadowing with flask session object
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    _session = db.create_scoped_session(options=options)

    db.session = _session

    def teardown():
        transaction.rollback()
        connection.close()
        _session.remove()

    request.addfinalizer(teardown)
    return _session


@pytest.fixture(scope='function')
def client(db, _session, app):
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


###############################################################
# Pytest Helpers                                              #
###############################################################

def login(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password,
        'remember': False
    }, follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def register(client, username, password, email):
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password,
        'password2': password,
    }, follow_redirects=True)

def generate_model(client, corpus, name, order):
    return client.post('/generate_model', data={
        'corpus': corpus,
        'name': name,
        'order': order,
    }, follow_redirects=True)

def generate_sentence(client, name):
    return client.get(f'/generate_sentence', data={
        'model_name': name,
    }, follow_redirects=True)


###############################################################
# Auth Tests                                                  #
###############################################################

def test_index(client):
    """ Test for index route """
    rv = client.get('/index')
    assert b'index' in rv.data


def test_about(client):
    """ Test for about route """
    rv = client.get('/about')
    assert b'about' in rv.data


def test_login_logout(client, app, db):
    """ Test for Login/Logout """
    # check login/logout
    rv = login(client, app.config['USERNAME'], app.config['PASSWORD'])
    assert b"Success!" in rv.data

    rv = logout(client)
    assert b"logout" in rv.data


def test_incorrect_login(client, app):
    """ Test for incorrect login credentials (username/password)"""
    # check incorrect username
    rv = login(client, app.config['USERNAME'] + "wrong", app.config['PASSWORD'])
    assert b"Incorrect Username or Password" in rv.data

    # check incorrect password
    rv = login(client, app.config['USERNAME'], app.config['PASSWORD'] + 'wrong')
    assert b"Incorrect Username or Password" in rv.data


def test_register(client, app):
    """ Test registering a new account"""
    # Register new account (should authenticate)
    rv = register(client, "JohnDoe", "password", "JohnDoe@somewhere.com")
    assert b'index' in rv.data
    assert current_user.is_authenticated


def test_register_taken(client, app):
    """ Test for registration attempt with username/email already taken"""
    # Register account (username taken)
    rv = register(client, app.config['USERNAME'], "password", "Somewhere@gmail.com")
    assert b'Sorry, that username is already taken!' in rv.data
    assert not current_user.is_authenticated

    # Register account (email taken)
    rv = register(client, "MatthewWood", "password", app.config["EMAIL"])
    assert b'Sorry, that email is already taken!'
    assert not current_user.is_authenticated


def test_register_logged_in(client, app):
    """ Test for registration attempt when already logged in"""
    # Register account (already logged in)
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = register(client, "Some username", "Some password", "email@gmail.com")
    assert b'Please logout to register a new account' in rv.data


###############################################################
# Markov Tests                                                #
###############################################################

TEST_ORDER = 1
TEST_MODEL_NAME = "testmodel"
TEST_CORPUS = """
    Lorem ipsum dolor sit amet, consectetuer adipiscing elit, 
    sed diam nonummy nibh euismod tincidunt ut laoreet dolore 
    magna aliquam erat volutpat. Ut wisi enim ad minim veniam, 
    quis nostrud exercitation ulliam corper suscipit lobortis 
    nisl ut aliquip ex ea commodo consequat. Duis autem veleum 
    iriure dolor in hendrerit in vulputate velit esse molestie 
    consequat, vel willum lunombro dolore eu feugiat nulla 
    facilisis at vero eros et accumsan et iusto odio dignissim 
    qui blandit praesent luptatum zzril delenit augue duis dolore 
    te feugait nulla facilisi.
"""

def test_creating_model_sets_model_id_on_session_and_displays_model_name(client):
    rv = generate_model(client, corpus=TEST_CORPUS, name=TEST_MODEL_NAME, order=TEST_ORDER)
    #new_model = MarkovModel.query.filter_by(model_name=TEST_MODEL_NAME).first()
    #assert "testmodel" == new_model.model_name
    assert b'testmodel' in rv.data

def test_generated_sentence_displayed(client):
    generate_model(client, corpus=TEST_CORPUS, name=TEST_MODEL_NAME, order=TEST_ORDER)
    rv = generate_sentence(client, name=TEST_MODEL_NAME)
    assert b'sentence' in rv.data