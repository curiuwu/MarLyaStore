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
from datetime import datetime, date
import random

def seed_database():
    app = create_app()

    with app.app_context():
        print("🌱 Начинаем заполнение базы демонстрационными данными...")

        # Проверяем, есть ли уже данные
        if Product.query.first():
            print("⚠️  База данных уже содержит товары. Пропускаем заполнение.")
            return

        # Создаем валюту
        if not Currency.query.first():
            ruble = Currency(currency_name="RUB")
            db.session.add(ruble)
            db.session.commit()
            print("✓ Валюта создана")

        # Создаем статусы заказов
        statuses = ["Оформлен", "Подтвержден", "В пути", "Доставлен", "Отменен"]
        for status_name in statuses:
            if not Status.query.filter_by(name=status_name).first():
                status = Status(name=status_name)
                db.session.add(status)
        db.session.commit()
        print("✓ Статусы заказов созданы")

        # Создаем категории
        categories_data = [
            "Электроника", "Одежда", "Обувь", "Дом и сад", "Косметика",
            "Спорт", "Книги", "Игрушки", "Автотовары", "Здоровье"
        ]
        categories = []
        for cat_name in categories_data:
            category = Category(name=cat_name)
            db.session.add(category)
            categories.append(category)
        db.session.commit()
        print("✓ Категории созданы")

        # Создаем продавцов
        sellers = []
        seller_names = [
            ("Иван", "Петров"), ("Мария", "Сидорова"), ("Алексей", "Кузнецов"),
            ("Елена", "Васильева"), ("Дмитрий", "Морозов")
        ]

        for first_name, last_name in seller_names:
            # Создаем пользователя
            user = User(
                role_id=2,  # seller
                name=first_name,
                second_name=last_name,
                age=random.randint(25, 50),
                email=f"{first_name.lower()}.{last_name.lower()}@marlya.com",
                created_at=datetime.utcnow(),
                is_active=True
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.flush()  # Получаем ID

            # Создаем валет для продавца
            valet = Valet(user_id=user.id, currency_id=1)
            db.session.add(valet)
            sellers.append((user, valet))

        db.session.commit()
        print("✓ Продавцы созданы")

        # Создаем товары
        products_data = [
            # Электроника
            ("iPhone 15 Pro", "Флагманский смартфон Apple с продвинутой камерой", 120000, 0),
            ("Samsung Galaxy S24", "Мощный Android-смартфон с AMOLED дисплеем", 90000, 0),
            ("MacBook Air M3", "Легкий ноутбук Apple с чипом M3", 150000, 0),
            ("Sony WH-1000XM5", "Беспроводные наушники с активным шумоподавлением", 35000, 0),

            # Одежда
            ("Куртка зимняя", "Теплая зимняя куртка с натуральным мехом", 25000, 1),
            ("Джинсы Levi's", "Классические джинсы от Levi's 501", 8000, 1),
            ("Платье вечернее", "Элегантное платье для особых случаев", 15000, 1),
            ("Футболка хлопковая", "Удобная хлопковая футболка на каждый день", 2000, 1),

            # Обувь
            ("Кроссовки Nike Air", "Спортивные кроссовки с амортизацией", 12000, 2),
            ("Ботинки зимние", "Утепленные ботинки для холодной погоды", 8000, 2),
            ("Туфли классические", "Черные кожаные туфли для деловых встреч", 15000, 2),

            # Дом и сад
            ("Кофемашина", "Автоматическая кофемашина с капучинатором", 45000, 3),
            ("Пылесос робот", "Робот-пылесос с навигацией", 35000, 3),
            ("Набор посуды", "Комплект кухонной посуды из нержавеющей стали", 12000, 3),

            # Косметика
            ("Крем для лица", "Увлажняющий крем с гиалуроновой кислотой", 1500, 4),
            ("Тушь для ресниц", "Водостойкая тушь объемного эффекта", 800, 4),
            ("Парфюм Chanel", "Классический аромат Chanel №5", 25000, 4),
        ]

        products = []
        for name, desc, price, cat_idx in products_data:
            seller_idx = random.randint(0, len(sellers) - 1)
            seller_user, seller_valet = sellers[seller_idx]

            product = Product(
                name=name,
                description=desc,
                category_id=categories[cat_idx].id
            )
            db.session.add(product)
            products.append((product, seller_valet, price))

        db.session.commit()
        print("✓ Товары созданы")

        # Создаем изображения для товаров (placeholders)
        image_urls = [
            "https://via.placeholder.com/400x400/FF6B9D/FFFFFF?text=Product+Image",
            "https://via.placeholder.com/400x400/4ECDC4/FFFFFF?text=No+Image",
            "https://via.placeholder.com/400x400/45B7D1/FFFFFF?text=Placeholder"
        ]

        for product, _, _ in products:
            # Добавляем 1-2 изображения на товар
            num_images = random.randint(1, 2)
            for _ in range(num_images):
                image = ProductImage(
                    product_id=product.id,
                    url=random.choice(image_urls)
                )
                db.session.add(image)

        db.session.commit()
        print("✓ Изображения товаров добавлены")

        # Создаем покупателей
        buyers = []
        buyer_names = [
            ("Анна", "Иванова"), ("Сергей", "Смирнов"), ("Ольга", "Попова"),
            ("Андрей", "Волков"), ("Наталья", "Соколова")
        ]

        for first_name, last_name in buyer_names:
            user = User(
                role_id=1,  # user
                name=first_name,
                second_name=last_name,
                age=random.randint(18, 65),
                email=f"{first_name.lower()}.{last_name.lower()}@example.com",
                created_at=datetime.utcnow(),
                is_active=True
            )
            user.set_password("password123")
            db.session.add(user)
            buyers.append(user)

        db.session.commit()
        print("✓ Покупатели созданы")

        # Создаем заказы и отзывы
        for buyer in buyers:
            # Каждый покупатель делает 2-4 заказа
            num_orders = random.randint(2, 4)
            for _ in range(num_orders):
                # Выбираем случайные товары для заказа
                order_products = random.sample(products, random.randint(1, 3))

                # Создаем заказ
                order = Order(
                    buyer_id=buyer.id,
                    status_id=random.randint(1, 5),  # Случайный статус
                    valet_id=order_products[0][1].id  # Валет первого товара
                )
                db.session.add(order)
                db.session.flush()

                # Создаем OrderStatus
                order_status = OrderStatus(
                    status_id=order.status_id,
                    order_id=order.id,
                    date=datetime.utcnow()
                )
                db.session.add(order_status)

                # Добавляем товары в заказ
                for product_tuple in order_products:
                    product, _, price = product_tuple
                    quantity = random.randint(1, 3)
                    order_item = OrderItem(
                        items_id=product.id,
                        order_id=order.id,
                        price_at_purchase=price,
                        quantity=quantity
                    )
                    db.session.add(order_item)

                    # С шансом 70% создаем отзыв
                    if random.random() < 0.7:
                        review = Review(
                            user_id=buyer.id,
                            product_id=product.id,
                            title=f"Отзыв о {product.name}",
                            comment=f"Хороший товар, рекомендую! Качество соответствует цене.",
                            date=date.today(),
                            rating=random.randint(3, 5)  # Положительные отзывы
                        )
                        db.session.add(review)

        db.session.commit()
        print("✓ Заказы и отзывы созданы")

        print("\n✅ Демонстрационные данные успешно добавлены!")
        print(f"📊 Статистика:")
        print(f"   Категорий: {len(categories)}")
        print(f"   Продавцов: {len(sellers)}")
        print(f"   Товаров: {len(products)}")
        print(f"   Покупателей: {len(buyers)}")
        print(f"   Отзывов: {Review.query.count()}")
        print("\n🔐 Данные для входа:")
        print("   Админ: admin@marlya.com / admin123")
        print("   Продавцы: [имя].[фамилия]@marlya.com / password123")
        print("   Покупатели: [имя].[фамилия]@example.com / password123")

if __name__ == "__main__":
    seed_database()