from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Product, Category, Review, ProductImage, User, Valet, OrderItem, Order

products_bp = Blueprint("products", __name__, url_prefix="/products")

@products_bp.route('/')
def catalog():
    """Каталог товаров"""
    # Получаем параметры фильтрации
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 12

    query = Product.query

    # Фильтр по категории
    if category_id:
        query = query.filter(Product.category_id == category_id)

    # Поиск по названию или описанию
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )

    # Пагинация
    products = query.paginate(page=page, per_page=per_page, error_out=False)

    # Получаем все категории для фильтра
    categories = Category.query.all()

    # Для каждого товара получаем средний рейтинг и количество отзывов
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

    # Получаем продавца - пока что не реализовано, так как модель не имеет seller_id
    seller = None  # TODO: добавить поле seller_id в модель Product

    # Получаем изображения
    images = ProductImage.query.filter_by(product_id=product_id).all()

    # Получаем отзывы
    reviews = Review.query.filter_by(product_id=product_id).join(User).order_by(Review.date.desc()).all()

    # Статистика отзывов
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        review_count = len(reviews)
    else:
        avg_rating = 0
        review_count = 0

    # Проверяем, может ли пользователь оставить отзыв
    can_review = False
    if current_user.is_authenticated:
        # Проверяем, покупал ли пользователь этот товар
        has_purchased = db.session.query(OrderItem).join(Order).filter(
            Order.buyer_id == current_user.id,
            OrderItem.items_id == product_id
        ).first() is not None

        # Проверяем, не оставлял ли уже отзыв
        existing_review = Review.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()

        can_review = has_purchased and not existing_review

    return render_template('products/product_detail.html',
                         product=product,
                         seller=seller,
                         images=images,
                         reviews=reviews,
                         avg_rating=avg_rating,
                         review_count=review_count,
                         can_review=can_review)

@products_bp.route('/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    """Добавление отзыва"""
    product = Product.query.get_or_404(product_id)

    # Получаем данные из формы
    rating = request.form.get('rating', type=int)
    title = request.form.get('title', '').strip()
    comment = request.form.get('comment', '').strip()

    if not rating or rating < 1 or rating > 5:
        flash('Пожалуйста, укажите оценку от 1 до 5.', 'error')
        return redirect(url_for('products.product_detail', product_id=product_id))

    if not title or not comment:
        flash('Пожалуйста, заполните все поля отзыва.', 'error')
        return redirect(url_for('products.product_detail', product_id=product_id))

    # Создаем отзыв
    from datetime import date
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