from flask import render_template, Blueprint

bp = Blueprint('routes', __name__)

@bp.route("/")
def index():
    return render_template("index.html")