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
