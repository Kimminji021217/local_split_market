from flask import Blueprint

def create_app():
    app = Flask(__name__)
    app.jinja_env.globals["deadline_badge"] = deadline_badge

    return app

bp = Blueprint("posts", __name__, url_prefix="/posts")
