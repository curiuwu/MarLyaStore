from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.analytics import AnalyticsService
from app.models import Category, Currency, Order, Product, ProductImage, Status, Valet
from app import db
from app.role_utils import get_user_role_name
from app.helpers import role_required
from decimal import Decimal, InvalidOperation
auth_profile_bp = Blueprint("auth_profile", __name__, url_prefix="/auth")

MONEY_QUANT = Decimal("0.01")
MAX_TOP_UP_AMOUNT = Decimal("1000000.00")


def _money(value):
    return Decimal(str(value or "0.00")).quantize(MONEY_QUANT)


def _order_total(order):
    return sum(
        _money(item.price_at_purchase) * int(item.quantity)
        for item in order.order_items
    ).quantize(MONEY_QUANT)


def _order_status_name(order):
    status = db.session.get(Status, order.status_id) if order.status_id else None
    return status.name if status else "N/A"


def _order_view(order):
    return {
        "id": order.id,
        "date": order.date,
        "status": _order_status_name(order),
        "items": [
            {
                "name": item.product.name if item.product else f"Товар #{item.items_id}",
                "quantity": item.quantity,
                "price": _money(item.price_at_purchase),
                "total": (_money(item.price_at_purchase) * int(item.quantity)).quantize(MONEY_QUANT),
            }
            for item in order.order_items
        ],
        "total": _order_total(order),
    }


def _buyer_order_views(user_id, limit=None):
    query = Order.query.filter_by(buyer_id=user_id).order_by(Order.date.desc())
    if limit:
        query = query.limit(limit)
    return [_order_view(order) for order in query.all()]

@auth_profile_bp.route("/profile")
@login_required
def profile():
    # Получаем роль пользователя
    user_role = get_user_role_name(current_user) or "user"
    
    # Вычисляем общую статистику для профиля
    profile_stats = {
        'wishlist_count': AnalyticsService.get_user_wishlist_count(current_user.id),
        'active_orders_count': AnalyticsService.get_user_active_orders_count(current_user.id),
        'rating': AnalyticsService.get_user_rating(current_user.id),
        'bonuses': AnalyticsService.get_user_bonuses(current_user.id),
    }
    
    if user_role == "admin":
        return render_template("auth/profile_admin.html", user=current_user, profile_stats=profile_stats)
    elif user_role == "seller":
        return render_template("auth/profile_seller.html", user=current_user, profile_stats=profile_stats)
    else:  # user/customer
        return render_template(
            "auth/profile_customer.html",
            user=current_user,
            profile_stats=profile_stats,
            recent_orders=_buyer_order_views(current_user.id, limit=3),
            balance=_money(current_user.valet.balance if current_user.valet else 0),
        )


@auth_profile_bp.route("/profile/wishlist")
@login_required
def profile_wishlist():
    """Страница с избранным"""
    return render_template("auth/profile_wishlist.html", user=current_user)

@auth_profile_bp.route("/profile/settings")
@login_required
def profile_settings():
    """Настройки профиля"""
    return render_template("auth/profile_settings.html", user=current_user)

@auth_profile_bp.route("/profile/addresses")
@login_required
def profile_addresses():
    """Страница с адресами доставки"""
    return render_template("auth/profile_addresses.html", user=current_user)


# ===== API ROUTES ДЛЯ АНАЛИТИКИ =====

@auth_profile_bp.route("/api/seller/stats", methods=["GET"])
@login_required
def api_seller_stats():
    """JSON API для статистики продавца"""
    user_role = get_user_role_name(current_user) or "user"
    if user_role != "seller":
        return jsonify({"error": "Unauthorized"}), 403
    
    period = request.args.get('period', '30d')
    
    stats = {
        'orders_count': AnalyticsService.seller_orders_count(current_user.id, period),
        'revenue': AnalyticsService.seller_revenue(current_user.id, period),
        'avg_check': AnalyticsService.seller_avg_check(current_user.id, period),
        'top_products': AnalyticsService.seller_top_products(current_user.id, period),
        'top_categories': AnalyticsService.seller_top_categories(current_user.id, period),
        'orders_by_status': AnalyticsService.seller_orders_by_status(current_user.id, period),
    }
    
    return jsonify(stats)


@auth_profile_bp.route("/api/admin/stats", methods=["GET"])
@login_required
def api_admin_stats():
    """JSON API для статистики администратора"""
    user_role = get_user_role_name(current_user) or "user"
    if user_role != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    period = request.args.get('period', '30d')
    
    stats = {
        'total_orders': AnalyticsService.admin_total_orders(period),
        'total_gmv': AnalyticsService.admin_total_gmv(period),
        'total_buyers': AnalyticsService.admin_total_buyers(period),
        'total_sellers': AnalyticsService.admin_total_sellers(),
        'top_categories': AnalyticsService.admin_top_categories(period),
        'top_sellers': AnalyticsService.admin_top_sellers(period),
        'orders_by_status': AnalyticsService.admin_orders_by_status(period),
        'new_users': AnalyticsService.admin_new_users(period),
    }
    
    return jsonify(stats)

