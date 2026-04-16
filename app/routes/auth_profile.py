from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.analytics import AnalyticsService
from app.models import Order
from app import db
from decimal import Decimal
auth_profile_bp = Blueprint("auth_profile", __name__, url_prefix="/auth")

@auth_profile_bp.route("/profile")
@login_required
def profile():
    # Получаем роль пользователя
    user_role = current_user.role.role_name if current_user.role else "user"
    
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
        return render_template("auth/profile_customer.html", user=current_user, profile_stats=profile_stats)


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
    user_role = current_user.role.role_name if current_user.role else "user"
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
    user_role = current_user.role.role_name if current_user.role else "user"
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
    try:
        if current_user.valet:
            # Преобразуем к Decimal, так как в базе Numeric
            current_user.valet.balance = Decimal(str(current_user.valet.balance)) + Decimal('50000.00')
            db.session.commit()
            flash('Баланс пополнен! ✨', 'success')
        else:
            flash('Кошелек не найден', 'danger')
    except Exception as e:
        db.session.rollback() # Откатываем, если что-то пошло не так
        print(f"Ошибка дюпа: {e}")
        flash('Ошибка при записи в базу', 'danger')
        
    return redirect(request.referrer or url_for('auth_profile.profile'))

@auth_profile_bp.route("/api/buyer/stats", methods=["GET"])
@login_required
def api_buyer_stats():
    """JSON API для статистики покупателя"""
    user_role = current_user.role.role_name if current_user.role else "user"
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
    orders = Order.query.filter_by(buyer_id=current_user.id).order_by(Order.date.desc()).all()
    return render_template('auth/profile_orders.html', orders=orders)