from datetime import datetime
from app import db


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.BigInteger, primary_key=True)
    role_name = db.Column(db.String(255), nullable=False)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.BigInteger, primary_key=True)
    role_id = db.Column(db.BigInteger, db.ForeignKey("roles.id"), nullable=False, default=1)
    
    name = db.Column(db.String(255), nullable=False)
    second_name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.BigInteger, nullable=False)
    
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    role = db.relationship("Role", backref="users")
    valet = db.relationship('Valet', backref='owner', uselist=False)
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)


class Address(db.Model):
    __tablename__ = "adresses"
    id = db.Column(db.BigInteger, primary_key=True)
    city = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    post_index = db.Column(db.String(255), nullable=False)


class UserAddress(db.Model):
    __tablename__ = "user_adress"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    adress_id = db.Column(db.BigInteger, db.ForeignKey("adresses.id"), nullable=False)


class Currency(db.Model):
    __tablename__ = "currency"
    id = db.Column(db.BigInteger, primary_key=True)
    currency_name = db.Column(db.String(255), nullable=False)


class Valet(db.Model):
    __tablename__ = "valet"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    currency_id = db.Column(db.BigInteger, db.ForeignKey("currency.id"), nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0) # ДОБАВЛЕНО: для хранения денег


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.BigInteger, primary_key=True)
    buyer_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=True)
    status_id = db.Column(db.BigInteger, db.ForeignKey("status.id"), nullable=False)
    valet_id = db.Column(db.BigInteger, db.ForeignKey("valet.id"), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow) # ДОБАВЛЕНО: дата заказа


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
    price = db.Column(db.Numeric(10, 2), nullable=False) # ДОБАВЛЕНО: цена товара
    category_id = db.Column(db.BigInteger, db.ForeignKey("categories.id"), nullable=False)
    category = db.relationship("Category", backref="products")

class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.BigInteger, primary_key=True)
    items_id = db.Column(db.BigInteger, db.ForeignKey("products.id"), nullable=False)
    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.id"), nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False) # Исправлен тип на Numeric
    quantity = db.Column(db.BigInteger, nullable=False)
    
    product = db.relationship("Product") # ДОБАВЛЕНО: связь для получения имени товара
    order_ref = db.relationship("Order", backref="order_items") # ДОБАВЛЕНО: связь с заказом


class Wishlist(db.Model):
    __tablename__ = "wishlist"
    id = db.Column(db.BigInteger, primary_key=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)


class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.BigInteger, nullable=False)
    
    product = db.relationship("Product") # ДОБАВЛЕНО: чтобы видеть товар в корзине


class Review(db.Model):
    __tablename__ = "rewievs"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow) # Исправлено на DateTime для гибкости
    rating = db.Column(db.BigInteger, nullable=False)
    user = db.relationship("User", backref="reviews")

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