from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound


###############################################################
# Main Blueprint                                              #
###############################################################

main = Blueprint("main", __name__, template_folder="templates")

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/about/")
def about():
    try:
        return render_template("about.html")
    except TemplateNotFound:
        abort(404)

###############################################################
# Auth Blueprint                                              #
###############################################################

auth = Blueprint("auth", __name__, template_folder="templates")

@auth.route("/login/", methods=['POST'])
def login():
    return "login"

@auth.route("/register/")
def register():
    return "register"

@auth.route("/logout/")
def logout():
    return "logout"