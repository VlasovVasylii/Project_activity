import os


class Config:
    SECRET_KEY = "supersecretkey"
    SQLALCHEMY_DATABASE_URI = "sqlite:///watching_show.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS S3 Configuration
    S3_BUCKET = os.environ.get("S3_BUCKET")
    S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
    S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
    S3_REGION = os.environ.get("S3_REGION") or "us-east-1"
    S3_BASE_URL = f"https://{S3_BUCKET}.s3.amazonaws.com/"

    # Flask-Login Remember Me
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 30  # 30 дней
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
