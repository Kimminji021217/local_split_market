from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import bp
from ..extensions import db
from ..models import Neighborhood, UserNeighborhood, Post, JoinRequest


@bp.route("/")
def index():
    return redirect(url_for("posts.list_posts"))


@bp.route("/choose-neighborhood", methods=["GET", "POST"])
@login_required
def choose_neighborhood():
    neighborhoods = Neighborhood.query.all()

    if request.method == "POST":
        nid = request.form.get("neighborhood_id")
        if not nid:
            flash("동네를 선택해줘.")
            return redirect(url_for("main.choose_neighborhood"))

        # 기존 primary 해제
        for rel in current_user.neighborhoods:
            rel.is_primary = False

        # 관계 있으면 primary로, 없으면 생성
        rel = UserNeighborhood.query.filter_by(user_id=current_user.id, neighborhood_id=int(nid)).first()
        if not rel:
            rel = UserNeighborhood(
                user_id=current_user.id,
                neighborhood_id=int(nid),
                verify_status="SELF_DECLARED",
                is_primary=True,
            )
            db.session.add(rel)
        else:
            rel.is_primary = True

        db.session.commit()
        return redirect(url_for("posts.list_posts"))

    return render_template("main/choose_neighborhood.html", neighborhoods=neighborhoods)


@bp.route("/me/joins")
@login_required
def my_joins():
    """내가 ACTIVE로 참여 중인 모집글 목록"""
    joins = JoinRequest.query.filter_by(user_id=current_user.id, status="ACTIVE") \
                             .order_by(JoinRequest.created_at.desc()).all()

    post_ids = [j.post_id for j in joins]
    posts_by_id = {}
    if post_ids:
        posts = Post.query.filter(Post.id.in_(post_ids)).all()
        posts_by_id = {p.id: p for p in posts}

    return render_template("main/my_joins.html", joins=joins, posts_by_id=posts_by_id)


@bp.route("/me/posts")
@login_required
def my_posts():
    """내가 작성한 모집글 목록"""
    posts = Post.query.filter_by(author_id=current_user.id) \
                      .order_by(Post.created_at.desc()).all()
    return render_template("main/my_posts.html", posts=posts)