@auth_profile_bp.route('/dupe-balance', methods=['POST'])
@login_required
def dupe_balance():
    flash('Демо-пополнение заменено формой пополнения в кабинете покупателя', 'info')
    return redirect(request.referrer or url_for('auth_profile.profile'))


@auth_profile_bp.route('/profile/balance/top-up', methods=['POST'])
@login_required
def top_up_balance():
    user_role = get_user_role_name(current_user) or "user"
    if user_role not in ["user", "customer"]:
        flash('Пополнение баланса доступно только покупателю', 'danger')
        return redirect(url_for('auth_profile.profile'))

    amount_raw = request.form.get('amount', '').strip().replace(',', '.')

    try:
        amount = Decimal(amount_raw).quantize(MONEY_QUANT)
    except (InvalidOperation, ValueError):
        flash('Введите корректную сумму пополнения', 'danger')
        return redirect(url_for('auth_profile.profile'))

    if amount <= 0:
        flash('Сумма пополнения должна быть больше нуля', 'danger')
        return redirect(url_for('auth_profile.profile'))

    if amount > MAX_TOP_UP_AMOUNT:
        flash('Сумма пополнения слишком большая', 'danger')
        return redirect(url_for('auth_profile.profile'))

    try:
        wallet = current_user.valet or Valet.query.filter_by(user_id=current_user.id).first()

        if not wallet:
            rub = Currency.query.filter_by(currency_name="RUB").first()
            if not rub:
                flash('Кошелёк не найден, валюта RUB отсутствует', 'danger')
                return redirect(url_for('auth_profile.profile'))
            wallet = Valet(user_id=current_user.id, currency_id=rub.id, balance=Decimal('0.00'))
            db.session.add(wallet)

        wallet.balance = _money(wallet.balance) + amount
        db.session.commit()
        flash(f'Баланс пополнен на {amount} ₽', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Top-up error: {e}")
        flash('Ошибка при пополнении баланса', 'danger')

    return redirect(url_for('auth_profile.profile'))


@auth_profile_bp.route('/seller/products/create', methods=['GET', 'POST'])
@login_required
@role_required('seller')
def seller_product_create():
    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price_raw = request.form.get('price', '').strip().replace(',', '.')
        category_id = request.form.get('category_id', type=int)
        image_url = request.form.get('image_url', '').strip()

        try:
            price = Decimal(price_raw).quantize(MONEY_QUANT)
        except (InvalidOperation, ValueError):
            flash('Введите корректную цену товара', 'danger')
            return redirect(url_for('auth_profile.seller_product_create'))

        if len(name) < 3:
            flash('Название товара должно содержать минимум 3 символа', 'danger')
            return redirect(url_for('auth_profile.seller_product_create'))

        if len(description) < 10:
            flash('Описание должно содержать минимум 10 символов', 'danger')
            return redirect(url_for('auth_profile.seller_product_create'))

        if price <= 0:
            flash('Цена товара должна быть больше нуля', 'danger')
            return redirect(url_for('auth_profile.seller_product_create'))

        category = db.session.get(Category, category_id) if category_id else None
        if not category:
            flash('Выберите существующую категорию', 'danger')
            return redirect(url_for('auth_profile.seller_product_create'))

        try:
            product = Product(
                name=name,
                description=description,
                price=price,
                category_id=category.id,
            )
            db.session.add(product)
            db.session.flush()

            if image_url:
                db.session.add(ProductImage(product_id=product.id, url=image_url))

            db.session.commit()
            flash(f'Товар "{name}" создан', 'success')
            return redirect(url_for('auth_profile.profile'))
        except Exception as e:
            db.session.rollback()
            print(f"Seller product create error: {e}")
            flash(f'Ошибка создания товара: {str(e)}', 'danger')

    return render_template('auth/seller_product_create.html', user=current_user, categories=categories)


@auth_profile_bp.route("/api/buyer/stats", methods=["GET"])
@login_required
def api_buyer_stats():
    """JSON API для статистики покупателя"""
    user_role = get_user_role_name(current_user) or "user"
    if user_role not in ["user", "customer"]:
        return jsonify({"error": "Unauthorized"}), 403
    
    period = request.args.get('period', '30d')
    
    stats = {
        'orders_count': AnalyticsService.buyer_orders_count(current_user.id, period),
        'total_spent': AnalyticsService.buyer_total_spent(current_user.id, period),
        'avg_check': AnalyticsService.buyer_avg_check(current_user.id, period),
        'top_categories': AnalyticsService.buyer_top_categories(current_user.id, period),
        'recent_orders': AnalyticsService.buyer_recent_orders(current_user.id),
    }
    
    return jsonify(stats)

@auth_profile_bp.route('/profile/orders')
@login_required
def profile_orders():
    """История заказов пользователя"""
    orders = _buyer_order_views(current_user.id)
    return render_template('auth/profile_orders.html', user=current_user, orders=orders)
