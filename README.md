# storekmv.ru — Сайт складского комплекса

Проект: разработка и запуск нового сайта [storekmv.ru](https://storekmv.ru)

**Концепция:** сайт продаёт не отдельные склады, а light industrial кластер.

---

## Структура проекта

```
storekmv-website/
├── index.html              # Главная страница (10 секций, адаптив)
├── pages/
│   └── warehouses.html     # Каталог складов с фильтрами
├── css/
│   └── styles.css
├── js/
│   └── main.js
├── intercom/
│   └── DESIGN.md           # Design system: Intercom-inspired (warm cream, Fin Orange)
├── DESIGN.md               # Design system: Stripe-inspired (deep navy, purple)
└── docs/                   # Вся аналитика и документация по проекту
    ├── PRD.md              # PRD сайта v1.0 — IA, UX flows, SEO, roadmap
    ├── complex-data.md     # Данные по комплексу: объекты, ставки, арендаторы
    ├── diversification-strategy.md  # 5 вариантов диверсификации → 3 млн руб./мес.
    └── warehouse-strategy.md        # Сводная стратегия СКФО (knowledge base)
```

---

## Статус сайта

| Что | Статус |
|-----|--------|
| Главная (`index.html`) | Готова: 7 направлений, реальные фото, интерактивный генплан |
| Каталог (`pages/warehouses.html`) | Готов: фильтры, карточки по 7 объектам |
| Техника (`pages/equipment.html`) | Готова: 10 позиций Kandela с фото и ценами |
| Инвесторам (`pages/investors.html`) | Готова |
| Маркетплейсы | `#marketplaces` (фулфилмент) + `#wb-hub` (помещение под хаб WB) |
| Формы лидогенерации | Код готов (`api/lead.js`); нужен деплой функции и SMTP |
| Яндекс.Метрика | Не подключена — нужен номер счётчика |
| SEO | title/description/OG, og:image 1200×630, LocalBusiness, robots, sitemap |
| Деплой | Не выполнен: на домене старая версия Tilda |

---

## Ближайшие задачи

1. Опубликовать на Tilda — см. [DEPLOY-tilda.md](DEPLOY-tilda.md)
2. Задеплоить функцию форм и прописать SMTP — см. [DEPLOY-forms.md](DEPLOY-forms.md)
3. Подключить Яндекс.Метрику и цель `lead_submit`
4. Подать заявку в программу партнёрских хабов RWB (`docs/wb-hub-application.md`)
5. Фотосессия номеров гостиницы «Атмосфера» — блокер лендинга гостиницы

---

## Документация

- [PRD сайта](docs/PRD.md) — полный product requirements document
- [Данные по комплексу](docs/complex-data.md) — объекты, ставки, арендаторы, контакты
- [Стратегия диверсификации](docs/diversification-strategy.md) — 5 вариантов → 3 млн/мес.
- [Warehouse стратегия](docs/warehouse-strategy.md) — сводный анализ СКФО-рынка

---

## Ключевые параметры

**Адрес:** г. Георгиевск, ул. Октябрьская 155, Ставропольский край  
**Площадь:** 11 741 м² (7 складских корпусов)  
**Текущая выручка:** ~650–730 тыс. руб./мес.  
**Цель:** 3 000 000 руб./мес. за 18 месяцев  
**Контакт:** +7 928 630 63 44 · storekmv.ru
