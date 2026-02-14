// Плавная прокрутка и анимации при появлении элементов
document.addEventListener('DOMContentLoaded', function() {
    // Конфигурация наблюдателя для элементов
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = entry.target.dataset.animation || 'fadeInUp 0.8s ease-out forwards';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Применяем наблюдатель к элементам с классами
    const animatedElements = document.querySelectorAll('.category-card, .offer-card, .advantage-item, .section-title');
    animatedElements.forEach(el => observer.observe(el));

    // Анимация при наведении на кнопки
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.02)';
        });
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Анимация навигационных ссылок
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
        });
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // Плавность появления при скролле
    window.addEventListener('scroll', function() {
        const parallaxElements = document.querySelectorAll('.shape');
        parallaxElements.forEach((el, index) => {
            const scrollPosition = window.pageYOffset;
            el.style.transform = `translateY(${scrollPosition * 0.1 * (index + 1)}px)`;
        });
    });

    // Форма подписки
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = this.querySelector('input[type="email"]');
            const email = emailInput.value;

            // Добавляем визуальную обратную связь
            const submitBtn = this.querySelector('.btn-primary');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = '✓ Спасибо!';
            submitBtn.style.background = 'linear-gradient(135deg, #10b981, #34d399)';

            setTimeout(() => {
                submitBtn.textContent = originalText;
                submitBtn.style.background = '';
                emailInput.value = '';
            }, 2000);
        });
    }

    // Анимация счетчика при появлении
    const animateCounter = (element, targetValue, duration = 2000) => {
        let currentValue = 0;
        const increment = targetValue / (duration / 16);
        
        const counter = setInterval(() => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                element.textContent = targetValue;
                clearInterval(counter);
            } else {
                element.textContent = Math.floor(currentValue);
            }
        }, 16);
    };

    // Анимация категорий при наведении
    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.card-icon');
            icon.style.animation = 'none';
            setTimeout(() => {
                icon.style.animation = 'bounceIn 0.6s ease-out';
            }, 10);
        });
    });

    // Активная ссылка при прокрутке
    const sections = document.querySelectorAll('section');
    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            if (pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
    });

    // Эффект разброса при клике на кнопки
    const createRipple = (event) => {
        const btn = event.currentTarget;
        const ripple = document.createElement('span');
        
        const rect = btn.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        btn.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    };

    buttons.forEach(btn => {
        btn.addEventListener('click', createRipple);
    });

    // Загрузка страницы с анимацией
    document.body.style.animation = 'fadeIn 0.6s ease-out';
});

// Добавляем стили для ripple эффекта динамически
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: rippleAnimation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes rippleAnimation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Инициализация при загрузке
window.addEventListener('load', function() {
    console.log('✨ MarLya Store загрузилась успешно!');
});

// ===== ФУНКЦИИ ДЛЯ АВТОРИЗАЦИИ =====

// Показать/скрыть пароль
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
    input.setAttribute('type', type);
    
    // Анимация кнопки
    const btn = event.currentTarget;
    btn.style.transform = 'translateY(-50%) scale(1.2)';
    setTimeout(() => {
        btn.style.transform = 'translateY(-50%) scale(1)';
    }, 200);
}

// Валидация формы регистрации
function validateRegistrationForm() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    const email = document.getElementById('email');
    const age = document.getElementById('age');
    
    let isValid = true;
    
    // Проверка email
    if (email && !isValidEmail(email.value)) {
        showError(email, 'Введите корректный email');
        isValid = false;
    }
    
    // Проверка пароля
    if (password && password.value.length < 6) {
        showError(password, 'Пароль должен быть минимум 6 символов');
        isValid = false;
    }
    
    // Проверка совпадения паролей
    if (confirmPassword && password.value !== confirmPassword.value) {
        showError(confirmPassword, 'Пароли не совпадают');
        isValid = false;
    }
    
    // Проверка возраста
    if (age && (age.value < 14 || age.value > 120)) {
        showError(age, 'Возраст должен быть от 14 до 120 лет');
        isValid = false;
    }
    
    return isValid;
}

