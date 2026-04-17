from flask import Blueprint, render_template

# Создаем Blueprint для информационного раздела
info_bp = Blueprint('info', __name__, template_folder='templates')

@info_bp.route('/about')
def about():
    """Страница 'О нас'"""
    return render_template('info/aboutus.html')

@info_bp.route('/contacts')
def contacts():
    """Страница 'Контакты'"""
    return render_template('info/contacts.html')

@info_bp.route('/faq')
def faq():
    """Страница 'FAQ' (Вопросы и ответы)"""
    return render_template('info/FAQ.html')

@info_bp.route('/shipping')
def shipping():
    """Страница 'Доставка'"""
    return render_template('info/shipping.html')