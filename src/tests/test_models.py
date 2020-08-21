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

def test_empty_model_should_have_empty_model_member():
    test_model = MarkovModel()
    assert test_model.model == {}

def test_add_sentence_should_update_model_size(markovmodel):
    # update with words in model doesn't produce new nodes, size is same
    old_model_size = markovmodel.model_size
    markovmodel.add_sentence(["Lorem", "ipsum", "dolor", "sit", "amet,"])
    new_model_size = markovmodel.model_size
    assert new_model_size == old_model_size

    # update with words not in model does produce new nodes, size is changed
    old_model_size = markovmodel.model_size
    markovmodel.add_sentence(["This", "is", "a", "new", "sentence."])
    new_model_size = markovmodel.model_size
    assert new_model_size != old_model_size

def test_add_sentence_should_update_model(markovmodel):
    old_model = markovmodel.model.copy()
    markovmodel.add_sentence(["This", "is", "a", "new", "sentence."])
    model = markovmodel.model
    assert model != old_model

def test_sequential_serialize_deserialize_should_preserve_original_model(markovmodel):
    previous_model = markovmodel.model.copy()
    markovmodel.serialize()
    markovmodel.deserialize()
    assert previous_model == markovmodel.model

def test_model_name_should_default_to_first_20_chars_of_corpus(markovmodel):
    assert markovmodel.model_name == CORPUS[0:20]+"..."

def test_model_name_should_default_to_DEFAULT_NAME_if_no_corpus_and_no_name():
    testmodel = MarkovModel()
    assert testmodel.model_name == testmodel.DEFAULT_NAME

def test_empty_model_should_generate_error_sentence():
    testmodel = MarkovModel()
    sentence = testmodel.generate()
    assert sentence != None
    assert sentence == testmodel.EMPTY_MODEL_ERROR

def test_full_model_should_generate_sentence(markovmodel):
    sentence = markovmodel.generate()
    assert type(sentence) == str
    assert len(sentence) != 0
    assert sentence != markovmodel.EMPTY_MODEL_ERROR