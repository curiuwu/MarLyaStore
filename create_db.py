from app import create_app, db
# Импортируй свои модели, чтобы SQLAlchemy их увидела
# Замени 'app.models' на путь к твоему файлу с моделями
from app.models import * # и остальные...

app = create_app()

with app.app_context():
    try:
        db.create_all()
        print("✅ Таблицы успешно созданы в PostgreSQL!")
    except Exception as e:
        print(f"❌ Ошибка при создании базы: {e}")