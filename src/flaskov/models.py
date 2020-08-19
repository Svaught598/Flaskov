import json

from flask_login import UserMixin

from . import db, login_manager

from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
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
    
    `START`: 
        [string] to denote the start of a sentence. serves as 
        the root of the model dict.
    `END`: 
        [string] to denote the end of a sentence.
    """
    __tablename__ = 'markov_model'
    id = db.Column(db.Integer, primary_key = True)

    START = ["START"]
    END = ["END"]

    def __init__(self, corpus=None, model=None, order=1):
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
        """
        self.model = model if model else {}
        self.order = order
        if corpus:
            # split corpus into list of sentences
            for sentence in corpus.split('. '):
                # add sentence as list of constituent words
                self.add_sentence(sentence.split())

    def add_sentence(self, sentence):
        """
        Adds a sentence to the markov model. Used to build markov models.
        
        `sentence`:
            list of words that are ordered as a syntactically correct
            sentence. used to generate model. 
        """
        self.old_model = self.model
        order = self.order
        words = self.START*order + sentence + self.END
        for i in range(len(sentence) + 1):
            current = tuple(words[i:i+order])
            follows = words[i+order]

            if current not in self.model:
                self.model[current] = {}

            if follows not in self.model[current]:
                self.model[current][follows] = 0

            self.model[current][follows] += 1
        if "This" in sentence:
            import pdb; pdb.set_trace()

    def serialize(self):
        """Serialize model as JSON string"""
        return json.dumps(list(self.model.items()))

    @classmethod
    def deserialize(cls, serialized_model):
        """Deserialize JSON string to model"""
        raw_model = json.loads(serialized_model)
        model = {tuple(pair[0]):pair[1] for pair in raw_model}
        #import pdb; pdb.set_trace()
        return cls(model=model)
        


            
            








@login_manager.user_loader
def user_loader(user_id):
    try:
        return User.query.get(user_id)
    except:
        return