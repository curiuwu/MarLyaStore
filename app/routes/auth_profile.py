from flask import Blueprint, render_template
from flask_login import login_required, current_user

auth_profile_bp = Blueprint("auth_profile", __name__, url_prefix="/auth")

@auth_profile_bp.route("/profile")
@login_required
def profile():
    """Личный кабинет"""
    return render_template("auth/profile.html", user=current_user)

@auth_profile_bp.route("/profile/orders")
@login_required
def profile_orders():
    """Страница с заказами пользователя"""
    return render_template("auth/profile_orders.html", user=current_user)

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