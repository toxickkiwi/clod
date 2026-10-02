"""Собирает таблицу точек продаж из site/data.json и подбирает координаты.

Результат: where-to-buy/data/points.csv в формате Google-таблицы из брифа
(city, region, name, type, address, phone, lat, lng, tochka, sorts, updated).

Координаты берутся из OpenStreetMap (Nominatim), не чаще 1 запроса в секунду.
Уже найденные адреса кешируются в tools/geocache.json, повторный запуск быстрый.

Запуск: python3 where-to-buy/tools/make_csv.py
"""
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "where-to-buy" / "data" / "points.csv"
CACHE = Path(__file__).with_name("geocache.json")

TOCHKA_REGION = {"Минск": "Минская область", "Бобруйск": "Могилевская область", "Лида": "Гродненская область"}


def partner_type(prefix):
    p = prefix.lower()
    if "бар" in p and ("магазин" in p or "мрп" in p):
        return "Магазин-бар"
    if p.startswith(("магазин", "мрп", "сеть магазинов")):
        return "Магазин"
    return "Бар"  # бар, паб, пивная, кафе, ресторан: пьют на месте


def split_name(raw):
    """'Магазин "Лавка разливного пива"' -> ('Магазин', '«Лавка разливного пива»')."""
    m = re.match(r'^(.*?)"(.+)"\s*(МРП)?$', raw)
    if not m:
        return raw, raw  # 'МРП', 'Магазин пива': название и есть тип
    return m.group(1).strip(), f"«{m.group(2)}»"


def split_city(address, default_city):
    m = re.match(r"^(?:г[.,]|пос\.|п\.|д\.)\s*([^,]+),\s*(.*)$", address)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    m = re.match(r"^Минский р-н,\s*(?:д\.|п\.)\s*([^,]+),\s*(.*)$", address)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return default_city, address


def rows():
    data = json.loads((ROOT / "site" / "data.json").read_text(encoding="utf-8"))
    for p in data["tochka"]:
        yield dict(city=p["city"], region=TOCHKA_REGION[p["city"]], name="«Точка»", type=p["type"],
                   address=p["address"], phone=re.sub(r"[^\d+]", "", p["phone"]), tochka="да")
    for region, items in data["partners"].items():
        for p in items:
            prefix, name = split_name(p["name"])
            city, address = split_city(p["address"], "Минск" if region == "Минск" else "")
            yield dict(city=city, region="Минская область" if region == "Минск" else region, name=name,
                       type=partner_type(prefix), address=address, phone="", tochka="")


# Сокращения в адресах -> полные слова, которые понимает геокодер.
ABBR = [
    (r"\bпр-т\.?\s*", "проспект "), (r"\bпроспект\s+", "проспект "), (r"\bпр\.\s*", "проспект "),
    (r"\bб-р\s*", "бульвар "), (r"\bул\.\s*", "улица "), (r"\bтр-т\b\.?", "тракт"),
    (r"\bш\.\s*", "шоссе "),
]


def street_query(address):
    a = re.sub(r"\(.*?\)", "", address)              # (павильон в ТЦ ...)
    a = re.sub(r",?\s*(?:ТЦ|пав\.|мини-рынок|подземный|фудкорт|остановка).*$", "", a)
    a = re.sub(r",\s*(?:д\.|корп\.|корпус|к\s*\.).*?(?=$)", lambda m: m.group(0) if re.search(r"д\.\s*\d", m.group(0)) else "", a)
    a = re.sub(r"\bд\.\s*(\d)", r"\1", a)
    for pat, rep in ABBR:
        a = re.sub(pat, rep, a)
    a = re.sub(r"\s+", " ", a).strip(" ,.")
    # Номер дома: оставляем только первую часть (63 - 54 -> 63, 8А-2 с 12 -> 8А)
    a = re.sub(r",\s*(?:корп\.|корпус).*$", "", a)
    a = re.sub(r",\s*(\d+[А-Яа-яA-Za-z]?(?:/\d+)?)\s*[-\s].*$", r", \1", a)
    return a


def geocode(cache, city, address):
    key = f"{city}|{address}"
    if key in cache:
        return cache[key]
    street = street_query(address)
    plain = re.sub(r'[()"«»]', " ", address)
    attempts = [
        {"street": street.replace(",", ""), "city": city, "country": "Беларусь"},
        {"q": f"{street}, {city}, Беларусь"},
        {"q": f"{plain}, {city}, Беларусь"},
    ]
    result = None
    for params in attempts:
        if not street and "street" in params:
            continue
        url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
            {**params, "format": "json", "limit": 1, "accept-language": "ru"})
        req = urllib.request.Request(url, headers={"User-Agent": "robimgood-where-to-buy/1.0 (info@robimgood.beer)"})
        time.sleep(1.1)
        hits = json.load(urllib.request.urlopen(req, timeout=30))
        if hits:
            result = {"lat": round(float(hits[0]["lat"]), 6), "lng": round(float(hits[0]["lon"]), 6), "approx": False}
            break
    if result is None:  # хотя бы центр города, чтобы точка была на карте
        url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
            {"city": city, "country": "Беларусь", "format": "json", "limit": 1})
        req = urllib.request.Request(url, headers={"User-Agent": "robimgood-where-to-buy/1.0 (info@robimgood.beer)"})
        time.sleep(1.1)
        hits = json.load(urllib.request.urlopen(req, timeout=30))
        result = {"lat": round(float(hits[0]["lat"]), 6), "lng": round(float(hits[0]["lon"]), 6), "approx": True}
    cache[key] = result
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return result


def main():
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    out, approx = [], []
    for r in rows():
        g = geocode(cache, r["city"], r["address"])
        if g["approx"]:
            approx.append(f'{r["city"]}, {r["address"]} ({r["name"]})')
        out.append({**r, "lat": g["lat"], "lng": g["lng"], "sorts": "", "updated": date.today().isoformat()})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["city", "region", "name", "type", "address", "phone",
                                          "lat", "lng", "tochka", "sorts", "updated"])
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} точек -> {OUT.relative_to(ROOT)}")
    if approx:
        print(f"Только центр города ({len(approx)}), проверьте вручную:", *approx, sep="\n  ", file=sys.stderr)


if __name__ == "__main__":
    main()
