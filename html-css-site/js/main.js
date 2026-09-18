// Бургер-меню
const burger = document.querySelector('.burger');
const mobileMenu = document.querySelector('.mobile-menu');
let overlay = document.querySelector('.menu-overlay');
const body = document.body;

if (burger && mobileMenu && !overlay) {
    overlay = document.createElement('div');
    overlay.className = 'menu-overlay';
    overlay.setAttribute('aria-hidden', 'true');
    document.body.appendChild(overlay);
}

// Функция закрытия меню
function closeMenu() {
    burger.classList.remove('active');
    mobileMenu.classList.remove('active');
    if (overlay) {
        overlay.classList.remove('active');
    }
    body.style.overflow = '';
}

// Функция открытия меню
function openMenu() {
    burger.classList.add('active');
    mobileMenu.classList.add('active');
    if (overlay) {
        overlay.classList.add('active');
    }
    body.style.overflow = 'hidden';
}

if (burger && mobileMenu) {
    // Клик по бургеру
    burger.addEventListener('click', (e) => {
        e.stopPropagation();
        if (mobileMenu.classList.contains('active')) {
            closeMenu();
        } else {
            openMenu();
        }
    });
    
    // Закрытие меню при клике на ссылку
    const mobileLinks = document.querySelectorAll('.mobile-menu__link');
    mobileLinks.forEach(link => {
        link.addEventListener('click', closeMenu);
    });
    
    // Закрытие при клике на оверлей
    if (overlay) {
        overlay.addEventListener('click', closeMenu);
    }
    
    // Закрытие при клике вне меню и вне бургера
    document.addEventListener('click', (e) => {
        if (mobileMenu.classList.contains('active')) {
            const isClickOnBurger = burger.contains(e.target);
            const isClickOnMenu = mobileMenu.contains(e.target);
            
            if (!isClickOnBurger && !isClickOnMenu) {
                closeMenu();
            }
        }
    });
    
    // Закрытие при нажатии клавиши Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
            closeMenu();
        }
    });
}

// Активная ссылка при скролле
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav__link');

window.addEventListener('scroll', () => {
    let current = '';
    const scrollPosition = window.scrollY + 100;
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        
        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            current = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href').substring(1);
        if (href === current) {
            link.classList.add('active');
        }
    });
});

// Аккордеон «Почему Hungrie?»
const whyTriggers = document.querySelectorAll('.why__trigger');

whyTriggers.forEach((trigger) => {
    trigger.addEventListener('click', () => {
        const item = trigger.closest('.why__item');
        const panel = item.querySelector('.why__panel');
        const isOpen = item.classList.contains('is-open');

        document.querySelectorAll('.why__item.is-open').forEach((openItem) => {
            if (openItem !== item) {
                openItem.classList.remove('is-open');
                const openTrigger = openItem.querySelector('.why__trigger');
                const openPanel = openItem.querySelector('.why__panel');
                openTrigger.setAttribute('aria-expanded', 'false');
                openPanel.hidden = true;
            }
        });

        if (isOpen) {
            item.classList.remove('is-open');
            trigger.setAttribute('aria-expanded', 'false');
            panel.hidden = true;
        } else {
            item.classList.add('is-open');
            trigger.setAttribute('aria-expanded', 'true');
            panel.hidden = false;
        }
    });
});

// Форма контактов (демо — без отправки на сервер)
const contactForm = document.querySelector('.contacts__form');

if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        contactForm.classList.add('is-sent');
        const submitBtn = contactForm.querySelector('.contacts__submit');
        if (submitBtn) {
            submitBtn.textContent = 'Сообщение отправлено';
            submitBtn.disabled = true;
        }
        contactForm.reset();
    });
}