// Валидация email
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Показать ошибку
function showError(input, message) {
    input.classList.add('is-invalid');
    
    // Создаем или обновляем сообщение об ошибке
    let error = input.parentNode.querySelector('.error-message');
    if (!error) {
        error = document.createElement('div');
        error.className = 'error-message';
        error.style.cssText = 'color: #ef4444; font-size: 0.85rem; margin-top: 5px; animation: slideInUp 0.3s ease;';
        input.parentNode.appendChild(error);
    }
    error.textContent = message;
    
    // Удаляем ошибку при вводе
    input.addEventListener('input', function() {
        this.classList.remove('is-invalid');
        const error = this.parentNode.querySelector('.error-message');
        if (error) error.remove();
    }, { once: true });
}

// Смена аватарки (предпросмотр)
function previewAvatar(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const avatar = document.querySelector('.avatar-image');
            if (avatar) {
                avatar.style.backgroundImage = `url(${e.target.result})`;
                avatar.style.backgroundSize = 'cover';
                avatar.textContent = '';
                
                // Анимация
                avatar.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    avatar.style.transform = 'scale(1)';
                }, 200);
            }
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Редактирование профиля
function toggleEditProfile() {
    const form = document.querySelector('.profile-info-form');
    const editBtn = document.querySelector('.edit-profile-btn');
    const saveBtn = document.querySelector('.save-profile-btn');
    
    if (form) {
        const inputs = form.querySelectorAll('input:not([type="hidden"])');
        inputs.forEach(input => {
            input.disabled = !input.disabled;
        });
        
        if (editBtn) editBtn.style.display = editBtn.style.display === 'none' ? 'flex' : 'none';
        if (saveBtn) saveBtn.style.display = saveBtn.style.display === 'none' ? 'flex' : 'none';
    }
}

// Удаление из избранного
function removeFromWishlist(productId, element) {
    if (confirm('Удалить товар из избранного?')) {
        // Анимация удаления
        const item = element.closest('.wishlist-item');
        item.style.transform = 'scale(0)';
        item.style.opacity = '0';
        
        setTimeout(() => {
            item.remove();
            
            // Показываем уведомление
            showNotification('Товар удален из избранного', 'success');
        }, 300);
        
        // Здесь будет AJAX запрос к серверу
        console.log('Удаление товара из избранного:', productId);
    }
}

// Уведомления
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 30px;
        padding: 15px 25px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        border-left: 4px solid ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: var(--text-dark);
        font-weight: 500;
        z-index: 9999;
        animation: slideInRight 0.3s ease;
        display: flex;
        align-items: center;
        gap: 10px;
    `;
    
    notification.innerHTML = `
        <span style="color: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'}">
            ${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}
        </span>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Активный пункт меню в ЛК
function setActiveMenuItem() {
    const path = window.location.pathname;
    const menuItems = document.querySelectorAll('.profile-menu li');
    
    menuItems.forEach(item => {
        const link = item.querySelector('a');
        if (link && link.getAttribute('href') === path) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    console.log('✨ MarLya Store загрузилась успешно!');
    
    // Активный пункт меню
    setActiveMenuItem();
    
    // Валидация формы регистрации
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            if (!validateRegistrationForm()) {
                e.preventDefault();
            }
        });
    }
    
    // Предпросмотр аватарки
    const avatarInput = document.getElementById('avatar-upload');
    if (avatarInput) {
        avatarInput.addEventListener('change', function() {
            previewAvatar(this);
        });
    }
    
    // Кнопка редактирования профиля
    const editBtn = document.querySelector('.edit-profile-btn');
    if (editBtn) {
        editBtn.addEventListener('click', toggleEditProfile);
    }
    
    // Кнопка сохранения профиля
    const saveBtn = document.querySelector('.save-profile-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', toggleEditProfile);
    }
});

// Добавляем стили для уведомлений
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .error-message {
        animation: slideInUp 0.3s ease;
    }
    
    @keyframes slideInUp {
        from {
            transform: translateY(10px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(notificationStyles);