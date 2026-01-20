from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import bp
from ..extensions import db
from ..models import User

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        nickname = request.form.get("nickname", "").strip()
        password = request.form.get("password", "")

        if not email or not nickname or not password:
            flash("모든 항목을 입력해줘.")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("이미 가입된 이메일이야.")
            return redirect(url_for("auth.register"))

        user = User(email=email, nickname=nickname)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("main.choose_neighborhood"))

    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("이메일 또는 비밀번호가 올바르지 않아.")
            return redirect(url_for("auth.login"))

        login_user(user)
        # 동네 설정 안했으면 동네 선택으로
        if not user.primary_neighborhood_id():
            return redirect(url_for("main.choose_neighborhood"))
        return redirect(url_for("posts.list_posts"))

    return render_template("auth/login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))