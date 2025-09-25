from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from app.logging_config import setup_logging
import logging
from app.routes.route_main import main_bp

setup_logging()
logger = logging.getLogger(__name__)


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(main_bp)

    db.init_app(app)
    register_commands(app)

    
    return app

def register_commands(app):
    @app.cli.command("init-db")
    def init_db():
        """Создать все таблицы (если их ещё нет)"""
        db.create_all()
        print("✅ База данных инициализирована")

from app import models