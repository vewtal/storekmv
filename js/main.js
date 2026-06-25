/* StoreKMV — main.js */
'use strict';

// ---- Mobile Nav ----
const menuToggle = document.getElementById('menuToggle');
const mobileNav  = document.getElementById('mobileNav');
if (menuToggle && mobileNav) {
  menuToggle.addEventListener('click', () => {
    mobileNav.classList.toggle('open');
    menuToggle.setAttribute('aria-expanded', mobileNav.classList.contains('open'));
  });
  document.addEventListener('click', (e) => {
    if (!menuToggle.contains(e.target) && !mobileNav.contains(e.target)) {
      mobileNav.classList.remove('open');
    }
  });
}

// ---- Modal ----
const modalOverlay = document.getElementById('modalOverlay');
const modalClose   = document.getElementById('modalClose');
const modalTitle   = document.getElementById('modalTitle');
const modalDesc    = document.getElementById('modalDesc');

function openModal(title, desc) {
  if (!modalOverlay) return;
  if (modalTitle) modalTitle.textContent = title || 'Оставьте заявку';
  if (modalDesc) modalDesc.textContent = desc || 'Мы свяжемся с вами в течение рабочего дня.';
  modalOverlay.classList.add('active');
  document.body.style.overflow = 'hidden';
}
function closeModal() {
  if (!modalOverlay) return;
  modalOverlay.classList.remove('active');
  document.body.style.overflow = '';
}
if (modalClose) modalClose.addEventListener('click', closeModal);
if (modalOverlay) {
  modalOverlay.addEventListener('click', (e) => { if (e.target === modalOverlay) closeModal(); });
}
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });

// Wire up all CTA buttons
document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-modal]');
  if (!btn) return;
  const type = btn.dataset.modal;
  const titles = {
    'view':    'Записаться на показ',
    'kp':      'Запросить коммерческое предложение',
    '3pl':     'Заявка на 3PL / ответственное хранение',
    'pick':    'Подобрать помещение',
    'present': 'Получить презентацию',
    'invest':  'Запросить инвест-пакет',
  };
  const descs = {
    'view':    'Выберем удобное время для осмотра комплекса.',
    'kp':      'Подготовим индивидуальное предложение под ваши задачи.',
    '3pl':     'Опишите объём и характер груза, подберём сервис.',
    'pick':    'Укажите параметры — подберём оптимальный блок.',
    'present': 'PDF с полным описанием объектов, схемами и ставками.',
    'invest':  'Пакет материалов для инвесторов и BTS-партнёров.',
  };
  openModal(titles[type] || 'Оставьте заявку', descs[type] || '');
});

// ---- Form submit ----
const leadForm = document.getElementById('leadForm');
if (leadForm) {
  leadForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = leadForm.querySelector('[type="submit"]');
    if (btn) { btn.textContent = 'Отправляем…'; btn.disabled = true; }
    // Simulate send (replace with real endpoint)
    setTimeout(() => {
      closeModal();
      showToast('Заявка принята! Мы свяжемся с вами в ближайшее время.');
      leadForm.reset();
      if (btn) { btn.textContent = 'Отправить заявку'; btn.disabled = false; }
    }, 1000);
  });
}

// ---- Toast ----
function showToast(msg) {
  const toast = document.createElement('div');
  toast.style.cssText = `
    position:fixed; bottom:24px; left:50%; transform:translateX(-50%);
    background:#0F1F3D; color:#fff; padding:14px 24px; border-radius:8px;
    font-size:0.9rem; font-weight:500; z-index:3000; white-space:nowrap;
    box-shadow:0 8px 32px rgba(0,0,0,0.3); animation:fadeInUp 0.3s ease;
  `;
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.4s'; }, 3000);
  setTimeout(() => toast.remove(), 3500);
}

// ---- Warehouse filters ----
const filterBtns = document.querySelectorAll('.filter-btn[data-filter]');
const objectCards = document.querySelectorAll('.object-card[data-type]');
filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const f = btn.dataset.filter;
    objectCards.forEach(card => {
      const show = f === 'all' || card.dataset.type === f;
      card.style.display = show ? '' : 'none';
    });
  });
});

// ---- Smooth scroll for anchor links ----
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', (e) => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      mobileNav && mobileNav.classList.remove('open');
    }
  });
});

// ---- Intersection Observer for animations ----
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-in');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });
document.querySelectorAll('.direction-card, .object-card, .li-scenario, .infra-card, .invest-stat')
  .forEach(el => observer.observe(el));

// ---- Phone click tracking (Yandex Metrika stub) ----
document.querySelectorAll('a[href^="tel:"]').forEach(link => {
  link.addEventListener('click', () => {
    if (window.ym) ym(0, 'reachGoal', 'phone_click');
  });
});
