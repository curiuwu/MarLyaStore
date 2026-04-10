"""Admin routes - управление товарами и системой"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy import or_, desc, func
from app import db
from app.models import Product, Category, ProductImage, Discount, Review
from app.helpers import admin_required
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ============================================================================
# Главная страница админ-панели
# ============================================================================

@admin_bp.route('/')
@admin_required
def dashboard():
    """Главная страница админ-панели"""
    stats = {
        'total_products': db.session.query(func.count(Product.id)).scalar() or 0,
        'total_categories': db.session.query(func.count(Category.id)).scalar() or 0,
        'total_reviews': db.session.query(func.count(Review.id)).scalar() or 0,
    }
    return render_template('admin/dashboard.html', stats=stats)


# ============================================================================
# CRUD ТОВАРОВ
# ============================================================================

@admin_bp.route('/products')
@admin_required
def products_list():
    """Список товаров с поиском и пагинацией"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category', 0, type=int)
    per_page = 20
    
    query = Product.query
    
    # Фильтр по поиску
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )
    
    # Фильтр по категории
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    # Сортировка по id (новые в конце)
    query = query.order_by(desc(Product.id))
    
    products = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.all()
    
    return render_template(
        'admin/products/list.html',
        products=products,
        categories=categories,
        search=search,
        category_id=category_id
    )


@admin_bp.route('/products/create', methods=['GET', 'POST'])
@admin_required
def product_create():
    """Создание нового товара"""
    categories = Category.query.all()
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            category_id = request.form.get('category_id', type=int)
            
            # Валидация
            if not name or len(name) < 3:
                flash('Название товара должно содержать минимум 3 символа', 'danger')
                return redirect(url_for('admin.product_create'))
            
            if not description or len(description) < 10:
                flash('Описание должно содержать минимум 10 символов', 'danger')
                return redirect(url_for('admin.product_create'))
            
            if not category_id:
                flash('Выберите категорию', 'danger')
                return redirect(url_for('admin.product_create'))
            
            # Проверяем, существует ли категория
            category = Category.query.get(category_id)
            if not category:
                flash('Выбранная категория не существует', 'danger')
                return redirect(url_for('admin.product_create'))
            
            # Создаём товар
            product = Product(
                name=name,
                description=description,
                category_id=category_id
            )
            
            db.session.add(product)
            db.session.flush()  # Получаем ID товара
            
            # Обработка изображения (если загружено)
            if 'image_url' in request.form and request.form.get('image_url'):
                image_url = request.form.get('image_url').strip()
                if image_url:
                    product_image = ProductImage(
                        product_id=product.id,
                        url=image_url
                    )
                    db.session.add(product_image)
            
            db.session.commit()
            logger.info(f"Товар создан: {product.id} - {name} (admin_id={current_user.id})")
            flash(f'Товар "{name}" успешно создан', 'success')
            return redirect(url_for('admin.products_list'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при создании товара: {str(e)}")
            flash(f'Ошибка при создании товара: {str(e)}', 'danger')
            return redirect(url_for('admin.product_create'))
    
    return render_template('admin/products/create.html', categories=categories)


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def product_edit(product_id):
    """Редактирование товара"""
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            category_id = request.form.get('category_id', type=int)
            
            # Валидация
            if not name or len(name) < 3:
                flash('Название товара должно содержать минимум 3 символа', 'danger')
                return redirect(url_for('admin.product_edit', product_id=product_id))
            
            if not description or len(description) < 10:
                flash('Описание должно содержать минимум 10 символов', 'danger')
                return redirect(url_for('admin.product_edit', product_id=product_id))
            
            if not category_id:
                flash('Выберите категорию', 'danger')
                return redirect(url_for('admin.product_edit', product_id=product_id))
            
            # Проверяем, существует ли категория
            category = Category.query.get(category_id)
            if not category:
                flash('Выбранная категория не существует', 'danger')
                return redirect(url_for('admin.product_edit', product_id=product_id))
            
            # Обновляем товар
            product.name = name
            product.description = description
            product.category_id = category_id
            
            db.session.commit()
            logger.info(f"Товар обновлён: {product.id} - {name} (admin_id={current_user.id})")
            flash(f'Товар "{name}" успешно обновлён', 'success')
            return redirect(url_for('admin.products_list'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при редактировании товара: {str(e)}")
            flash(f'Ошибка при редактировании товара: {str(e)}', 'danger')
            return redirect(url_for('admin.product_edit', product_id=product_id))
    
    return render_template('admin/products/edit.html', product=product, categories=categories)


@admin_bp.route('/products/<int:product_id>/delete', methods=['GET', 'POST'])
@admin_required
def product_delete(product_id):
    """Удаление товара"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            product_name = product.name
            
            # Удаляем связанные данные
            ProductImage.query.filter_by(product_id=product_id).delete()
            Discount.query.filter_by(product_id=product_id).delete()
            Review.query.filter_by(product_id=product_id).delete()
            
            # Удаляем товар
            db.session.delete(product)
            db.session.commit()
            
            logger.info(f"Товар удалён: {product_id} - {product_name} (admin_id={current_user.id})")
            flash(f'Товар "{product_name}" успешно удалён', 'success')
            return redirect(url_for('admin.products_list'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при удалении товара: {str(e)}")
            flash(f'Ошибка при удалении товара: {str(e)}', 'danger')
            return redirect(url_for('admin.product_delete', product_id=product_id))
    
    return render_template('admin/products/delete.html', product=product)


# ============================================================================
# API для удаления (AJAX)
# ============================================================================

@admin_bp.route('/api/products/<int:product_id>/delete', methods=['DELETE'])
@admin_required
def api_product_delete(product_id):
    """API для удаления товара (DELETE запрос)"""
    try:
        product = Product.query.get_or_404(product_id)
        product_name = product.name
        
        ProductImage.query.filter_by(product_id=product_id).delete()
        Discount.query.filter_by(product_id=product_id).delete()
        Review.query.filter_by(product_id=product_id).delete()
        
        db.session.delete(product)
        db.session.commit()
        
        logger.info(f"Товар удалён (API): {product_id} - {product_name} (admin_id={current_user.id})")
        
        return jsonify({
            'success': True,
            'message': f'Товар "{product_name}" успешно удалён'
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при удалении товара (API): {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Ошибка при удалении: {str(e)}'
        }), 500
