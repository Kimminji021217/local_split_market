from flask import Flask
from .extensions import db, login_manager
from .models import User, Neighborhood

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key"  # 배포 때는 환경변수로 빼기
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    # Blueprint 등록
    from .auth.routes import bp as auth_bp
    from .main.routes import bp as main_bp
    from .posts.routes import bp as posts_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(posts_bp)

    # DB 생성 + 동네 더미 seed
    with app.app_context():
        db.create_all()
        seed_neighborhoods()

    return app

@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))

def seed_neighborhoods():
    # 이미 있으면 스킵
    if Neighborhood.query.count() > 0:
        return
    defaults = [
        Neighborhood(name="인천 연수구 송도동", region_code="INC-YS-SD"),
        Neighborhood(name="인천 남동구 구월동", region_code="INC-ND-GW"),
        Neighborhood(name="서울 마포구 합정동", region_code="SEO-MP-HJ"),
    ]
    db.session.add_all(defaults)
    db.session.commit()