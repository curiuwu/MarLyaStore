#!/usr/bin/env python
"""
Script to populate the database with demo data
"""
from app import create_app, db
from app.models import (
    Role, User, Address, UserAddress, Currency, Valet, Order, Status,
    OrderStatus, Category, Product, OrderItem, Wishlist, Cart, Review,
    ProductImage, Discount
)
from datetime import datetime
import random
from decimal import Decimal

def seed_database():
    app = create_app()

    with app.app_context():
        print("🌱 Начинаем заполнение базы демонстрационными данными...")

        # 1. Роли (Сначала роли, так как User на них ссылается)
        if not Role.query.first():
            print("--- Создаем роли...")
            db.session.add_all([
                Role(id=1, role_name="User"),
                Role(id=2, role_name="Seller"),
                Role(id=3, role_name="Admin")
            ])
            db.session.commit()

        # 2. Валюта
        ruble = Currency.query.filter_by(currency_name="RUB").first()
        if not ruble:
            print("--- Создаем валюту...")
            ruble = Currency(currency_name="RUB")
            db.session.add(ruble)
            db.session.commit()

        # 3. Статусы
        if not Status.query.first():
            print("--- Создаем статусы...")
            statuses_names = ["Оформлен", "Подтвержден", "В пути", "Доставлен", "Отменен"]
            for idx, s_name in enumerate(statuses_names, 1):
                db.session.add(Status(id=idx, name=s_name))
            db.session.commit()

        # 4. Категории
        if not Category.query.first():
            print("--- Создаем категории...")
            categories_data = ["Электроника", "Одежда", "Обувь", "Дом и сад", "Косметика"]
            for idx, cat_name in enumerate(categories_data, 1):
                db.session.add(Category(id=idx, name=cat_name))
            db.session.commit()

        # Получаем актуальные категории из базы для ссылок
        db_categories = Category.query.all()

        # 5. Продавцы
        if not User.query.filter_by(role_id=2).first():
            print("--- Создаем продавцов...")
            seller_names = [("Иван", "Петров"), ("Мария", "Сидорова")]
            for f_name, l_name in seller_names:
                user = User(
                    role_id=2,
                    name=f_name, second_name=l_name,
                    age=random.randint(25, 50),
                    email=f"{f_name.lower()}.{l_name.lower()}@marlya.com",
                    is_active=True
                )
                user.set_password("password123")
                db.session.add(user)
                db.session.flush()
                
                # Создаем кошелек продавцу
                db.session.add(Valet(user_id=user.id, currency_id=ruble.id, balance=Decimal('0.00')))
            db.session.commit()

        # 6. Товары
        if not Product.query.first():
            print("--- Создаем товары...")
            products_info = [
                ("iPhone 15 Pro", "Флагманский смартфон Apple", 120000, 0),
                ("Samsung Galaxy S24", "Мощный Android-смартфон", 90000, 0),
                ("MacBook Air M3", "Легкий ноутбук Apple", 150000, 0),
                ("Sony WH-1000XM5", "Беспроводные наушники", 35000, 0),
                ("Куртка зимняя", "Теплая куртка", 25000, 1),
                ("Джинсы Levi's", "Классические джинсы", 8000, 1),
                ("Кроссовки Nike Air", "Спортивные кроссовки", 12000, 2),
                ("Кофемашина", "Автоматическая кофемашина", 45000, 3)
            ]

            for name, desc, price, cat_idx in products_info:
                product = Product(
                    name=name,
                    description=desc,
                    price=Decimal(str(price)),
                    category_id=db_categories[cat_idx].id
                )
                db.session.add(product)
            db.session.commit()

        # 7. Покупатели (Те, кто будут "дюпать")
        if not User.query.filter_by(role_id=1).first():
            print("--- Создаем покупателей...")
            buyer_names = [("Анна", "Иванова"), ("Сергей", "Смирнов")]
            for f_name, l_name in buyer_names:
                user = User(
                    role_id=1,
                    name=f_name, second_name=l_name,
                    age=random.randint(18, 65),
                    email=f"{f_name.lower()}.{l_name.lower()}@example.com"
                )
                user.set_password("password123")
                db.session.add(user)
                db.session.flush()
                
                # Дарим покупателю деньги на кошелек
                db.session.add(Valet(user_id=user.id, currency_id=ruble.id, balance=Decimal('100000.00')))
            db.session.commit()

        # 8. Генерация заказов для истории
        print("--- Генерируем историю заказов и отзывов...")
        all_buyers = User.query.filter_by(role_id=1).all()
        all_products = Product.query.all()
        all_statuses = Status.query.all()

        for buyer in all_buyers:
            if not Order.query.filter_by(buyer_id=buyer.id).first():
                b_valet = Valet.query.filter_by(user_id=buyer.id).first()
                
                order = Order(
                    buyer_id=buyer.id,
                    status_id=random.choice(all_statuses).id,
                    valet_id=b_valet.id,
                    date=datetime.utcnow()
                )
                db.session.add(order)
                db.session.flush()

                # Случайный товар в заказ
                prod = random.choice(all_products)
                item = OrderItem(
                    items_id=prod.id,
                    order_id=order.id,
                    price_at_purchase=prod.price,
                    quantity=random.randint(1, 2)
                )
                db.session.add(item)

                # Отзыв
                review = Review(
                    user_id=buyer.id,
                    product_id=prod.id,
                    title=f"Отзыв о {prod.name}",
                    comment="Все отлично, быстрая доставка!",
                    rating=5,
                    date=datetime.utcnow()
                )
                db.session.add(review)

        db.session.commit()
        print("✅ База полностью готова к работе!")

if __name__ == "__main__":
    seed_database()