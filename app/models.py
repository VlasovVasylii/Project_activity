from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    watch_history = db.relationship("WatchHistory", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    genre = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    thumbnail_url = db.Column(db.String(250), nullable=False)
    video_url = db.Column(db.String(250), nullable=False)
    external_rating = db.Column(db.Float, default=0)

    @property
    def average_rating(self):
        user_rating_avg = (
                db.session.query(db.func.avg(Rating.rating))
                .filter(Rating.movie_id == self.id)
                .scalar() or 0
        )
        return round((user_rating_avg + self.external_rating) / 2, 1)


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    genre = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    thumbnail_url = db.Column(db.String(250), nullable=False)
    external_rating = db.Column(db.Float, default=0)
    seasons = db.relationship('Season', backref='show', lazy=True)

    @property
    def average_rating(self):
        user_rating_avg = (
                db.session.query(db.func.avg(Rating.rating))
                .filter(Rating.show_id == self.id)
                .scalar() or 0
        )
        return round((user_rating_avg + self.external_rating) / 2, 1)


class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season_number = db.Column(db.Integer, nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    episodes = db.relationship('Episode', backref='season', lazy=True)


class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    episode_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    video_url = db.Column(db.String(250), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    movie_id = db.Column(
        db.Integer, db.ForeignKey("movie.id"), nullable=True
    )  # Для фильмов
    show_id = db.Column(
        db.Integer, db.ForeignKey("show.id"), nullable=True
    )  # Для сериалов

    user = db.relationship("User", backref="comments", lazy=True)
    movie = db.relationship("Movie", backref="comments", lazy=True)
    show = db.relationship("Show", backref="comments", lazy=True)


class WatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=True)
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"), nullable=True)
    watched_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    genre = db.Column(db.String(100), nullable=True)  # Любимый жанр
    last_watched_movie = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=True)
    last_watched_show = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=True)

    user = db.relationship('User', backref='preferences', lazy=True)
    last_movie = db.relationship('Movie', foreign_keys=[last_watched_movie])
    last_show = db.relationship('Show', foreign_keys=[last_watched_show])