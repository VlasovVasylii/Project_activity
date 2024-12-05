from app.models import Movie, Show, UserPreference
import boto3
from flask import current_app
import requests


def get_recommended_movies(user_id):
    user_pref = UserPreference.query.filter_by(user_id=user_id).first()
    if not user_pref:
        return Movie.query.order_by(Movie.external_rating.desc()).limit(10).all()

    genre_movies = Movie.query.filter(Movie.genre.ilike(f"%{user_pref.genre}%")).order_by(Movie.external_rating.desc()).limit(5).all()
    top_movies = Movie.query.order_by(Movie.external_rating.desc()).limit(5).all()
    return {movie.id: movie for movie in (genre_movies + top_movies)}.values()


def get_recommended_shows(user_id):
    user_pref = UserPreference.query.filter_by(user_id=user_id).first()
    if not user_pref:
        return Show.query.order_by(Show.external_rating.desc()).limit(10).all()

    genre_shows = Show.query.filter(Show.genre.ilike(f"%{user_pref.genre}%")).order_by(Show.external_rating.desc()).limit(5).all()
    top_shows = Show.query.order_by(Show.external_rating.desc()).limit(5).all()
    return {show.id: show for show in (genre_shows + top_shows)}.values()


def fetch_external_rating(title):
    # Пример с IMDb (замените на актуальный API)
    response = requests.get(f"https://api.example.com/rating?title={title}")
    if response.status_code == 200:
        data = response.json()
        return data.get("rating", 0)
    return 0


def upload_to_s3(file, folder_name):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=current_app.config["S3_ACCESS_KEY"],
        aws_secret_access_key=current_app.config["S3_SECRET_KEY"],
        region_name=current_app.config["S3_REGION"],
    )
    bucket = current_app.config["S3_BUCKET"]
    file_key = f"{folder_name}/{file.filename}"
    s3.upload_fileobj(file, bucket, file_key, ExtraArgs={"ACL": "public-read"})
    return f"{current_app.config['S3_BASE_URL']}{file_key}"
