"""Вспомогательные функции и декораторы"""

from functools import wraps
from flask import redirect, url_for, flash, abort, current_app
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)


def admin_required(f):
    """Декоратор для проверки, что пользователь является администратором"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('auth_login.login_page'))
        
        # Проверяем роль пользователя
        user_role = current_user.role.role_name if current_user.role else None
        
        if user_role != 'admin':
            logger.warning(f"Попытка несанкционированного доступа к админ-панели: user_id={current_user.id}, role={user_role}")
            flash('У вас нет доступа к админ-панели', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function


def role_required(*allowed_roles):
    """Декоратор для проверки роли пользователя (можно несколько ролей)
    
    Использование:
    @role_required('admin', 'seller')
    def some_view():
        pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Пожалуйста, войдите в систему', 'warning')
                return redirect(url_for('auth_login.login_page'))
            
            user_role = current_user.role.role_name if current_user.role else None
            
            if user_role not in allowed_roles:
                logger.warning(f"Попытка доступа с недостаточными правами: user_id={current_user.id}, role={user_role}, required={allowed_roles}")
                flash('У вас нет доступа к этому разделу', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator
