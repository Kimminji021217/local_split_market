from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import bp
from ..extensions import db
from ..models import Neighborhood, UserNeighborhood

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
            rel = UserNeighborhood(user_id=current_user.id, neighborhood_id=int(nid), verify_status="SELF_DECLARED", is_primary=True)
            db.session.add(rel)
        else:
            rel.is_primary = True

        db.session.commit()
        return redirect(url_for("posts.list_posts"))

    return render_template("main/choose_neighborhood.html", neighborhoods=neighborhoods)