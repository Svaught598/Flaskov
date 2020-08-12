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


@login_manager.user_loader
def user_loader(user_id):
    try:
        print(user_id)
        print(User.query.get(user_id))
        return User.query.get(user_id)
    except:
        return