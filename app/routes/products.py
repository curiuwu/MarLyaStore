from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Product, Category, Review, ProductImage, User, Valet, OrderItem, Order, Cart
from datetime import date, datetime
from decimal import Decimal

products_bp = Blueprint("products", __name__, url_prefix="/products")

@products_bp.route('/')
def catalog():
    """Каталог товаров"""
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 12

    query = Product.query

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )

    products = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.all()

    for product in products.items:
        reviews_stats = db.session.query(
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('review_count')
        ).filter(Review.product_id == product.id).first()

        product.avg_rating = reviews_stats.avg_rating or 0
        product.review_count = reviews_stats.review_count or 0

    return render_template('products/catalog.html',
                           products=products,
                           categories=categories,
                           selected_category=category_id,
                           search=search)

@products_bp.route('/<int:product_id>')
def product_detail(product_id):
    """Страница товара"""
    product = Product.query.get_or_404(product_id)
    images = ProductImage.query.filter_by(product_id=product_id).all()
    reviews = Review.query.filter_by(product_id=product_id).join(User).order_by(Review.date.desc()).all()

    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        review_count = len(reviews)
    else:
        avg_rating = 0
        review_count = 0

    can_review = False
    if current_user.is_authenticated:
        has_purchased = db.session.query(OrderItem).join(Order).filter(
            Order.buyer_id == current_user.id,
            OrderItem.items_id == product_id
        ).first() is not None

        existing_review = Review.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()
        can_review = has_purchased and not existing_review

    return render_template('products/product_detail.html',
                           product=product,
                           images=images,
                           reviews=reviews,
                           avg_rating=avg_rating,
                           review_count=review_count,
                           can_review=can_review)

@products_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Добавление товара в корзину"""
    product = Product.query.get_or_404(product_id)
    quantity = request.form.get('quantity', 1, type=int)

    if quantity < 1: quantity = 1

    item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = Cart(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(item)
    
    db.session.commit()
    flash(f'Товар {product.name} добавлен в корзину!', 'success')
    return redirect(url_for('products.product_detail', product_id=product_id))

@products_bp.route('/cart')
@login_required
def cart():
    """Страница корзины"""
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    # Приводим к Decimal, чтобы избежать float-ошибок
    total_price = sum(Decimal(str(item.product.price)) * item.quantity for item in cart_items)
    
    valet = Valet.query.filter_by(user_id=current_user.id).first()
    balance = valet.balance if valet else Decimal('0.00')
    
    return render_template('products/cart.html', 
                           items=cart_items, 
                           total_price=total_price, 
                           balance=balance)

@products_bp.route('/cart/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    """Удаление из корзины"""
    item = Cart.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('products.cart'))

@products_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return redirect(url_for('products.cart'))

    # Считаем итоговую сумму
    total_cost = sum(Decimal(str(item.product.price)) * item.quantity for item in cart_items)
    
    # Получаем кошелек
    wallet = Valet.query.filter_by(user_id=current_user.id).first()
    
    if not wallet or wallet.balance < total_cost:
        flash('Недостаточно средств!', 'error')
        return redirect(url_for('products.cart'))

    try:
        # 1. Списываем деньги
        wallet.balance -= total_cost

        # 2. Создаем ЗАКАЗ
        # Проверь, чтобы названия полей (buyer_id, valet_id) совпадали с твоим models.py!
        new_order = Order(
            buyer_id=current_user.id,
            valet_id=wallet.id,
            status_id=1,  # Убедись, что статус с ID 1 существует в таблице статусов!
            date=datetime.now()
        )
        db.session.add(new_order)
        db.session.flush() # Получаем ID заказа для items

        # 3. Создаем ЭЛЕМЕНТЫ ЗАКАЗА
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=new_order.id,
                items_id=cart_item.product_id,
                # ЗАМЕНИТЕ count на то имя, которое у вас в модели OrderItem (вероятно quantity)
                quantity=cart_item.quantity, 
                price_at_purchase=cart_item.product.price
            )
            db.session.add(order_item)
            db.session.delete(cart_item) # Очищаем корзину

        db.session.commit()
        flash(f'Заказ успешно оформлен!', 'success')
        return redirect(url_for('auth_profile.profile_orders'))

    except Exception as e:
        db.session.rollback()
        # ВАЖНО: Посмотри в консоль PyCharm после ошибки, там будет точная причина!
        print("-" * 30)
        print(f"КРИТИЧЕСКАЯ ОШИБКА БАЗЫ: {str(e)}")
        print("-" * 30)
        flash(f'Ошибка при сохранении заказа: {str(e)[:50]}...', 'error')
        return redirect(url_for('products.cart'))

@products_bp.route('/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    """Добавление отзыва"""
    product = Product.query.get_or_404(product_id)
    rating = request.form.get('rating', type=int)
    title = request.form.get('title', '').strip()
    comment = request.form.get('comment', '').strip()

    if not rating or rating < 1 or rating > 5:
        flash('Пожалуйста, укажите оценку от 1 до 5.', 'error')
        return redirect(url_for('products.product_detail', product_id=product_id))

    review = Review(
        user_id=current_user.id,
        product_id=product_id,
        title=title,
        comment=comment,
        rating=rating,
        date=date.today()
    )

    db.session.add(review)
    db.session.commit()

    flash('Ваш отзыв успешно добавлен!', 'success')
    return redirect(url_for('products.product_detail', product_id=product_id))