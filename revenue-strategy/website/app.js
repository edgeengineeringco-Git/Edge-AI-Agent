/* ═══════════════════════════════════════════════════════════════
   EDGE Global Solutions — App JavaScript
   Language switching, navbar, form handling, mobile menu
   ═══════════════════════════════════════════════════════════════ */

// ─── Current Language State ───
let currentLang = localStorage.getItem('edge-lang') || 'en';

// ─── Translation Lookup ───
function t(key) {
    if (translations && translations[key] && translations[key][currentLang]) {
        return translations[key][currentLang];
    }
    // Fallback to English
    if (translations && translations[key] && translations[key]['en']) {
        return translations[key]['en'];
    }
    return key;
}

// ─── Apply Translations to DOM ───
function applyTranslations() {
    // Text content
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const translated = t(key);
        if (translated && translated !== key) {
            el.innerHTML = translated;
        }
    });

    // Placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        const translated = t(key);
        if (translated && translated !== key) {
            el.placeholder = translated;
        }
    });

    // Update page title
    document.title = currentLang === 'ar' ? 'EDGE Global Solutions — الذكاء الاصطناعي والطائرات بدون طيار والأتمتة'
        : currentLang === 'fa' ? 'EDGE Global Solutions — هوش مصنوعی، پهپاد و اتوماسیون'
        : currentLang === 'tr' ? 'EDGE Global Solutions — Yapay Zeka, Drone ve Otomasyon'
        : currentLang === 'fr' ? 'EDGE Global Solutions — IA, Drones & Automatisation'
        : currentLang === 'es' ? 'EDGE Global Solutions — IA, Drones y Automatización'
        : 'EDGE Global Solutions — AI, Drones & Automation';
}

// ─── Set Language ───
function setLang(lang) {
    currentLang = lang;
    localStorage.setItem('edge-lang', lang);

    // Set direction for RTL languages
    const isRTL = lang === 'ar' || lang === 'fa';
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;

    // Update active button
    document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    // Apply translations
    applyTranslations();

    // Close mobile menu if open
    document.getElementById('navLinks').classList.remove('open');
}

// ─── Mobile Menu Toggle ───
function toggleMenu() {
    document.getElementById('navLinks').classList.toggle('open');
}

// ─── Navbar Scroll Effect ───
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// ─── Close Mobile Menu on Link Click ───
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        document.getElementById('navLinks').classList.remove('open');
    });
});

// ─── Form Submission ───
function handleSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const successMessages = {
        en: { icon: '✅', title: 'Inquiry Sent Successfully!', desc: 'Our AI agents will review your request and respond within 24 hours.' },
        fr: { icon: '✅', title: 'Demande Envoyée!', desc: 'Nos agents IA examineront votre demande et répondront dans les 24 heures.' },
        es: { icon: '✅', title: '¡Consulta Enviada!', desc: 'Nuestros agentes IA revisarán su solicitud y responderán en 24 horas.' },
        ar: { icon: '✅', title: 'تم إرسال الاستفسار بنجاح!', desc: 'سيراجع وكلاء الذكاء الاصطناعي طلبك ويردوا خلال 24 ساعة.' },
        tr: { icon: '✅', title: 'Sorgu Başarıyla Gönderildi!', desc: 'Yapay zeka ajanlarımız talebinizi inceleyecek ve 24 saat içinde yanıt verecektir.' },
        fa: { icon: '✅', title: 'درخواست با موفقیت ارسال شد!', desc: 'عامل‌های هوش مصنوعی ما درخواست شما را بررسی و ظرف ۲۴ ساعت پاسخ خواهند داد.' }
    };
    const msg = successMessages[currentLang] || successMessages.en;

    form.innerHTML = `
        <div class="form-success">
            <div class="success-icon">${msg.icon}</div>
            <h3>${msg.title}</h3>
            <p>${msg.desc}</p>
        </div>
    `;
}

// ─── Intersection Observer for Animations ───
const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' };
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// ─── Initialize ───
document.addEventListener('DOMContentLoaded', () => {
    // Apply saved language
    if (currentLang !== 'en') {
        const isRTL = currentLang === 'ar' || currentLang === 'fa';
        document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
        document.documentElement.lang = currentLang;

        // Mark correct button as active
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.textContent.trim() === currentLang.toUpperCase() ||
                (currentLang === 'ar' && btn.textContent.includes('عربي')) ||
                (currentLang === 'fa' && btn.textContent.includes('فارسی'))) {
                btn.classList.add('active');
            }
        });
    }
    applyTranslations();

    // Animate cards on scroll
    document.querySelectorAll('.service-card, .market-card, .advantage-item, .service-detail').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});
