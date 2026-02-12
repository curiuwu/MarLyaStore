from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from datetime import datetime

auth_login_bp = Blueprint("auth_login", __name__, url_prefix="/auth")

@auth_login_bp.route("/login", methods=["GET", "POST"])
def login_page():
    """Вход пользователя"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash("Неверный email или пароль", "danger")
            return redirect(url_for("auth_login.login_page"))
        
        if not user.is_active:
            flash("Аккаунт деактивирован", "warning")
            return redirect(url_for("auth_login.login_page"))
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=remember)
        
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        return redirect(url_for("auth_profile.profile"))
    
    return render_template("auth/login.html")

@auth_login_bp.route("/logout")
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("auth_login.login_page"))