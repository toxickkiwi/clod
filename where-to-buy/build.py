"""Собирает блок для Tilda и страницу предпросмотра.

    python3 where-to-buy/build.py

dist/tilda-block.html  — вставить целиком в блок «HTML-код» (T123) на Tilda.
dist/preview.html      — тот же блок под шапкой, похожей на шапку сайта, для проверки в браузере.
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
DIST = HERE / "dist"

rows = list(csv.DictReader((HERE / "data" / "points.csv").open(encoding="utf-8")))
fallback = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
block = (HERE / "src" / "block.html").read_text(encoding="utf-8").replace("{{FALLBACK_JSON}}", fallback)

DIST.mkdir(exist_ok=True)
(DIST / "tilda-block.html").write_text(block, encoding="utf-8")

# Предпросмотр: имитация шапки Tilda (на компьютере она прозрачная поверх первого блока,
# на телефоне — обычная тёмная полоса над ним).
preview = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Где купить Robim Good в банке — Минск и вся Беларусь</title>
<meta name="description" content="Магазины и бары, где продают баночное пиво Robim Good: Zero IPA, Zero Lager, FACTORY I.P.A Vista и TOMATO BBQ. Найдите ближайшую точку.">
<style>
  body {{ margin: 0; }}
  .tilda-menu {{ position: absolute; inset: 0 0 auto 0; height: 80px; z-index: 10; background: rgba(0,0,0,.5);
    display: flex; align-items: center; justify-content: center; color: #fff; font: 600 15px Arial, sans-serif; letter-spacing: .02em; }}
  .tilda-menu img {{ position: absolute; left: 40px; top: 0; height: 80px; }}
  @media (max-width: 899px) {{ .tilda-menu {{ position: static; height: 64px; background: #10202e; }} .tilda-menu img {{ left: 16px; height: 56px; top: 4px; }} }}
</style>
</head>
<body>
<div class="tilda-menu"><img src="https://static.tildacdn.biz/tild3965-6637-4262-a534-663832396664/for_tilda.png" alt="">Шапка сайта на Tilda</div>
{block}
</body>
</html>
"""
(DIST / "preview.html").write_text(preview, encoding="utf-8")
print(f"Готово: {len(rows)} точек в резервном списке, {len(block) // 1024} КБ блок")
