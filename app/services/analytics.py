"""Сервис для сбора аналитики по разным ролям пользователей"""

from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, distinct
from app import db
from app.models import Order, OrderItem, OrderStatus, Product, Category, User, Valet, Status, Review, Wishlist


class AnalyticsService:
    """Сервис для получения аналитических данных"""
    
    # Периоды в днях
    PERIODS = {
        '7d': 7,
        '30d': 30,
        '90d': 90,
        '365d': 365,
        'all': None
    }
    
    @staticmethod
    def get_date_from_period(period: str) -> datetime:
        """Получить дату начала периода"""
        days = AnalyticsService.PERIODS.get(period, 30)
        if days is None:
            return datetime(2000, 1, 1)
        return datetime.utcnow() - timedelta(days=days)
    
    # ===== АНАЛИТИКА ПРОДАВЦА =====
    
    @staticmethod
    def seller_orders_count(seller_id: int, period: str = '30d') -> int:
        """Количество заказов продавца за период"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        count = db.session.query(func.count(Order.id)).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            Order.valet_id == (
                db.session.query(Valet.id).filter(Valet.user_id == seller_id).scalar()
            ),
            OrderStatus.date >= start_date
        ).scalar() or 0
        
        return count
    
    @staticmethod
    def seller_revenue(seller_id: int, period: str = '30d') -> float:
        """Выручка продавца за период"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        valet_id = db.session.query(Valet.id).filter(Valet.user_id == seller_id).scalar()
        if not valet_id:
            return 0.0
        
        revenue = db.session.query(
            func.sum(OrderItem.price_at_purchase * OrderItem.quantity)
        ).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            Order.valet_id == valet_id,
            OrderStatus.date >= start_date
        ).scalar() or 0.0
        
        return float(revenue)
    
    @staticmethod
    def seller_avg_check(seller_id: int, period: str = '30d') -> float:
        """Средний чек продавца за период"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        valet_id = db.session.query(Valet.id).filter(Valet.user_id == seller_id).scalar()
        if not valet_id:
            return 0.0
        
        avg = db.session.query(
            func.avg(
                db.session.query(
                    func.sum(OrderItem.price_at_purchase * OrderItem.quantity)
                ).join(Order, OrderItem.order_id == Order.id).filter(
                    OrderItem.order_id == Order.id
                ).correlate(Order).scalar_subquery()
            )
        ).select_from(Order).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            Order.valet_id == valet_id,
            OrderStatus.date >= start_date
        ).scalar()
        
        # Альтернативный расчет - средняя цена товара
        avg_simple = db.session.query(
            func.avg(OrderItem.price_at_purchase)
        ).join(Order, OrderItem.order_id == Order.id).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            Order.valet_id == valet_id,
            OrderStatus.date >= start_date
        ).scalar() or 0.0
        
        return float(avg_simple)
    
    @staticmethod
    def seller_top_products(seller_id: int, period: str = '30d', limit: int = 5):
        """ТОП товары продавца по количеству продаж"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        valet_id = db.session.query(Valet.id).filter(Valet.user_id == seller_id).scalar()
        if not valet_id:
            return []
        
        results = db.session.query(
            Product.id,
            Product.name,
            func.count(OrderItem.id).label('order_count'),
            func.sum(OrderItem.quantity).label('total_qty'),
            func.sum(OrderItem.price_at_purchase * OrderItem.quantity).label('revenue')
        ).join(
            OrderItem, Product.id == OrderItem.items_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            Order.valet_id == valet_id,
            OrderStatus.date >= start_date
        ).group_by(
            Product.id, Product.name
        ).order_by(
            desc('total_qty')
        ).limit(limit).all()
        
        return [{'id': r[0], 'name': r[1], 'count': r[2], 'qty': r[3], 'revenue': float(r[4] or 0)} 
                for r in results]
    
    @staticmethod
    def seller_top_categories(seller_id: int, period: str = '30d', limit: int = 5):
        """ТОП категории продавца по количеству заказов"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        valet_id = db.session.query(Valet.id).filter(Valet.user_id == seller_id).scalar()
        if not valet_id:
            return []
        
        results = db.session.query(
            Category.id,
            Category.name,
            func.count(distinct(Order.id)).label('order_count'),
            func.sum(OrderItem.quantity).label('total_qty')
        ).join(
            Product, Category.id == Product.category_id
        ).join(
            OrderItem, Product.id == OrderItem.items_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            Order.valet_id == valet_id,
            OrderStatus.date >= start_date
        ).group_by(
            Category.id, Category.name
        ).order_by(
            desc('order_count')
        ).limit(limit).all()
        
        return [{'id': r[0], 'name': r[1], 'orders': r[2], 'qty': r[3]} for r in results]
    
    @staticmethod
    def seller_orders_by_status(seller_id: int, period: str = '30d'):
        """Распределение заказов продавца по статусам"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        valet_id = db.session.query(Valet.id).filter(Valet.user_id == seller_id).scalar()
        if not valet_id:
            return []
        
        results = db.session.query(
            Status.name,
            func.count(Order.id).label('count')
        ).join(
            OrderStatus, Status.id == OrderStatus.status_id
        ).join(
            Order, OrderStatus.order_id == Order.id
        ).filter(
            Order.valet_id == valet_id,
            OrderStatus.date >= start_date
        ).group_by(
            Status.name
        ).all()
        
        return [{'status': r[0], 'count': r[1]} for r in results]
    
    # ===== АНАЛИТИКА АДМИНИСТРАТОРА =====
    
    @staticmethod
    def admin_total_orders(period: str = '30d') -> int:
        """Общее количество заказов на маркетплейсе за период"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        count = db.session.query(func.count(Order.id)).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            OrderStatus.date >= start_date
        ).scalar() or 0
        
        return count
    
    @staticmethod
    def admin_total_gmv(period: str = '30d') -> float:
        """Общий оборот маркетплейса за период"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        gmv = db.session.query(
            func.sum(OrderItem.price_at_purchase * OrderItem.quantity)
        ).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            OrderStatus.date >= start_date
        ).scalar() or 0.0
        
        return float(gmv)
    
    @staticmethod
    def admin_total_buyers(period: str = '30d') -> int:
        """Количество уникальных покупателей за период"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        count = db.session.query(func.count(distinct(Order.buyer_id))).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            Order.buyer_id.isnot(None),
            OrderStatus.date >= start_date
        ).scalar() or 0
        
        return count
    
    @staticmethod
    def admin_total_sellers() -> int:
        """Количество продавцов на маркетплейсе"""
        count = db.session.query(func.count(distinct(Valet.user_id))).scalar() or 0
        return count
    
    @staticmethod
    def admin_top_categories(period: str = '30d', limit: int = 5):
        """ТОП категории на маркетплейсе"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        results = db.session.query(
            Category.id,
            Category.name,
            func.count(distinct(Order.id)).label('order_count'),
            func.sum(OrderItem.quantity).label('total_qty')
        ).join(
            Product, Category.id == Product.category_id
        ).join(
            OrderItem, Product.id == OrderItem.items_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            OrderStatus.date >= start_date
        ).group_by(
            Category.id, Category.name
        ).order_by(
            desc('order_count')
        ).limit(limit).all()
        
        return [{'id': r[0], 'name': r[1], 'orders': r[2], 'qty': r[3]} for r in results]
    
    @staticmethod
    def admin_top_sellers(period: str = '30d', limit: int = 5):
        """ТОП продавцы по обороту"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        results = db.session.query(
            User.id,
            User.name,
            User.second_name,
            func.count(distinct(Order.id)).label('order_count'),
            func.sum(OrderItem.price_at_purchase * OrderItem.quantity).label('revenue')
        ).join(
            Valet, User.id == Valet.user_id
        ).join(
            Order, Valet.id == Order.valet_id
        ).join(
            OrderItem, Order.id == OrderItem.order_id
        ).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            OrderStatus.date >= start_date
        ).group_by(
            User.id, User.name, User.second_name
        ).order_by(
            desc('revenue')
        ).limit(limit).all()
        
        return [{'id': r[0], 'name': f"{r[1]} {r[2]}", 'orders': r[3], 'revenue': float(r[4] or 0)} 
                for r in results]
    
    @staticmethod
    def admin_orders_by_status(period: str = '30d'):
        """Распределение всех заказов по статусам"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        results = db.session.query(
            Status.name,
            func.count(Order.id).label('count')
        ).join(
            OrderStatus, Status.id == OrderStatus.status_id
        ).join(
            Order, OrderStatus.order_id == Order.id
        ).filter(
            OrderStatus.date >= start_date
        ).group_by(
            Status.name
        ).all()
        
        return [{'status': r[0], 'count': r[1]} for r in results]
    
    @staticmethod
    def admin_new_users(period: str = '30d') -> int:
        """Количество новых пользователей за период"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        count = db.session.query(func.count(User.id)).filter(
            User.created_at >= start_date
        ).scalar() or 0
        
        return count
    
    # ===== АНАЛИТИКА ПОКУПАТЕЛЯ =====
    
    @staticmethod
    def buyer_orders_count(buyer_id: int, period: str = '30d') -> int:
        """Количество заказов покупателя за период"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        count = db.session.query(func.count(Order.id)).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            Order.buyer_id == buyer_id,
            OrderStatus.date >= start_date
        ).scalar() or 0
        
        return count
    
    @staticmethod
    def buyer_total_spent(buyer_id: int, period: str = '30d') -> float:
        """Общая сумма покупок покупателя за период"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        total = db.session.query(
            func.sum(OrderItem.price_at_purchase * OrderItem.quantity)
        ).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            Order.buyer_id == buyer_id,
            OrderStatus.date >= start_date
        ).scalar() or 0.0
        
        return float(total)
    
    @staticmethod
    def buyer_avg_check(buyer_id: int, period: str = '30d') -> float:
        """Средний чек покупателя за период"""
        total = AnalyticsService.buyer_total_spent(buyer_id, period)
        count = AnalyticsService.buyer_orders_count(buyer_id, period)
        
        if count == 0:
            return 0.0
        
        return total / count
    
    @staticmethod
    def buyer_top_categories(buyer_id: int, period: str = '30d', limit: int = 5):
        """ТОП категории покупателя по количеству покупок"""
        start_date = AnalyticsService.get_date_from_period(period)
        
        results = db.session.query(
            Category.id,
            Category.name,
            func.count(distinct(Order.id)).label('order_count'),
            func.sum(OrderItem.quantity).label('total_qty'),
            func.sum(OrderItem.price_at_purchase * OrderItem.quantity).label('spent')
        ).join(
            Product, Category.id == Product.category_id
        ).join(
            OrderItem, Product.id == OrderItem.items_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).filter(
            Order.buyer_id == buyer_id,
            OrderStatus.date >= start_date
        ).group_by(
            Category.id, Category.name
        ).order_by(
            desc('total_qty')
        ).limit(limit).all()
        
        return [{'id': r[0], 'name': r[1], 'orders': r[2], 'qty': r[3], 'spent': float(r[4] or 0)} 
                for r in results]
    
    @staticmethod
    def buyer_recent_orders(buyer_id: int, limit: int = 5):
        """Последние заказы покупателя"""
        results = db.session.query(
            Order.id,
            OrderStatus.date,
            Status.name,
            func.sum(OrderItem.price_at_purchase * OrderItem.quantity).label('total')
        ).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).join(
            Status, OrderStatus.status_id == Status.id
        ).join(
            OrderItem, Order.id == OrderItem.order_id
        ).filter(
            Order.buyer_id == buyer_id
        ).group_by(
            Order.id, OrderStatus.date, Status.name
        ).order_by(
            desc(OrderStatus.date)
        ).limit(limit).all()
        
        return [{'id': r[0], 'date': r[1].strftime('%d.%m.%Y') if r[1] else 'N/A', 
                'status': r[2], 'total': float(r[3] or 0)} for r in results]
    
    # ===== МЕТОДЫ ДЛЯ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ =====
    
    @staticmethod
    def get_user_wishlist_count(user_id: int) -> int:
        """Количество товаров в избранном пользователя"""
        count = db.session.query(func.count(Wishlist.id)).filter(
            Wishlist.user_id == user_id
        ).scalar() or 0
        return count
    
    @staticmethod
    def get_user_active_orders_count(user_id: int) -> int:
        """Количество активных заказов пользователя (не завершенные)"""
        # Активные заказы - это те, у которых статус не "Доставлен" и не "Отменен"
        inactive_statuses = ['Доставлен', 'Отменен']
        
        count = db.session.query(func.count(Order.id)).join(
            OrderStatus, Order.id == OrderStatus.order_id
        ).join(
            Status, OrderStatus.status_id == Status.id
        ).filter(
            Order.buyer_id == user_id,
            ~Status.name.in_(inactive_statuses)
        ).scalar() or 0
        
        return count
    
    @staticmethod
    def get_user_rating(user_id: int) -> float:
        """Средний рейтинг пользователя как покупателя (на основе отзывов)"""
        avg_rating = db.session.query(func.avg(Review.rating)).filter(
            Review.user_id == user_id
        ).scalar() or 0.0
        return float(avg_rating)
    
    @staticmethod
    def get_user_bonuses(user_id: int) -> float:
        """Бонусы пользователя (заглушка, можно реализовать логику начисления бонусов)"""
        # Пока возвращаем 0, можно добавить логику начисления бонусов
        return 0.0
