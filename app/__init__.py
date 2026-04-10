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
    
    @app.context_processor
    def utility_processor():
        from app.models import Category  # Импорт внутри, чтобы избежать ошибок
        def get_cat_name(cat_id):
            # Используем session.get, так как query.get считается устаревшим в новых версиях, 
            # но query.get(cat_id) тоже сработает
            category = db.session.get(Category, cat_id) 
            return category.name if category else f"ID {cat_id} не найден"
        return dict(get_cat_name=get_cat_name)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Импорт и регистрация ВСЕХ blueprint
    from app.routes.route_main import main_bp
    from app.routes.auth_register import auth_register_bp
    from app.routes.auth_login import auth_login_bp
    from app.routes.auth_profile import auth_profile_bp
    from app.routes.products import products_bp
    from app.routes.admin_routes import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_register_bp)
    app.register_blueprint(auth_login_bp)
    app.register_blueprint(auth_profile_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(admin_bp)
    
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
    
    @app.cli.command("seed-db")
    def seed_db():
        """Заполнить базу демонстрационными данными"""
        from seed_db import seed_database
        seed_database()
    
    @app.cli.command("create-admin")
    def create_admin():
        """Создать администратора через CLI"""
        from app.models import User, Role
        
        # Проверяем или создаём роль admin
        admin_role = Role.query.filter_by(role_name='admin').first()
        if not admin_role:
            admin_role = Role(role_name='admin')
            db.session.add(admin_role)
            db.session.commit()
            print("✅ Роль 'admin' создана")
        
        while True:
            email = input("Email администратора: ").strip()
            
            if not email or '@' not in email:
                print("❌ Email должен быть валидным и содержать @")
                continue
            
            # Проверяем, нет ли уже такого пользователя
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                print(f"❌ Пользователь с email {email} уже существует")
                continue
            
            break
        
        while True:
            password = input("Пароль (минимум 6 символов): ").strip()
            if len(password) < 6:
                print("❌ Пароль должен быть не менее 6 символов")
                continue
            break
        
        name = input("Имя: ").strip()
        if not name:
            print("❌ Имя не может быть пустым")
            return
        
        second_name = input("Фамилия: ").strip()
        if not second_name:
            print("❌ Фамилия не может быть пустой")
            return
        
        try:
            admin = User(
                email=email,
                name=name,
                second_name=second_name,
                age=18,
                role_id=admin_role.id,
                is_active=True
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Администратор '{name} {second_name}' ({email}) успешно создан")
            print(f"📧 Email: {email}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Ошибка при создании администратора: {str(e)}")
            logger.error(f"Ошибка create-admin: {str(e)}")

from app import models