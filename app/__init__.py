from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth_login.login_page'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Импорт и регистрация ВСЕХ blueprint
    from app.routes.route_main import main_bp
    from app.routes.auth_register import auth_register_bp
    from app.routes.auth_login import auth_login_bp
    from app.routes.auth_profile import auth_profile_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_register_bp)
    app.register_blueprint(auth_login_bp)
    app.register_blueprint(auth_profile_bp)
    
    register_commands(app)
    
    return app

def register_commands(app):
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        from app.models import Role
        if not Role.query.first():
            user_role = Role(role_name='user')
            db.session.add(user_role)
            db.session.commit()
            print("✅ Создана роль 'user'")
        print("✅ База данных инициализирована")
    
    @app.cli.command("create-admin")
    def create_admin():
        from app.models import User, Role
        admin_role = Role.query.filter_by(role_name='admin').first()
        if not admin_role:
            admin_role = Role(role_name='admin')
            db.session.add(admin_role)
            db.session.commit()
        
        email = input("Email администратора: ")
        password = input("Пароль: ")
        name = input("Имя: ")
        second_name = input("Фамилия: ")
        
        admin = User(
            email=email,
            name=name,
            second_name=second_name,
            age=99,
            role_id=admin_role.id,
            is_active=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Администратор {email} создан")

from app import models