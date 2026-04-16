from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import User, Role, Currency, Valet  # ДОБАВЛЕНО: Currency и Valet
from datetime import datetime
from decimal import Decimal # ДОБАВЛЕНО

auth_register_bp = Blueprint("auth_register", __name__, url_prefix="/auth")

@auth_register_bp.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        name = request.form.get("name")
        second_name = request.form.get("second_name")
        age = request.form.get("age")
        role_id = request.form.get("role_id")
        
        # 1. Базовая проверка
        if not all([email, password, confirm_password, name, second_name, age, role_id]):
            flash("Все поля обязательны для заполнения", "danger")
            return redirect(url_for("auth_register.register_page"))
        
        if password != confirm_password:
            flash("Пароли не совпадают", "danger")
            return redirect(url_for("auth_register.register_page"))

        # 2. Проверка существования роли
        role = Role.query.get(int(role_id))
        if not role:
            flash("Выбранная роль не существует", "danger")
            return redirect(url_for("auth_register.register_page"))

        # 3. Проверка email
        if User.query.filter_by(email=email).first():
            flash("Пользователь с таким email уже существует", "danger")
            return redirect(url_for("auth_register.register_page"))

        try:
            # 4. Создание пользователя
            password_hash = generate_password_hash(password=password, salt_length=18)
            new_user = User(
                email=email,
                name=name,
                second_name=second_name,
                age=int(age),
                role_id=int(role_id),
                password_hash=password_hash 
            )
            db.session.add(new_user)
            db.session.flush() # Получаем ID пользователя

            # 5. Создание кошелька (ВАЖНО: Currency должен быть в базе!)
            rub = Currency.query.filter_by(currency_name="RUB").first()
            if not rub:
                # Если вдруг в базе нет рубля, создаем его на лету или кидаем ошибку
                raise Exception("Валюта RUB не найдена в базе данных. Запустите seed_db.")

            new_valet = Valet(
                user_id=new_user.id,
                currency_id=rub.id,
                balance=Decimal('0.00')
            )
            db.session.add(new_valet)
            
            db.session.commit()
            flash("Регистрация успешна!", "success")
            return redirect(url_for("auth_login.login_page"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при регистрации: {str(e)}", "danger")
            print(f"Registration error: {e}")
    
    roles = Role.query.all()
    return render_template("auth/register.html", roles=roles)