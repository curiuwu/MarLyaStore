from datetime import datetime
from app import db


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.BigInteger, primary_key=True)
    role_name = db.Column(db.String(255), nullable=False)


class User(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.BigInteger, primary_key=True)
    role_id = db.Column(db.BigInteger, db.ForeignKey("roles.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    second_name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.BigInteger, nullable=False)

    role = db.relationship("Role", backref="users")


class Address(db.Model):
    __tablename__ = "adresses"
    id = db.Column(db.BigInteger, primary_key=True)
    city = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    post_index = db.Column(db.String(255), nullable=False)


class UserAddress(db.Model):
    __tablename__ = "user_adress"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("Users.id"), nullable=False)
    adress_id = db.Column(db.BigInteger, db.ForeignKey("adresses.id"), nullable=False)


class Currency(db.Model):
    __tablename__ = "Currency"
    id = db.Column(db.BigInteger, primary_key=True)
    currency_name = db.Column(db.String(255), nullable=False)


class Valet(db.Model):
    __tablename__ = "valet"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("Users.id"), nullable=False)
    currency_id = db.Column(db.BigInteger, db.ForeignKey("Currency.id"), nullable=False)


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.BigInteger, primary_key=True)
    status_id = db.Column(db.BigInteger, db.ForeignKey("status.id"), nullable=False)
    valet_id = db.Column(db.BigInteger, db.ForeignKey("valet.id"), nullable=False)


class Status(db.Model):
    __tablename__ = "status"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class OrderStatus(db.Model):
    __tablename__ = "order_status"
    id = db.Column(db.BigInteger, primary_key=True)
    status_id = db.Column(db.BigInteger, db.ForeignKey("status.id"), nullable=False)
    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.id"), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False)


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.BigInteger, db.ForeignKey("categories.id"), nullable=False)


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.BigInteger, primary_key=True)
    items_id = db.Column(db.BigInteger, db.ForeignKey("products.id"), nullable=False)
    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.id"), nullable=False)
    price_at_purchase = db.Column(db.BigInteger, nullable=False)
    quantity = db.Column(db.BigInteger, nullable=False)


class Wishlist(db.Model):
    __tablename__ = "wishlist"
    id = db.Column(db.BigInteger, primary_key=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey("Users.id"), nullable=False)


class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("Users.id"), nullable=False)
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.BigInteger, nullable=False)


class Review(db.Model):
    __tablename__ = "rewievs"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("Users.id"), nullable=False)
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    rating = db.Column(db.BigInteger, nullable=False)


class ProductImage(db.Model):
    __tablename__ = "product_images"
    image_id = db.Column(db.BigInteger, primary_key=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id"), nullable=False)
    url = db.Column(db.String(255))


class Discount(db.Model):
    __tablename__ = "discounts"
    discount_id = db.Column(db.BigInteger, primary_key=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id"), nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)