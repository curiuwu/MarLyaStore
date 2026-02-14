#!/usr/bin/env python
"""
Script to recreate the database with all models including password_hash field
"""
from app import create_app, db

def recreate_database():
    app = create_app()
    
    with app.app_context():
        print("Удалении существующих таблиц...")
        db.drop_all()
        print("✓ Таблицы удалены")
        
        print("\nСоздание новых таблиц со структурой password_hash...")
        db.create_all()
        print("✓ Таблицы созданы")
        
        # Добавляем роли по умолчанию
        from app.models import Role
        
        roles_data = [
            {"id": 1, "role_name": "user"},  # Покупатель
            {"id": 2, "role_name": "seller"},  # Продавец
            {"id": 3, "role_name": "admin"},  # Администратор
        ]
        
        for role_data in roles_data:
            if not Role.query.filter_by(id=role_data["id"]).first():
                role = Role(**role_data)
                db.session.add(role)
        
        db.session.commit()
        print("✓ Роли добавлены по умолчанию")
        
        print("\n✅ База данных успешно пересоздана с полем password_hash!")
        print("\nТекущая структура таблицы Users:")
        print("- id (BigInteger, primary_key)")
        print("- role_id (BigInteger, foreign_key)")
        print("- name (String)")
        print("- second_name (String)")
        print("- age (BigInteger)")
        print("- email (String, unique)")
        print("- password_hash (String) ✓ ДОБАВЛЕНО")
        print("- created_at (DateTime)")
        print("- last_login (DateTime)")
        print("- is_active (Boolean)")
        print("\nДоступные роли:")
        print("- 1: Покупатель (user)")
        print("- 2: Продавец (seller)")
        print("- 3: Администратор (admin)")

if __name__ == '__main__':
    recreate_database()
