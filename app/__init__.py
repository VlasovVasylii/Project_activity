from flask import Flask
from app.extensions import db, login_manager
from app.routes.movie import movie
from app.routes.main import main
from app.routes.show import show
from app.routes.auth import auth


# Register
def register_routes(app):
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(main)
    app.register_blueprint(movie, url_prefix="/movie")
    app.register_blueprint(show, url_prefix="/show")


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Инициализация расширений
    db.init_app(app)
    with app.app_context():
        db.create_all()
    login_manager.init_app(app)

    # Регистрация маршрутов
    register_routes(app)

    return app