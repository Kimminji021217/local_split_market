from datetime import datetime, date
from .extensions import db
from .models import Post


def auto_close_posts():
    """마감시간 지난 모집글 자동 CLOSED 처리"""
    now = datetime.utcnow()

    posts = Post.query.filter(
        Post.status == "OPEN",
        Post.deadline.isnot(None),
        Post.deadline < now
    ).all()

    if not posts:
        return

    for post in posts:
        post.status = "CLOSED"

    db.session.commit()


def deadline_badge(deadline):
    """마감 D-Day 표시 문자열 반환"""
    if not deadline:
        return None

    today = date.today()
    dday = (deadline.date() - today).days

    if dday < 0:
        return "마감됨"
    elif dday == 0:
        return "오늘 마감"
    elif dday == 1:
        return "D-1"
    else:
        return f"D-{dday}"
