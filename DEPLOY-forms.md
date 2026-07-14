# Подключение отправки форм

Формы сайта отправляют заявку POST-запросом на `/api/lead`, а серверная функция
[`api/lead.js`](api/lead.js) пересылает её письмом на `LEAD_TO` (i@vllobanov.ru).

## Что нужно

1. Хостинг с поддержкой serverless-функций Node.js (Vercel, Netlify, аналог) **или** свой Node-сервер.
2. Почтовый ящик с доступом по SMTP (например, `robot@storekmv.ru`).

## Переменные окружения

Задать в панели хостинга (значения — из `.env.example`, файл `.env` не коммитить):

| Переменная | Назначение |
|---|---|
| `SMTP_HOST` | адрес SMTP-сервера |
| `SMTP_PORT` | порт (587 STARTTLS или 465 SSL) |
| `SMTP_USER` | логин почты |
| `SMTP_PASS` | пароль/токен почты |
| `LEAD_TO` | получатель заявок — `i@vllobanov.ru` |
| `LEAD_FROM` | адрес отправителя |

## Vercel

- Функция автоматически поднимается из папки `api/` (`/api/lead`).
- `package.json` с `nodemailer` уже есть — Vercel установит зависимость.
- Переменные окружения: Project → Settings → Environment Variables.

## Netlify

- Netlify ищет функции в `netlify/functions/`. Либо перенесите `api/lead.js` туда,
  либо добавьте в `netlify.toml`: `[functions] directory = "api"` и роут `/api/lead`.
- Сигнатура Netlify — `exports.handler = async (event) => {...}`; текущий файл написан
  под Vercel `(req, res)`. Для Netlify адаптируйте обёртку (тело в `event.body`, ответ `return {statusCode, body}`).

## Проверка

```bash
curl -X POST https://storekmv.ru/api/lead \
  -H 'Content-Type: application/json' \
  -d '{"name":"Тест","phone":"+70000000000","consent":true}'
# ожидается {"ok":true} и письмо на LEAD_TO
```

## Защита

- Honeypot-поле `fwebsite` отсекается и на клиенте, и на сервере.
- Согласие на ПДн (`consent`) проверяется на сервере — без него 422.
- Рекомендуется добавить rate-limit на уровне хостинга (например, лимит запросов на IP).

## Метрика

В `index.html` при успешной отправке вызывается `ym(window.YM_ID,'reachGoal','lead_submit')`.
После подключения Яндекс.Метрики задайте `window.YM_ID` и создайте цель `lead_submit`.
