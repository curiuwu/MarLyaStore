from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from app import db
from app.models import Currency, Role, User, Valet
from app.role_utils import normalize_role_name


auth_register_bp = Blueprint("auth_register", __name__, url_prefix="/auth")

PUBLIC_REGISTRATION_ROLES = {"user", "seller"}


def _public_registration_roles():
    return [
        role
        for role in Role.query.order_by(Role.id).all()
        if normalize_role_name(role.role_name) in PUBLIC_REGISTRATION_ROLES
    ]


@auth_register_bp.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        name = request.form.get("name", "").strip()
        second_name = request.form.get("second_name", "").strip()
        age = request.form.get("age", "").strip()
        role_id = request.form.get("role_id", "").strip()

        if not all([email, password, confirm_password, name, second_name, age, role_id]):
            flash("Все поля обязательны для заполнения", "danger")
            return redirect(url_for("auth_register.register_page"))

        if password != confirm_password:
            flash("Пароли не совпадают", "danger")
            return redirect(url_for("auth_register.register_page"))

        try:
            role_id_int = int(role_id)
            age_int = int(age)
        except ValueError:
            flash("Некорректные данные регистрации", "danger")
            return redirect(url_for("auth_register.register_page"))

        role = db.session.get(Role, role_id_int)
        if not role:
            flash("Выбранная роль не существует", "danger")
            return redirect(url_for("auth_register.register_page"))

        if normalize_role_name(role.role_name) not in PUBLIC_REGISTRATION_ROLES:
            flash("Эта роль недоступна для публичной регистрации", "danger")
            return redirect(url_for("auth_register.register_page"))

        if User.query.filter_by(email=email).first():
            flash("Пользователь с таким email уже существует", "danger")
            return redirect(url_for("auth_register.register_page"))

        try:
            password_hash = generate_password_hash(password=password, salt_length=18)
            new_user = User(
                email=email,
                name=name,
                second_name=second_name,
                age=age_int,
                role_id=role.id,
                password_hash=password_hash,
                is_active=True,
            )
            db.session.add(new_user)
            db.session.flush()

            rub = Currency.query.filter_by(currency_name="RUB").first()
            if not rub:
                raise RuntimeError("Валюта RUB не найдена. Запустите seed-db.")

            db.session.add(
                Valet(
                    user_id=new_user.id,
                    currency_id=rub.id,
                    balance=Decimal("0.00"),
                )
            )

            db.session.commit()
            flash("Регистрация успешна!", "success")
            return redirect(url_for("auth_login.login_page"))

        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при регистрации: {str(e)}", "danger")
            print(f"Registration error: {e}")

    return render_template("auth/register.html", roles=_public_registration_roles())
