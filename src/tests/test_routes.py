import os
import sys
import tempfile
from sqlite3 import IntegrityError

import pytest

from flask_login import current_user

from werkzeug.security import generate_password_hash

from ..flaskov import *
from ..flaskov.models import User

app = create_app()
app.config.from_object(TestConfig())
u = User(
    username = app.config['USERNAME'],
    email = app.config['EMAIL'],
    password = generate_password_hash(app.config['PASSWORD']),
)
try:
    db.drop_all()
    db.create_all()
    db.session.add(u)
    db.session.commit()
except:
    db.session.rollback()
finally:
    db.session.close()


###############################################################
# Pytest Fixtures                                             #
###############################################################

@pytest.fixture
def client():
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
        'password': password,
        'email': email,
    }, follow_redirects=True)


###############################################################
# Tests                                                       #
###############################################################

def test_index_route(client):
    rv = client.get('/index')
    assert b'index' in rv.data


def test_about_route(client):
    rv = client.get('/about')
    assert b'about' in rv.data


def test_login_logout_route(client):
    # check login/logout
    rv = login(client, app.config['USERNAME'], app.config['PASSWORD'])
    assert b"Success!" in rv.data
    assert current_user.is_authenticated

    rv = logout(client)
    assert b"logout" in rv.data

    # check incorrect username/password
    rv = login(client, app.config['USERNAME'] + "wrong", app.config['PASSWORD'])
    assert b"Incorrect Username or Password" in rv.data

    rv = login(client, app.config['USERNAME'], app.config['PASSWORD'] + 'wrong')
    assert b"Incorrect Username or Password" in rv.data


def test_register_route(client):
    # Register new account (should not authenticate)
    rv = register(client, "JohnDoe", "password", "JohnDoe@somewhere.com")
    assert b'index' in rv.data
    assert not current_user.is_authenticated

    # Register account (username taken)
    rv = register(client, app.config['USERNAME'], "password", "Somewhere@gmail.com")
    assert b'Sorry, that username is already taken!' in rv.data
    assert not current_user.is_authenticated

    # Register account (email taken)
    rv = register(client, "MatthewWood", "password", app.config["EMAIL"])
    assert b'Sorry, that email is already taken!'
    assert not current_user.is_authenticated

    # Register account (already logged in)
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    assert current_user.is_authenticated
    assert b'Please logout to register a new account' in rv.data
