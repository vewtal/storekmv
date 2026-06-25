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
| Главная (`index.html`) | Готова (placeholder-фото) |
| Каталог (`warehouses.html`) | Готов (фильтры, карточки) |
| Дизайн-система | Два варианта в `DESIGN.md` и `intercom/DESIGN.md` |
| Формы лидогенерации | Stub — нужен backend endpoint |
| Яндекс.Метрика | Не подключена |
| Реальные фото | Нужны (сейчас placeholders) |
| Деплой | Не выполнен |

---

## Ближайшие задачи

1. Добавить реальные фото складов (все корпуса + территория)
2. Подключить backend для форм (Tilda Forms / собственный endpoint)
3. Интегрировать Яндекс.Метрику + цели
4. Деплой: Tilda Business или собственный хостинг
5. SEO: sitemap.xml, микроразметка, alt-тексты

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
