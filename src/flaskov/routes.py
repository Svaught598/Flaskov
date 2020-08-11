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


# GET routes
@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/register/")
def register():
    return render_template("register.html")


# POST routes
@auth.route("/login/", methods=['POST'])
def login_post():

    # get data from request and find user corresponding to it
    username = request.form['username']
    password = request.form['password']
    remember = True if request.form['remember'] else False
    user = User.query.filter_by(username=username).first()

    # redirect if any information is not correct
    if not user:
        flash("Incorrect Username or Password")
        return redirect(url_for('auth.login'))
    elif not check_password_hash(user.password, password):
        flash("Incorrect Username or Password")
        return redirect(url_for('auth.login'))
    # if user exists, and pass is correct, login
    else:
        flash("Success!")
        login_user(user, remember=remember)
        #user.is_authenticated = True
        print(user.is_authenticated)
        return redirect(url_for('main.index'))


@auth.route("/register", methods=['POST'])
def register_post():

    # if user is authenticated, redirect with message
    if current_user.is_authenticated:
        flash("Please logout to register a new account")
        return redirect(url_for('main'))
    
    # get data from request see if any fields are not unique
    username = request.form['username']
    email = request.form['email']
    db.session.rollback()
    username_taken = User.query.filter_by(username=username).first() 
    email_taken = User.query.filter_by(email=email).first() 

    # if email or username are taken, redirect
    if username_taken:
        flash("Sorry, that username is already taken!")
        return redirect(url_for('auth.register'))
    if email_taken:
        flash("Sorry, that email is already taken!")
        return redirect(url_for('auth.register'))
    
    # If everything is correct, create new user
    hash_pass = generate_password_hash(request.form['password'])
    user = User(
        username = username,
        email = email,
        password = hash_pass,
    )
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('main.index'))


# Login required routes
@login_required
@auth.route("/logout/")
def logout():
    return render_template("logout.html")


