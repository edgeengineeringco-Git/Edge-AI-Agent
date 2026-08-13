/* ============================================
   EDGE — Interactive JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

    // ---------- Nav scroll effect ----------
    const navWrapper = document.querySelector('.nav-wrapper');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const scroll = window.scrollY;
        if (scroll > 50) {
            navWrapper.classList.add('scrolled');
        } else {
            navWrapper.classList.remove('scrolled');
        }
        lastScroll = scroll;
    });

    // ---------- Mobile menu toggle ----------
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navToggle.classList.toggle('active');
            navLinks.classList.toggle('active');
        });

        // Close on link click
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navToggle.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });
    }

    // ---------- Scroll reveal (Intersection Observer) ----------
    const reveals = document.querySelectorAll('.reveal');
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });

    reveals.forEach(el => revealObserver.observe(el));

    // ---------- Animated counters ----------
    const counters = document.querySelectorAll('[data-count]');
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.dataset.count);
                const suffix = el.dataset.suffix || '';
                const duration = 2000;
                const start = performance.now();

                const animate = (now) => {
                    const elapsed = now - start;
                    const progress = Math.min(elapsed / duration, 1);
                    const eased = 1 - Math.pow(1 - progress, 3);
                    const current = Math.floor(eased * target);
                    el.textContent = current + suffix;
                    if (progress < 1) {
                        requestAnimationFrame(animate);
                    } else {
                        el.textContent = target + suffix;
                    }
                };

                requestAnimationFrame(animate);
                counterObserver.unobserve(el);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(c => counterObserver.observe(c));

    // ---------- Typing effect for hero ----------
    const typedEl = document.querySelector('.hero-typed-text');
    if (typedEl) {
        const phrases = JSON.parse(typedEl.dataset.phrases || '[""]');
        let phraseIdx = 0;
        let charIdx = 0;
        let isDeleting = false;

        const typeEffect = () => {
            const current = phrases[phraseIdx];

            if (isDeleting) {
                typedEl.textContent = current.substring(0, charIdx - 1);
                charIdx--;
            } else {
                typedEl.textContent = current.substring(0, charIdx + 1);
                charIdx++;
            }

            let delay = isDeleting ? 40 : 80;

            if (!isDeleting && charIdx === current.length) {
                delay = 2500;
                isDeleting = true;
            } else if (isDeleting && charIdx === 0) {
                isDeleting = false;
                phraseIdx = (phraseIdx + 1) % phrases.length;
                delay = 400;
            }

            setTimeout(typeEffect, delay);
        };

        setTimeout(typeEffect, 2000);
    }

    // ---------- Floating particles canvas ----------
    const canvas = document.getElementById('particles');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let particles = [];
        let animationId;

        const resizeCanvas = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        class Particle {
            constructor() {
                this.reset();
                this.y = Math.random() * canvas.height;
            }

            reset() {
                this.x = Math.random() * canvas.width;
                this.y = canvas.height + 10;
                this.size = Math.random() * 2 + 0.5;
                this.speedY = Math.random() * 0.6 + 0.2;
                this.speedX = (Math.random() - 0.5) * 0.3;
                this.opacity = Math.random() * 0.4 + 0.1;
                this.colors = ['#10b981', '#06b6d4', '#3b82f6'];
                this.color = this.colors[Math.floor(Math.random() * this.colors.length)];
            }

            update() {
                this.y -= this.speedY;
                this.x += this.speedX;
                if (this.y < -10) this.reset();
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.globalAlpha = this.opacity;
                ctx.fill();
                ctx.globalAlpha = 1;
            }
        }

        const createParticles = () => {
            particles = [];
            const count = Math.min(60, Math.floor(canvas.width / 25));
            for (let i = 0; i < count; i++) {
                particles.push(new Particle());
            }
        };
        createParticles();
        window.addEventListener('resize', () => {
            resizeCanvas();
            createParticles();
        });

        const animateParticles = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                p.update();
                p.draw();
            });
            animationId = requestAnimationFrame(animateParticles);
        };
        animateParticles();
    }

    // ---------- Smooth anchor scroll with offset ----------
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                const offset = 80;
                const pos = target.getBoundingClientRect().top + window.scrollY - offset;
                window.scrollTo({ top: pos, behavior: 'smooth' });
            }
        });
    });

    // ---------- Contact form (demo — connects to Formspree or similar) ----------
    const contactForm = document.querySelector('.contact-form-card form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = contactForm.querySelector('button[type="submit"]') || contactForm.querySelector('.btn');
            if (btn) {
                const originalText = btn.innerHTML;
                btn.innerHTML = 'Sending...';
                btn.disabled = true;

                setTimeout(() => {
                    btn.innerHTML = '✓ Message Sent!';
                    btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';

                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.style.background = '';
                        btn.disabled = false;
                        contactForm.reset();
                    }, 3000);
                }, 1500);
            }
        });
    }

    // ---------- Newsletter form ----------
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = newsletterForm.querySelector('button');
            const input = newsletterForm.querySelector('input');
            if (input.value.trim()) {
                const original = btn.innerHTML;
                btn.innerHTML = '✓';
                setTimeout(() => {
                    btn.innerHTML = original;
                    input.value = '';
                }, 2000);
            }
        });
    }

});
