import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True  

    YANDEX_API_BASE_URL = os.getenv(
        "YANDEX_API_BASE_URL",
        "https://cloud-api.yandex.net/v1/disk/resources"
    )
    YANDEX_OAUTH_TOKEN = os.getenv("YANDEX_OAUTH_TOKEN")

    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 5))