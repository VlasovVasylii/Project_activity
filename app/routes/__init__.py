from flask import Blueprint
from app.models import User
from app.extensions import login_manager


auth = Blueprint("auth", __name__)
main = Blueprint("main", __name__)
movie = Blueprint("movie", __name__)
show = Blueprint("show", __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
