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
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"

# Картинки отдаются с CDN публичного репозитория. После загрузки файлов в файловый
# менеджер Tilda достаточно поменять эту строку на адрес static.tildacdn.com.
ASSETS_BASE = "https://cdn.jsdelivr.net/gh/vewtal/storekmv@main"

# Адрес serverless-функции приёма заявок. Пустая строка — оставить относительный путь.
LEAD_ENDPOINT = "https://storekmv-api.vercel.app/api/lead"

# PDF-документы (презентация) загружаются в файловый менеджер Tilda вручную: каталог
# docs/ не хранится в репозитории, поэтому CDN его не отдаст. После загрузки скопировать
# сюда адрес папки вида "https://static.tildacdn.com/lib/..." без слэша на конце.
# Пустая строка — оставить относительный путь: для локальной версии он рабочий, а сборка
# напомнит, что ссылку на Tilda ещё предстоит подставить.
DOCS_BASE = "https://cdn.jsdelivr.net/gh/vewtal/storekmv@main/files"
# Счётчик Яндекс.Метрики проекта Tilda (подключён в настройках сайта Tilda), нужен для целей
YM_ID = 102592411

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
    """Относительные пути к картинкам и документам -> абсолютные адреса.

    Ловит и атрибуты (src="img/...", href="../img/..."), и строки внутри скриптов
    (photo:'../img/equipment/...') — на странице техники фото задаются данными, а не
    разметкой, и без этого они на Tilda не загрузятся.

    Картинки идут с CDN репозитория, PDF из docs/ — из файлового менеджера Tilda:
    каталог не хранится в git, поэтому CDN его отдать не может. Пока DOCS_BASE пуст,
    ссылки на документы остаются относительными.
    """
    html = re.sub(r"(['\"])\.\./img/", rf"\1{ASSETS_BASE}/img/", html)
    html = re.sub(r"(['\"])img/", rf"\1{ASSETS_BASE}/img/", html)
    if DOCS_BASE:
        html = re.sub(r"(['\"])\.\./docs/", rf"\1{DOCS_BASE}/", html)
        html = re.sub(r"(['\"])docs/", rf"\1{DOCS_BASE}/", html)
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
            f'<script>window.STOREKMV_LEAD_ENDPOINT="{LEAD_ENDPOINT}";window.YM_ID={YM_ID};</script>'
        )
    parts.extend(styles)
    parts.append(body.strip())

    out = "\n".join(parts)
    out = rewrite_assets(out)
    out = rewrite_links(out)
    return out


def check_scripts(html: str) -> list[str]:
    """Синтаксис каждого встроенного скрипта через `node --check`.

    Ловит класс ошибок, которые проверка путей не видит. Пример из истории проекта:
    строка с закрывающим тегом script внутри JS-комментария — браузер закрывает на ней
    весь блок, скрипт обрывается на середине, и на странице молча перестают работать
    формы, модалки и калькулятор. Без node проверка пропускается с предупреждением.
    """
    node = shutil.which("node")
    if not node:
        return ["node не найден — синтаксис скриптов не проверен"]
    problems = []
    blocks = re.findall(r"<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>", html, re.S)
    for i, (attrs, body) in enumerate(blocks):
        if "ld+json" in attrs or not body.strip():
            continue
        # Прямой детектор причины: тег script внутри кода. node --check его не всегда
        # видит — если обрыв пришёлся на валидное место, синтаксис чистый, а хвост кода
        # браузер выведет текстом прямо на страницу.
        if "<script" in body.lower():
            problems.append(f"скрипт #{i}: внутри кода есть тег script — браузер оборвёт блок")
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(body)
            path = f.name
        res = subprocess.run([node, "--check", path], capture_output=True, text=True)
        pathlib.Path(path).unlink(missing_ok=True)
        if res.returncode != 0:
            msg = next((l for l in res.stderr.splitlines() if "Error" in l), res.stderr.strip()[:120])
            problems.append(f"скрипт #{i}: {msg}")
    return problems


def check(html: str) -> tuple[list[str], list[str]]:
    """Проверки, которые ловят самые дорогие ошибки сборки.

    Возвращает (ошибки, напоминания). Ошибки роняют сборку, напоминания — нет.
    """
    problems: list[str] = []
    notes: list[str] = []

    # Значения, начинающиеся с кавычки или +, — это склейка строк в скрипте
    # (src="'+esc(p.photo)+'"), а не путь; такие пропускаем.
    leftover = re.findall(
        r"(?:src|href)=\"(?!https?:|/|#|tel:|mailto:|data:|'|\"|\+)[^\"]*", html
    )
    # Ссылки на docs/ ждут адрес файлового менеджера Tilda в DOCS_BASE — это не ошибка
    # сборки, а напоминание загрузить файл и подставить адрес.
    pending_docs = [p for p in leftover if "docs/" in p]
    leftover = [p for p in leftover if "docs/" not in p]
    if leftover:
        problems.append(f"остались относительные пути: {sorted(set(leftover))[:5]}")
    if pending_docs:
        notes.append(
            f"документы ждут DOCS_BASE (загрузить в файловый менеджер Tilda): "
            f"{sorted(set(pending_docs))[:3]}"
        )

    if re.search(r"<html|<head>|<body", html):
        problems.append("в вывод попали теги документа (<html>/<head>/<body>)")

    stale = re.findall(r'href="[^"]*\.html[^"]*"', html)
    if stale:
        problems.append(f"остались ссылки на .html: {sorted(set(stale))[:5]}")

    problems.extend(check_scripts(html))

    return problems, notes


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

        problems, notes = check(html)
        status = "ok" if not problems else "ПРОВЕРИТЬ"
        size_kb = len(html.encode("utf-8")) / 1024
        print(f"  {out_path.relative_to(ROOT)}  ->  {url}   {size_kb:6.1f} КБ   {status}")
        for p in problems:
            print(f"      ! {p}")
            failures += 1
        for n in notes:
            print(f"      · {n}")

    print(f"\nКартинки:     {ASSETS_BASE}/img/...")
    print(f"Документы:    {DOCS_BASE or 'DOCS_BASE не задан — ссылки относительные'}")
    print(f"Форма заявок: {LEAD_ENDPOINT or 'относительный /api/lead'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
