#!/usr/bin/env python3
"""Сборка страниц сайта в самодостаточные блоки для вставки в Tilda (блок T123).

Что делает:
  1. вырезает из страницы <style> и содержимое <body> (Tilda даёт свои <html>/<head>);
  2. переписывает относительные пути картинок на абсолютный CDN-адрес репозитория;
  3. переписывает ссылки между страницами на «чистые» адреса Tilda (/warehouses и т. п.);
  4. подставляет абсолютный адрес функции приёма заявок — на Tilda страница и функция
     живут на разных доменах, относительный /api/lead там не работает.

Запуск:  python3 build-tilda.py
Результат: dist/tilda-<страница>.html — содержимое для блока T123.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"

# Картинки отдаются с CDN публичного репозитория. После загрузки файлов в файловый
# менеджер Tilda достаточно поменять эту строку на адрес static.tildacdn.com.
ASSETS_BASE = "https://cdn.jsdelivr.net/gh/vewtal/storekmv@main"

# Адрес serverless-функции приёма заявок. Пустая строка — оставить относительный путь.
LEAD_ENDPOINT = "https://storekmv-api.vercel.app/api/lead"

# Страницы: исходник -> адрес страницы в Tilda.
PAGES = {
    "index.html": "/",
    "pages/warehouses.html": "/warehouses",
    "pages/equipment.html": "/equipment",
    "pages/investors.html": "/investors",
    "privacy.html": "/privacy",
}

# Ссылки с якорем: заменяется начало значения href, хвост (#rent, #wb-hub) сохраняется.
# Порядок важен: сначала более длинные варианты.
ANCHOR_MAP = [
    ("../index.html#", "/#"),
    ("index.html#", "/#"),
    ("../warehouses.html#", "/warehouses#"),
    ("pages/warehouses.html#", "/warehouses#"),
]

# Ссылки целиком: href совпадает со строкой полностью.
LINK_MAP = [
    ("pages/warehouses.html", "/warehouses"),
    ("pages/equipment.html", "/equipment"),
    ("pages/investors.html", "/investors"),
    ("../warehouses.html", "/warehouses"),
    ("../equipment.html", "/equipment"),
    ("../investors.html", "/investors"),
    ("../privacy.html", "/privacy"),
    ("../index.html", "/"),
    ("warehouses.html", "/warehouses"),
    ("equipment.html", "/equipment"),
    ("investors.html", "/investors"),
    ("privacy.html", "/privacy"),
    ("index.html", "/"),
]

STYLE_RE = re.compile(r"<style>.*?</style>", re.DOTALL)
LDJSON_RE = re.compile(r'<script type="application/ld\+json">.*?</script>', re.DOTALL)
BODY_RE = re.compile(r"<body[^>]*>(.*)</body>", re.DOTALL)
FONTS_RE = re.compile(r"<link[^>]+fonts\.googleapis\.com[^>]*>")


def rewrite_assets(html: str) -> str:
    """Относительные пути к картинкам -> абсолютные адреса CDN.

    Ловит и атрибуты (src="img/...", href="../img/..."), и строки внутри скриптов
    (photo:'../img/equipment/...') — на странице техники фото задаются данными, а не
    разметкой, и без этого они на Tilda не загрузятся.
    """
    html = re.sub(r"(['\"])\.\./img/", rf"\1{ASSETS_BASE}/img/", html)
    html = re.sub(r"(['\"])img/", rf"\1{ASSETS_BASE}/img/", html)
    return html


def rewrite_links(html: str) -> str:
    """Ссылки между страницами -> адреса страниц Tilda."""
    for src, dst in ANCHOR_MAP:
        html = html.replace(f'href="{src}', f'href="{dst}')
    for src, dst in LINK_MAP:
        html = html.replace(f'href="{src}"', f'href="{dst}"')
    return html


def build_page(src_path: pathlib.Path) -> str:
    raw = src_path.read_text(encoding="utf-8")

    styles = STYLE_RE.findall(raw)
    if not styles:
        raise SystemExit(f"{src_path}: не найден блок <style>")

    body_match = BODY_RE.search(raw)
    if not body_match:
        raise SystemExit(f"{src_path}: не найден <body>")
    body = body_match.group(1)

    parts: list[str] = []
    parts.append(
        "<!-- StoreKMV: содержимое блока T123. Собрано build-tilda.py, "
        "править исходник в репозитории, не здесь. -->"
    )
    parts.extend(FONTS_RE.findall(raw))
    parts.extend(LDJSON_RE.findall(raw))
    if LEAD_ENDPOINT:
        parts.append(
            f'<script>window.STOREKMV_LEAD_ENDPOINT="{LEAD_ENDPOINT}";</script>'
        )
    parts.extend(styles)
    parts.append(body.strip())

    out = "\n".join(parts)
    out = rewrite_assets(out)
    out = rewrite_links(out)
    return out


def check(html: str) -> list[str]:
    """Проверки, которые ловят самые дорогие ошибки сборки."""
    problems = []

    # Значения, начинающиеся с кавычки или +, — это склейка строк в скрипте
    # (src="'+esc(p.photo)+'"), а не путь; такие пропускаем.
    leftover = re.findall(
        r"(?:src|href)=\"(?!https?:|/|#|tel:|mailto:|data:|'|\"|\+)[^\"]*", html
    )
    if leftover:
        problems.append(f"остались относительные пути: {sorted(set(leftover))[:5]}")

    if re.search(r"<html|<head>|<body", html):
        problems.append("в вывод попали теги документа (<html>/<head>/<body>)")

    stale = re.findall(r'href="[^"]*\.html[^"]*"', html)
    if stale:
        problems.append(f"остались ссылки на .html: {sorted(set(stale))[:5]}")

    return problems


def main() -> int:
    DIST.mkdir(exist_ok=True)
    failures = 0

    for rel, url in PAGES.items():
        src = ROOT / rel
        if not src.exists():
            print(f"  пропуск {rel}: файла нет")
            continue

        html = build_page(src)
        name = "index" if rel == "index.html" else pathlib.Path(rel).stem
        out_path = DIST / f"tilda-{name}.html"
        out_path.write_text(html, encoding="utf-8")

        problems = check(html)
        status = "ok" if not problems else "ПРОВЕРИТЬ"
        size_kb = len(html.encode("utf-8")) / 1024
        print(f"  {out_path.relative_to(ROOT)}  ->  {url}   {size_kb:6.1f} КБ   {status}")
        for p in problems:
            print(f"      ! {p}")
            failures += 1

    print(f"\nКартинки:     {ASSETS_BASE}/img/...")
    print(f"Форма заявок: {LEAD_ENDPOINT or 'относительный /api/lead'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
