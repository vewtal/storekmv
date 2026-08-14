// Serverless-функция обработки заявок с форм storekmv.ru.
// Принимает POST /api/lead (JSON), отправляет заявку письмом на LEAD_TO.
// Совместима с Vercel Serverless Functions (Node.js). Для Netlify см. DEPLOY-forms.md.
//
// Требуемые переменные окружения (задать в панели хостинга, НЕ коммитить):
//   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS  — доступ к почтовому серверу
//   LEAD_TO   — получатель заявок (например, i@vllobanov.ru)
//   LEAD_FROM — адрес отправителя (например, robot@storekmv.ru)

const nodemailer = require('nodemailer');

const FIELD_LABELS = {
  name: 'Имя',
  company: 'Компания',
  phone: 'Телефон',
  email: 'Email',
  format: 'Формат',
  comment: 'Комментарий',
};

function esc(v) {
  return String(v == null ? '' : v).slice(0, 2000);
}

function buildText(p) {
  const lines = [];
  lines.push('Новая заявка с сайта storekmv.ru');
  lines.push('');
  lines.push('Источник: ' + esc(p.sourceTitle || p.source || 'форма'));
  for (const key of ['name', 'company', 'phone', 'email', 'format', 'comment']) {
    if (p[key]) lines.push(FIELD_LABELS[key] + ': ' + esc(p[key]));
  }
  if (p.context && Object.keys(p.context).length) {
    lines.push('');
    lines.push('Контекст:');
    for (const [k, v] of Object.entries(p.context)) lines.push('  ' + esc(k) + ': ' + esc(v));
  }
  if (p.utm && Object.keys(p.utm).length) {
    lines.push('');
    lines.push('UTM:');
    for (const [k, v] of Object.entries(p.utm)) lines.push('  ' + esc(k) + ': ' + esc(v));
  }
  lines.push('');
  lines.push('Согласие на обработку ПДн: ' + (p.consent ? 'да' : 'НЕТ'));
  lines.push('Страница: ' + esc(p.page));
  lines.push('Время: ' + esc(p.ts));
  return lines.join('\n');
}

// Origins, которым разрешён кросс-доменный POST. Нужны, когда страница живёт на Tilda,
// а функция — на отдельном домене Vercel. Переопределяется переменной окружения
// LEAD_ALLOWED_ORIGINS (список через запятую).
const DEFAULT_ALLOWED_ORIGINS = [
  'https://storekmv.ru',
  'https://www.storekmv.ru',
];

function allowedOrigins() {
  const raw = process.env.LEAD_ALLOWED_ORIGINS;
  if (!raw) return DEFAULT_ALLOWED_ORIGINS;
  return raw.split(',').map((s) => s.trim()).filter(Boolean);
}

function applyCors(req, res) {
  const origin = req.headers && req.headers.origin;
  if (origin && allowedOrigins().includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Vary', 'Origin');
  }
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Max-Age', '86400');
}

module.exports = async function handler(req, res) {
  applyCors(req, res);
  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return;
  }
  if (req.method !== 'POST') {
    res.status(405).json({ ok: false, error: 'method_not_allowed' });
    return;
  }
  let p = req.body;
  if (typeof p === 'string') {
    try { p = JSON.parse(p); } catch (e) { p = null; }
  }
  if (!p || typeof p !== 'object') {
    res.status(400).json({ ok: false, error: 'bad_request' });
    return;
  }
  // honeypot: если бот заполнил скрытое поле — делаем вид, что всё ок, но не отправляем
  if (p.fwebsite) {
    res.status(200).json({ ok: true });
    return;
  }
  // серверная валидация (не доверяем клиенту)
  if (!p.name || !p.phone) {
    res.status(422).json({ ok: false, error: 'missing_required' });
    return;
  }
  if (!p.consent) {
    res.status(422).json({ ok: false, error: 'consent_required' });
    return;
  }

  const to = process.env.LEAD_TO;
  const from = process.env.LEAD_FROM || process.env.SMTP_USER;
  if (!to || !process.env.SMTP_HOST || !process.env.SMTP_USER || !process.env.SMTP_PASS) {
    console.error('lead: SMTP/LEAD_TO env not configured');
    res.status(500).json({ ok: false, error: 'not_configured' });
    return;
  }

  try {
    const transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: Number(process.env.SMTP_PORT) || 587,
      secure: Number(process.env.SMTP_PORT) === 465,
      auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
    });
    await transporter.sendMail({
      from: from,
      to: to,
      replyTo: p.email || undefined,
      subject: 'Заявка с сайта: ' + esc(p.name) + (p.phone ? ' · ' + esc(p.phone) : ''),
      text: buildText(p),
    });
    res.status(200).json({ ok: true });
  } catch (err) {
    console.error('lead: send failed', err && err.message);
    res.status(502).json({ ok: false, error: 'send_failed' });
  }
};
