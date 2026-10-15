"""Типографика для страниц StoreKMV: неразрывные пробелы, чтобы числа не отрывались
от единиц, предлоги — от слов, тире — от предыдущего слова, телефон не переносился.
Обрабатывает только видимый текст HTML и строки JS с кириллицей; <style>, ld+json
и атрибуты тегов не трогает. Повторный запуск ничего не меняет.

Запуск: python3 typo.py index.html pages/*.html privacy.html"""
import re
import sys

NB = ' '
UNITS = r'(м²|м³|м|кВт|₽|°C|°|га|км|мес\.?|т/м²|час|ч|%|тыс\.?|млн|млрд|руб\.?|л|шт\.?)'
RULES = [
    (re.compile(r'(\d) (\d{3})(?!\d)'), r'\1' + NB + r'\2'),
    (re.compile(r'(\d) (\d{3})(?!\d)'), r'\1' + NB + r'\2'),
    (re.compile(r'(\d) ' + UNITS + r'(?![А-Яа-яЁёA-Za-z])'), r'\1' + NB + r'\2'),
    (re.compile(r'(\d) (Лит\.)'), r'\1' + NB + r'\2'),
    (re.compile(r'(?<=[^\s>]) (—|–)(?= )'), NB + r'\1'),
    (re.compile(r'(?<![А-Яа-яЁё])(от|до|по|за|на|из|под|над|при|без|для|не|и|в|с|к|о|у|а|В|С|К|О|У|И|А|От|До|По|За|На|Из|Для|Не) (?=[«(+№]?[\w\-]{1,9}(?![\w\-])|\d)'), r'\1' + NB),  # к длинным словам не клеим: распирают строку на 320 px
]
PHONE = re.compile(r'\+7 928-630-63-44')


def typo(text, html):
    for rx, rep in RULES:
        text = rx.sub(rep, text)
    if html:
        text = PHONE.sub('<span class="nowrap">+7' + NB + '928-630-63-44</span>', text)
    return text


def js_strings(code):
    def fix(m):
        s = m.group(0)
        # короткие строки — это ключи и значения сравнений, их не трогаем
        return typo(s, False) if len(s) > 40 and re.search('[А-Яа-яЁё]', s) else s
    return re.sub(r"'(?:[^'\\\n]|\\.)*'|\"(?:[^\"\\\n]|\\.)*\"", fix, code)


def process(src):
    out, pos = [], 0
    for m in re.finditer(r'<(style|script)\b([^>]*)>(.*?)</\1>', src, re.S):
        out.append(html_text(src[pos:m.start()]))
        tag, attrs, body = m.group(1), m.group(2), m.group(3)
        if tag == 'script' and 'ld+json' not in attrs:
            body = js_strings(body)
        out.append(f'<{tag}{attrs}>{body}</{tag}>')
        pos = m.end()
    out.append(html_text(src[pos:]))
    return ''.join(out)


def html_text(chunk):
    parts = re.split(r'(<[^>]+>)', chunk)
    inside_span_nowrap = False
    for i, part in enumerate(parts):
        if part.startswith('<'):
            inside_span_nowrap = part.startswith('<span class="nowrap">')
            continue
        if not inside_span_nowrap:
            parts[i] = typo(part, True)
    return ''.join(parts)


if __name__ == '__main__':
    for path in sys.argv[1:]:
        src = open(path, encoding='utf-8').read()
        new = process(src)
        if '.nowrap{' not in new:
            new = new.replace('</style>', '.nowrap{white-space:nowrap}\n</style>', 1)
        open(path, 'w', encoding='utf-8').write(new)
        print(path, src.count(NB), '->', new.count(NB))
