import os
import sys
import tempfile
from sqlite3 import IntegrityError

import pytest

from flask_login import current_user

from werkzeug.security import generate_password_hash

from ..flaskov.models import *



###############################################################
# Pytest Fixtures                                             #
###############################################################

USERNAME = "USERNAME"
PASSWORD = "PASSWORD"
EMAIL = "EMAIL"
CORPUS = """
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

@pytest.fixture(scope='function')
def user():
    return User(
        username = USERNAME,
        password = generate_password_hash(PASSWORD),
        email = EMAIL,
    )

@pytest.fixture(scope='function')
def markovmodel():
    return MarkovModel(corpus=CORPUS, order=1)

###############################################################
# Pytest Helpers                                              #
###############################################################



###############################################################
# Tests                                                       #
###############################################################

# Tests for user model ########################################

def test_check_password(user):
    assert user.check_password(PASSWORD)
    assert not user.check_password("wrong password")

def test_set_password(user):
    NEW_PASSWORD = "new password"
    OLD_PASSWORD = PASSWORD
    user.set_password(NEW_PASSWORD)
    assert user.check_password(NEW_PASSWORD)
    assert not user.check_password(OLD_PASSWORD)


# Tests for markov model ######################################

def test_empty_markov():
    test_model = MarkovModel()
    assert test_model.model == {}

def test_markov_add_sentence(markovmodel):
    old_model = markovmodel.model.copy()
    markovmodel.add_sentence(["This", "is", "a", "new", "sentence."])
    model = markovmodel.model
    assert model != old_model

def test_markov_serialization(markovmodel):
    previous_model = markovmodel.model.copy()
    markovmodel.serialize()
    markovmodel.deserialize()
    assert previous_model == markovmodel.model

def test_model_name(markovmodel):
    assert markovmodel.model_name == CORPUS[0:20]+"..."