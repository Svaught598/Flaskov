from flask_login import UserMixin

from . import db, login_manager

from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    _is_authenticated = False
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

    @property
    def is_authenticated(self):
        return self._is_authenticated

    @is_authenticated.setter
    def is_authenticated(self, boolean):
        self._is_authenticated = boolean

    def get_id(self):
        return self.id


@login_manager.user_loader
def user_loader(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return
    
    user.id = email
    return user


# @login_manager.request_loader
# def request_loader(request):
#     email = request.form.get('email')
#     user = User.query.filter_by(email=email).first()

#     # no user, return None
#     if not user:
#         return

#     # if user, set is_auth & return user
#     user.id = email
#     user.is_authenticated = check_password_hash(
#         request.form['password'], 
#         user.password
#     )
#     return user
