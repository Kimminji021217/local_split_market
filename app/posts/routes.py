from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from . import bp
from ..models import Post

@bp.route("/")
@login_required
def list_posts():
    nid = current_user.primary_neighborhood_id()
    if not nid:
        return redirect(url_for("main.choose_neighborhood"))

    posts = Post.query.filter_by(neighborhood_id=nid).order_by(Post.created_at.desc()).all()
    return render_template("posts/list.html", posts=posts)