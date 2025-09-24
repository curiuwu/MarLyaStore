from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

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