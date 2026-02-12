from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import User, Role
from datetime import datetime

auth_register_bp = Blueprint("auth_register", __name__, url_prefix="/auth")

@auth_register_bp.route("/register", methods=["GET", "POST"])
def register_page():
    """Регистрация нового пользователя"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        name = request.form.get("name")
        second_name = request.form.get("second_name")
        age = request.form.get("age")
        
        if not all([email, password, confirm_password, name, second_name, age]):
            flash("Все поля обязательны для заполнения", "danger")
            return redirect(url_for("auth_register.register_page"))
        
        if password != confirm_password:
            flash("Пароли не совпадают", "danger")
            return redirect(url_for("auth_register.register_page"))
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Пользователь с таким email уже существует", "danger")
            return redirect(url_for("auth_register.register_page"))
        
        try:
            new_user = User(
                email=email,
                name=name,
                second_name=second_name,
                age=int(age),
                role_id=1
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash("Регистрация успешна! Теперь вы можете войти", "success")
            return redirect(url_for("auth_login.login_page"))
            
        except Exception as e:
            db.session.rollback()
            flash("Ошибка при регистрации", "danger")
            print(f"Registration error: {e}")
    
    return render_template("auth/register.html")