/* ======================================================
   CALCULATOR — rental price estimator
   Pricing tiers (by % of total warehouse area):
     <60%  → base price + 25%
     60-89% → base price + 15%
     ≥90%  → base price
====================================================== */

(function () {
  'use strict';

  const overlay = document.getElementById('calcOverlay');
  const closeBtn = document.getElementById('calcClose');
  const form = document.getElementById('calcForm');
  const warehouseSelect = document.getElementById('calcWarehouse');
  const areaInput = document.getElementById('calcArea');
  const monthsInput = document.getElementById('calcMonths');
  const areaHint = document.getElementById('calcAreaHint');
  const resultEl = document.getElementById('calcResult');
  const breakdownEl = document.getElementById('calcBreakdown');
  const totalEl = document.getElementById('calcTotal');
  const sendBtn = document.getElementById('calcSend');

  if (!overlay) return;

  // Open calculator from card "Рассчитать" buttons
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('[data-calc]');
    if (!btn) return;

    const warehouseKey = btn.dataset.calc;
    const option = warehouseSelect.querySelector('option[value="' + warehouseKey + '"]');
    if (option) {
      warehouseSelect.value = warehouseKey;
      updateAreaHint();
    }
    openCalc();
  });

  closeBtn.addEventListener('click', closeCalc);
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closeCalc();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay.classList.contains('active')) closeCalc();
  });

  function openCalc() {
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    resultEl.style.display = 'none';
    areaInput.focus();
  }

  function closeCalc() {
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  // Recalculate whenever inputs change
  warehouseSelect.addEventListener('change', function () {
    updateAreaHint();
    recalculate();
  });
  areaInput.addEventListener('input', function () {
    updateAreaHint();
    recalculate();
  });
  monthsInput.addEventListener('input', recalculate);
  form.addEventListener('change', recalculate);

  function getSelectedWarehouse() {
    const opt = warehouseSelect.selectedOptions[0];
    return {
      name: opt.value,
      totalArea: parseInt(opt.dataset.area, 10),
      minBlock: parseInt(opt.dataset.min, 10),
      basePrice: parseInt(opt.dataset.price, 10),
    };
  }

  function updateAreaHint() {
    const w = getSelectedWarehouse();
    if (!areaHint) return;
    areaHint.textContent = 'Мин. блок: ' + w.minBlock.toLocaleString('ru') + ' м² · Всего: ' + w.totalArea.toLocaleString('ru') + ' м²';
    areaHint.className = 'form-hint';
  }

  function getServiceCost() {
    const checked = form.querySelector('input[name="services"]:checked');
    if (!checked) return 0;
    const v = checked.value;
    if (v === '2000' || v === '2000b') return 2000;
    if (v === '3000') return 3000;
    return 0;
  }

  function recalculate() {
    const w = getSelectedWarehouse();
    const area = parseFloat(areaInput.value);
    const months = parseFloat(monthsInput.value);

    if (!area || area < 1 || !months || months < 1) {
      resultEl.style.display = 'none';
      return;
    }

    // Validate min block
    if (area < w.minBlock) {
      areaHint.textContent = 'Минимальный блок для этого склада — ' + w.minBlock.toLocaleString('ru') + ' м²';
      areaHint.className = 'form-hint form-hint--error';
      resultEl.style.display = 'none';
      return;
    }

    areaHint.textContent = 'Мин. блок: ' + w.minBlock.toLocaleString('ru') + ' м² · Всего: ' + w.totalArea.toLocaleString('ru') + ' м²';
    areaHint.className = 'form-hint';

    // Price tier
    const pct = area / w.totalArea;
    var multiplier, tierLabel;
    if (pct < 0.6) {
      multiplier = 1.25;
      tierLabel = 'менее 60% от площади склада (+25% к базовой цене)';
    } else if (pct < 0.9) {
      multiplier = 1.15;
      tierLabel = '60–89% от площади склада (+15% к базовой цене)';
    } else {
      multiplier = 1.0;
      tierLabel = '90%+ от площади склада (базовая цена)';
    }

    const pricePerSqm = Math.round(w.basePrice * multiplier);
    const monthlyRent = area * pricePerSqm;
    const serviceCost = getServiceCost();
    const totalCost = (monthlyRent + serviceCost) * months;

    breakdownEl.innerHTML =
      'Склад: <strong>' + w.name + '</strong><br>' +
      'Объём: ' + area.toLocaleString('ru') + ' м² × ' + pricePerSqm.toLocaleString('ru') + ' ₽/м² (' + tierLabel + ')<br>' +
      'Аренда в мес.: ' + monthlyRent.toLocaleString('ru') + ' ₽<br>' +
      (serviceCost > 0 ? 'Доп. услуги: ' + serviceCost.toLocaleString('ru') + ' ₽/мес.<br>' : '') +
      'Срок: ' + months + ' мес.';

    totalEl.textContent = totalCost.toLocaleString('ru') + ' ₽';
    resultEl.style.display = 'block';
  }

  sendBtn.addEventListener('click', function () {
    const w = getSelectedWarehouse();
    const area = areaInput.value;
    const months = monthsInput.value;
    const comment = document.getElementById('fcomment');
    if (comment) {
      comment.value = 'Расчёт: склад ' + w.name + ', ' + area + ' м², ' + months + ' мес. Итого: ' + totalEl.textContent;
    }
    closeCalc();
    const mainOverlay = document.getElementById('modalOverlay');
    if (mainOverlay) {
      mainOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  });

  updateAreaHint();
})();
