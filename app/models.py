from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    neighborhoods = db.relationship("UserNeighborhood", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, pw: str) -> None:
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw: str) -> bool:
        return check_password_hash(pw)

    def primary_neighborhood_id(self):
        rel = next((x for x in self.neighborhoods if x.is_primary), None)
        return rel.neighborhood_id if rel else None


class Neighborhood(db.Model):
    __tablename__ = "neighborhoods"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    region_code = db.Column(db.String(50), nullable=True)

    users = db.relationship("UserNeighborhood", back_populates="neighborhood")


class UserNeighborhood(db.Model):
    __tablename__ = "user_neighborhoods"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    neighborhood_id = db.Column(db.Integer, db.ForeignKey("neighborhoods.id"), primary_key=True)

    verify_status = db.Column(db.String(20), default="SELF_DECLARED", nullable=False)  # SELF_DECLARED/PENDING/VERIFIED
    is_primary = db.Column(db.Boolean, default=True, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="neighborhoods")
    neighborhood = db.relationship("Neighborhood", back_populates="users")


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    neighborhood_id = db.Column(db.Integer, db.ForeignKey("neighborhoods.id"), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)

    total_qty = db.Column(db.Float, nullable=False)   # 총량(kg 등)
    unit_qty = db.Column(db.Float, nullable=False)    # 1몫 단위(kg 등)
    deadline = db.Column(db.DateTime, nullable=True)

    pickup_place = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default="OPEN", nullable=False)  # OPEN/CLOSED

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class JoinRequest(db.Model):
    __tablename__ = "join_requests"
    id = db.Column(db.Integer, primary_key=True)

    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # DB에는 '실제 수량'만 저장 (몫 * unit_qty 로 계산한 값)
    qty = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="ACTIVE", nullable=False)  # ACTIVE/CANCELED

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("post_id", "user_id", name="uq_join_post_user"),
    )
