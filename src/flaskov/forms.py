from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    PasswordField, 
    SubmitField, 
    BooleanField
)
from wtforms.validators import (
    DataRequired, 
    Email, 
    EqualTo, 
    Length, 
    Optional
)


class LoginForm(FlaskForm):
    """
    Simple Login Form
    
    DataRequired Fields:
        - username
        - password
        - submit
    Optional Fields:
        - remember
    """
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember = BooleanField('Remember', validators = [Optional()])
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    """ 
    New User Registration Form 

    Data Required Fields:
        - username
        - email
        - password
        - password2
        - submit
    """
    username = StringField(
        'Username',
        validators = [
            DataRequired(),
        ]
    )
    email = StringField(
        'Email',
        validators = [
            DataRequired(),
            Email(message="Enter a valid email address"),
        ]
    )
    password = PasswordField(
        'Password',
        validators = [
            DataRequired(),
            Length(min=5, message="Password is too short!"),
        ]
    )
    password2 = PasswordField(
        'Confirm Password',
        validators = [
            DataRequired(),
            EqualTo("password", message="Passwords do not match!"),
        ]
    )
    submit = SubmitField("Register!")