from app.models import Movie, Show, UserPreference
import boto3
from flask import current_app
import os
from werkzeug.utils import secure_filename
import requests


def save_video(file, content_type, season=None):
    """
    Сохраняет видео на локальный сервер в соответствующую директорию.

    :param file: Загружаемый файл
    :param content_type: Тип контента ('movie' или 'show')
    :param season: Номер сезона (только для сериалов)
    :return: Путь к сохранённому файлу
    """
    base_path = os.path.join(current_app.root_path, 'static/videos')

    if content_type == 'movie':
        save_path = os.path.join(base_path, 'movies')
    elif content_type == 'show' and season:
        save_path = os.path.join(base_path, 'shows', f'season_{season}')
    else:
        raise ValueError("Invalid content type or missing season for shows")

    os.makedirs(save_path, exist_ok=True)
    filename = secure_filename(file.filename)
    file_path = os.path.join(save_path, filename)
    file.save(file_path)
    return file_path


def get_video_path(content_type, title, season=None):
    """
    Генерирует путь к видео на локальном сервере.

    :param content_type: Тип контента ('movie' или 'show')
    :param title: Название видео
    :param season: Номер сезона (только для сериалов)
    :return: Путь к видеофайлу
    """
    base_path = os.path.join(current_app.root_path, 'static/videos')

    if content_type == 'movie':
        return os.path.join(base_path, 'movies', f"{title}.mp4")
    elif content_type == 'show' and season:
        return os.path.join(base_path, 'shows', f"season_{season}", f"{title}.mp4")
    else:
        raise ValueError("Invalid content type or missing season for shows")



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
