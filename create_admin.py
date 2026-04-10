#!/usr/bin/env python
"""Скрипт для создания администратора минуя flask CLI"""

import sys
import os

# Добавляем корневую папку в path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Role

def create_admin():
    """Создать администратора"""
    app = create_app()
    
    with app.app_context():
        # Проверяем или создаём роль admin
        admin_role = Role.query.filter_by(role_name='admin').first()
        if not admin_role:
            admin_role = Role(role_name='admin')
            db.session.add(admin_role)
            db.session.commit()
            print("✅ Роль 'admin' создана")
        
        while True:
            email = input("\n📧 Email администратора: ").strip()
            
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
            password = input("🔐 Пароль (минимум 6 символов): ").strip()
            if len(password) < 6:
                print("❌ Пароль должен быть не менее 6 символов")
                continue
            break
        
        name = input("👤 Имя: ").strip()
        if not name:
            print("❌ Имя не может быть пустым")
            return
        
        second_name = input("👤 Фамилия: ").strip()
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
            print(f"\n✅ Администратор '{name} {second_name}' ({email}) успешно создан")
            print(f"📧 Email: {email}")
            print(f"🔐 Пароль: {'*' * len(password)}")
            print("\n🎉 Теперь вы можете войти в админ-панель на /auth/login")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Ошибка при создании администратора: {str(e)}")

if __name__ == '__main__':
    create_admin()
