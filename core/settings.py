import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = not DEBUG