"""Собирает index.html из template.html и data.json.

Запуск: python3 build.py
"""
import json
import re
from html import escape
from pathlib import Path

root = Path(__file__).parent
data = json.loads((root / "data.json").read_text(encoding="utf-8"))
page = (root / "template.html").read_text(encoding="utf-8")


def tel(phone):
    digits = re.sub(r"\D", "", phone)
    return f'<a class="phone" href="tel:+{digits}">{escape(phone)}</a>'


tochka = "".join(
    f"<li><b>{escape(p['type'])} «Точка»</b>, г. {escape(p['city'])}, {escape(p['address'])}"
    + (f" — {tel(p['phone'])}" if p["phone"] else "")
    + "</li>"
    for p in data["tochka"]
)

partners = "".join(
    f'<div class="region"><h4>{escape(region)}</h4><ul class="list">'
    + "".join(f"<li><b>{escape(p['name'])}</b> — {escape(p['address'])}</li>" for p in items)
    + "</ul></div>"
    for region, items in data["partners"].items()
)

# Две одинаковые половины, чтобы бегущая строка шла без разрыва.
marquee = '<span class="marquee__item">Robim Good Brewery</span>' * 24

page = (
    page.replace("{{TOCHKA}}", tochka)
    .replace("{{PARTNERS}}", partners)
    .replace("{{MARQUEE}}", marquee)
)
(root / "index.html").write_text(page, encoding="utf-8")
print("index.html собран")
