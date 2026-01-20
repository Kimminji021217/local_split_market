from datetime import datetime
from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from . import bp
from ..extensions import db
from ..models import Post, JoinRequest


@bp.route("/")
@login_required
def list_posts():
    nid = current_user.primary_neighborhood_id()
    if not nid:
        return redirect(url_for("main.choose_neighborhood"))

    posts = Post.query.filter_by(neighborhood_id=nid).order_by(Post.created_at.desc()).all()
    return render_template("posts/list.html", posts=posts)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create_post():
    nid = current_user.primary_neighborhood_id()
    if not nid:
        return redirect(url_for("main.choose_neighborhood"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        item_name = request.form.get("item_name", "").strip()
        total_qty = request.form.get("total_qty", "").strip()
        unit_qty = request.form.get("unit_qty", "").strip()
        deadline_str = request.form.get("deadline", "").strip()  # "YYYY-MM-DDTHH:MM"
        pickup_place = request.form.get("pickup_place", "").strip()

        if not title or not item_name or not total_qty or not unit_qty:
            flash("제목/품목/총량/1몫은 필수야.")
            return redirect(url_for("posts.create_post"))

        try:
            total_qty_f = float(total_qty)
            unit_qty_f = float(unit_qty)
            if total_qty_f <= 0 or unit_qty_f <= 0:
                raise ValueError
        except ValueError:
            flash("총량/1몫은 0보다 큰 숫자여야 해.")
            return redirect(url_for("posts.create_post"))

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                flash("마감시간 형식이 올바르지 않아.")
                return redirect(url_for("posts.create_post"))

        post = Post(
            author_id=current_user.id,
            neighborhood_id=nid,
            title=title,
            item_name=item_name,
            total_qty=total_qty_f,
            unit_qty=unit_qty_f,
            deadline=deadline,
            pickup_place=pickup_place or None,
            status="OPEN",
        )
        db.session.add(post)
        db.session.commit()

        return redirect(url_for("posts.detail_post", post_id=post.id))

    return render_template("posts/new.html")


@bp.route("/<int:post_id>")
@login_required
def detail_post(post_id: int):
    nid = current_user.primary_neighborhood_id()
    if not nid:
        return redirect(url_for("main.choose_neighborhood"))

    post = Post.query.get_or_404(post_id)
    if post.neighborhood_id != nid:
        abort(403)

    is_author = (post.author_id == current_user.id)

    joins = JoinRequest.query.filter_by(post_id=post.id, status="ACTIVE").all()
    joined_qty = sum(j.qty for j in joins)
    remaining_qty = max(0.0, post.total_qty - joined_qty)

    my_join = JoinRequest.query.filter_by(post_id=post.id, user_id=current_user.id).first()

    # 남은 몫 계산(표시용)
    remaining_shares = int(remaining_qty // post.unit_qty) if post.unit_qty > 0 else 0

    return render_template(
        "posts/detail.html",
        post=post,
        is_author=is_author,
        joins=joins,
        joined_qty=joined_qty,
        remaining_qty=remaining_qty,
        remaining_shares=remaining_shares,
        my_join=my_join,
    )


@bp.route("/<int:post_id>/close", methods=["POST"])
@login_required
def close_post(post_id: int):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        abort(403)

    post.status = "CLOSED"
    db.session.commit()
    flash("모집을 마감했어.")
    return redirect(url_for("posts.detail_post", post_id=post.id))


@bp.route("/<int:post_id>/join", methods=["POST"])
@login_required
def join_post(post_id: int):
    post = Post.query.get_or_404(post_id)

    nid = current_user.primary_neighborhood_id()
    if not nid or post.neighborhood_id != nid:
        abort(403)

    if post.status != "OPEN":
        flash("모집이 마감된 글이야.")
        return redirect(url_for("posts.detail_post", post_id=post.id))

    # ✅ 몫 단위 입력
    shares_str = request.form.get("shares", "").strip()
    try:
        shares = int(shares_str)
        if shares <= 0:
            raise ValueError
    except ValueError:
        flash("참여 몫은 1 이상의 정수여야 해.")
        return redirect(url_for("posts.detail_post", post_id=post.id))

    qty = shares * post.unit_qty  # DB에는 실제 수량으로 저장

    # 현재 참여량(내 것 포함한 상태)
    joins = JoinRequest.query.filter_by(post_id=post.id, status="ACTIVE").all()
    joined_qty = sum(j.qty for j in joins)

    my_join = JoinRequest.query.filter_by(post_id=post.id, user_id=current_user.id).first()
    my_active_qty = (my_join.qty if (my_join and my_join.status == "ACTIVE") else 0.0)

    # 내 기존 참여량은 빼고 남은 수량 계산
    effective_joined = joined_qty - my_active_qty
    effective_remaining = post.total_qty - effective_joined

    if qty > effective_remaining + 1e-9:
        remaining_shares = int(max(0.0, effective_remaining) // post.unit_qty) if post.unit_qty > 0 else 0
        flash(f"남은 몫이 부족해. (남은 몫: {remaining_shares})")
        return redirect(url_for("posts.detail_post", post_id=post.id))

    if not my_join:
        my_join = JoinRequest(post_id=post.id, user_id=current_user.id, qty=qty, status="ACTIVE")
        db.session.add(my_join)
    else:
        my_join.qty = qty
        my_join.status = "ACTIVE"

    db.session.commit()
    flash("참여 신청 완료!")
    return redirect(url_for("posts.detail_post", post_id=post.id))


@bp.route("/<int:post_id>/cancel", methods=["POST"])
@login_required
def cancel_join(post_id: int):
    post = Post.query.get_or_404(post_id)

    nid = current_user.primary_neighborhood_id()
    if not nid or post.neighborhood_id != nid:
        abort(403)

    my_join = JoinRequest.query.filter_by(post_id=post.id, user_id=current_user.id).first()
    if not my_join or my_join.status != "ACTIVE":
        flash("취소할 참여가 없어.")
        return redirect(url_for("posts.detail_post", post_id=post.id))

    my_join.status = "CANCELED"
    db.session.commit()
    flash("참여를 취소했어.")
    return redirect(url_for("posts.detail_post", post_id=post.id))
