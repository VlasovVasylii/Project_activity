from flask import Flask

import config
from app.extensions import db, login_manager
from app.routes.main import main
from app.routes.auth import auth


# Register
def register_routes(app):
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(main)


def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)

    # Инициализация расширений
    db.init_app(app)
    with app.app_context():
        db.create_all()
    login_manager.init_app(app)

    # Регистрация маршрутов
    register_routes(app)

    return app
