"""Сохраняет текущие рейтинги Untappd в data/untappd.csv.

Этот файл — резервная копия для блока «Оценки в Untappd» (на случай, если лист
с рейтингами в Google-таблице недоступен) и стартовые данные для этого листа.
Колонки те же, что пишет integrations/untappd.gs.

Запуск: python3 where-to-buy/tools/untappd_snapshot.py
"""
import csv
import re
import urllib.request
from datetime import date
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "untappd.csv"
FIELDS = ["key", "beer", "url", "rating", "ratings", "updated", "quote", "quote_author"]

# Сопоставлено по этикеткам банок (крепость и IBU совпадают с карточками на Untappd).
BEERS = [
    ("brewery", "Robim Good Brewery", "https://untappd.com/Robim_Good_Brewery"),
    ("vista", "FACTORY I.P.A Vista", "https://untappd.com/b/robim-good-brewery-factory-ipa-vista/6753498"),
    ("bbq", "FACTORY TOMATO BBQ", "https://untappd.com/b/robim-good-brewery-bbq-tomato-beer/6798506"),
    ("strata", "IPA American Strata", "https://untappd.com/b/robim-good-brewery-factory-ipa-strata/6860636"),
    ("zlager", "Zero Lager", "https://untappd.com/b/robim-good-brewery-robim-good-zero/6772340"),
    ("zipa", "Zero IPA", "https://untappd.com/b/robim-good-brewery-robim-good-zero-ipa/6772342"),
    ("zstout", "Zero Stout", "https://untappd.com/b/robim-good-brewery-robim-good-zero-stout/6851862"),
]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
RATING = re.compile(r'"aggregateRating":\{[^}]*?"ratingValue":([\d.]+)[^}]*?"reviewCount":(\d+)')


def main():
    old = {r["key"]: r for r in csv.DictReader(OUT.open(encoding="utf-8"))} if OUT.exists() else {}
    rows = []
    for key, beer, url in BEERS:
        html = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read().decode("utf-8")
        m = RATING.search(html)
        prev = old.get(key, {})
        rows.append({
            "key": key, "beer": beer, "url": url,
            "rating": round(float(m.group(1)), 3) if m else prev.get("rating", ""),
            "ratings": m.group(2) if m else prev.get("ratings", ""),
            "updated": date.today().isoformat() if m else prev.get("updated", ""),
            "quote": prev.get("quote", ""), "quote_author": prev.get("quote_author", ""),
        })
        print(f"{beer}: {rows[-1]['rating']} ({rows[-1]['ratings']})")
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
