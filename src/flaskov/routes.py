from flask import (
    Blueprint, 
    render_template, 
    redirect,
    request,
    flash,
    url_for,
    abort,
)
from flask_login import (
    login_user, 
    logout_user, 
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from jinja2 import TemplateNotFound

from .models import User
from .forms import LoginForm, RegisterForm
from . import db


###############################################################
# Main Blueprint                                              #
###############################################################

main = Blueprint("main", __name__, template_folder="templates")


@main.route("/index")
def index():
    return render_template("index.html")


@main.route("/about/")
def about():
    return render_template("about.html")


###############################################################
# Auth Blueprint                                              #
###############################################################

auth = Blueprint("auth", __name__, template_folder="templates")


@auth.route("/login/", methods=['GET', 'POST'])
def login_post():
    """ Route for user login"""
    form = LoginForm(request.form)

    # validate on submit returns false if GET request
    # also checks form field validators
    if form.validate_on_submit():
        user = User.query.filter_by(username=str(form.username.data)).first()

        # Check that user exists, and pass is correct
        if user and user.check_password(form.password.data):
            flash("Success!")
            login_user(user, remember=form.remember)
            return redirect(url_for('main.index'))

        # else warn and redirect 
        flash("Incorrect Username or Password")
    return render_template('login.html')


@auth.route("/register", methods=['GET', 'POST'])
def register_post():
    """ Route for user registration"""
    form = RegisterForm(request.form)
    #import pdb; pdb.set_trace()

    # if user is auth, redirect to index page
    if current_user.is_authenticated:
        flash("Please logout to register a new account")
        return redirect(url_for('main.index'))


    # validate_on_submit returns false if GET request
    # also checks form field validators
    if form.validate_on_submit():
        username_taken = User.query.filter_by(username=str(form.username.data)).first()
        email_taken = User.query.filter_by(email=str(form.email.data)).first()


        if not username_taken and not email_taken:
            flash("Success!")
            user = User(username=str(form.username), email=str(form.email))
            user.set_password(str(form.password.data))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('main.index'))

        if username_taken:
            flash("Sorry, that username is already taken!")
        if email_taken:
            flash("Sorry, that email is already taken!")
    return render_template('register.html')


# Login required routes
@login_required
@auth.route("/logout/")
def logout():
    return render_template("logout.html")


