from flask import Flask
from config import Config
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.yandexAPI import YandexDiskAPI
from dotenv import load_dotenv

load_dotenv()


db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
yandexClient = YandexDiskAPI(os.getenv('YANDEX_OAUTH_TOKEN'))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "routes.login"

    with app.app_context():
        from app import models

    from app.routes import routes_bp
    app.register_blueprint(routes_bp)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    return app

