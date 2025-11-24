from flask import render_template, Blueprint

bp = Blueprint('routes', __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/forms/create/motorista")
def forms_motorista():
    return render_template("forms.html")

