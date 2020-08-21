import json
import random

from flask_login import UserMixin

from . import db, login_manager

from werkzeug.security import generate_password_hash, check_password_hash


###############################################################
# Models                                                      #
###############################################################

class User(db.Model, UserMixin):
    """
    User model for authentication

    TODO:
        Implement storage of markov models for each user.
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_id(self):
        return self.id

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)



class MarkovModel(db.Model):
    """
    Markov Chain model for sentence generation
    
    `START`: string
        denotes the start of a sentence. serves as 
        the root of the model dict.

    `END`: string
        denotes the end of a sentence.

    `DEFAULT_NAME`: string
        denotes default model name when no name is 
        provided or no corpus is provided

    `EMPTY_MODEL_ERROR`: string
        error message when generate() is called with
        no markov model.

    TODO:
        implement methods to generate sentences
    """
    __tablename__ = 'markov_model'
    id = db.Column(db.Integer, primary_key = True)
    model_name = db.Column(db.String(200), unique=True, nullable=False)
    model_size = db.Column(db.String(200), nullable=False)
    model_order = db.Column(db.Integer, nullable=False)
    model_serialized = db.Column(db.String(), nullable=False)
    
    START = "START"
    END = "END"
    DEFAULT_NAME = "Unnamed Model"
    EMPTY_MODEL_ERROR = (
        "WHOA! You are trying to generate a sentence from an empty model!"
    )

    def __repr__(self):
        return '<MarkovModel {}>'.format(self.model_name)

    def get_id(self):
        return self.id

    def __init__(self, corpus=None, model=None, order=1, name=None):
        """
        `corpus`: 
            a chunk of text. Should be multiple sentences 
            delimited by '. '. This is transformed into a 
            list of lists where the outer list is composed 
            sentences and each inner list is composed of the 
            words that make up a particular sentence

        `model`: 
            A dict. each key represents a word (or words) 
            in a sentence where the corresponding value is a 
            list containing words that have followed as keys. 
            essentially, an already built markov model. This 
            option is to support serialization/deserialization.

        `order`: 
            an integer. The number of words used to predict
            the next word in a sentence.

        `name`:
            Name of the model:
                - if provided, self.model_name = name
                - if not provided, and corpus is provided, 
            
        """
        self.model = (
            model if model else 
            {})
        self.model_name = (
            name if name else 
            corpus[0:20] + "..." if corpus else 
            self.DEFAULT_NAME)
        self.model_order = order
        if corpus:
            for sentence in corpus.split('. '):
                self.add_sentence(sentence.split())

        self.serialize()

    def _compute_size(self):
        """Subtract 2 from model size to get rid of START & END nodes"""
        self.model_size = len(self.model.keys()) - self.model_order - 2

    def add_sentence(self, sentence):
        """
        Adds a sentence to the markov model. Used to build markov models.
        
        `sentence`:
            list of words that are ordered as a syntactically correct
            sentence. used to generate model. 
        """
        order = self.model_order
        words = [self.START]*order + sentence + [self.END]

        # IMPORTANT COMMENT:
        #
        # loop through (sentence.len + 1) because words.length 
        # is equal to (sentence.length + order + 1)
        #
        # order is taken into account with list slicing below,
        # so we have to include the one to take into account the
        # END string
        for i in range(len(sentence) + 1):
            current = tuple(words[i:i+order])
            follows = words[i+order]

            if current not in self.model:
                self.model[current] = {}

            if follows not in self.model[current]:
                self.model[current][follows] = 0

            self.model[current][follows] += 1

        self._compute_size()

    def generate(self):
        """
        Generates a sentence from the markov model
        """
        self.deserialize()
        if self.model == {}:
            return self.EMPTY_MODEL_ERROR

        current_state = tuple(self.model_order * [self.START])
        word_list = []
        next_word = ""

        while self.END != next_word:
            next_word = random.choices(
                [i for i in self.model[current_state].keys()],
                weights=[i for i in self.model[current_state].values()]
            )[0] # we need string, not list of string

            word_list.append(next_word)
            current_state = tuple([next_word])

        return ' '.join(word_list)

    def serialize(self):
        """
        Serialize model as JSON string
        Stores serialization as `model_serialized` member
        """
        self.model_serialized = json.dumps(list(self.model.items()))

    def deserialize(self):
        """
        Deserialize JSON string to model
        Stores deserialized model as `model` member
        """
        raw_model = json.loads(self.model_serialized)
        # Next line removes outermost list, and changes keys from
        # lists to tuples (to match original model structure)
        self.model = {tuple(pair[0]):pair[1] for pair in raw_model}


###############################################################
# Helper Functions                                            #
###############################################################

@login_manager.user_loader
def user_loader(user_id):
    try:
        return User.query.get(user_id)
    except:
        return