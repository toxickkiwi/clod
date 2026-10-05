"""Собирает блок для Tilda и страницу предпросмотра.

    python3 where-to-buy/build.py

dist/tilda-block.html     — версия 1 (поиск по городу, список и карта): вставить целиком в блок «HTML-код» (T123) на Tilda.
dist/tilda-block-v2.html  — версия 2 (только карта со всеми точками, адреса «Точки» в выпадающем списке).
dist/preview.html, dist/preview-v2.html — те же блоки под шапкой, как на сайте, для проверки в браузере.
"""
import base64
import csv
import re
import json
import math
from pathlib import Path

HERE = Path(__file__).parent
DIST = HERE / "dist"

rows = list(csv.DictReader((HERE / "data" / "points.csv").open(encoding="utf-8")))
# Во встроенную копию — только поля, нужные для карты и карточек (без служебных колонок).
PUBLIC_FIELDS = ["city", "name", "type", "address", "phone", "lat", "lng", "tochka", "sorts"]
fallback = json.dumps([{k: r[k] for k in PUBLIC_FIELDS} for r in rows],
                      ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
# Ближайшее метро для минских «Точек» (data/metro-minsk.json). Подпись — только если станция не дальше 1,5 км.
METRO = json.loads((HERE / "data" / "metro-minsk.json").read_text(encoding="utf-8"))


def km(a_lat, a_lng, b_lat, b_lng):
    la1, lo1, la2, lo2 = map(math.radians, (a_lat, a_lng, b_lat, b_lng))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def with_metro(r):
    out = {k: r[k] for k in PUBLIC_FIELDS}
    if r["city"] == "Минск":
        lat, lng = float(r["lat"]), float(r["lng"])
        st = min(METRO, key=lambda s: km(lat, lng, s["lat"], s["lng"]))
        dist = km(lat, lng, st["lat"], st["lng"])
        if dist <= 1.5:
            out["metro"] = {"name": st["name"], "line": st["line"], "km": round(dist, 2)}
    return out


fallback_tochka = json.dumps([with_metro(r) for r in rows if r["tochka"] == "да"],
                             ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
untappd = list(csv.DictReader((HERE / "data" / "untappd.csv").open(encoding="utf-8")))
untappd_json = json.dumps(untappd, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
VARIANTS = [("block.html", "tilda-block.html", "preview.html"),
            ("block-v2.html", "tilda-block-v2.html", "preview-v2.html"),
            ("block-v3.html", "tilda-block-v3.html", "preview-v3.html")]  # v3: только сеть «Точка»
DIST.mkdir(exist_ok=True)

# Предпросмотр: копия шапки сайта на Tilda. На компьютере (больше 980px) это закреплённая
# полупрозрачная полоса T228, от 641 до 980px та же полоса в потоке, на телефоне (до 640px)
# прозрачная закреплённая шапка T280 с меню на весь экран.
NAV = [("Наша пивоварня", "https://robimgood.beer/about"), ("Наше пиво", "https://robimgood.beer"),
       ("Новости", "https://robimgood.beer/news"), ("Галерея", "https://robimgood.beer/gallery"),
       ("Экскурсии", "https://robimgood.beer/beer-excursions"), ("Кейтеринг", "https://robimgood.beer/pivonaprirode"),
       ("Где купить", "https://robimgood.beer/where-can-I-buy"), ("Места продаж ж/б", "https://robimgood.beer/mestaprodazh"),
       ("Контакты", "https://robimgood.beer/contact")]
NAV_MOBILE = [("Наше пиво", "https://robimgood.beer/#rec181732744"), ("Наша пивоварня", "https://robimgood.beer/about"),
              ("Галерея", "https://robimgood.beer/gallery"), ("Новости", "https://robimgood.beer/news"),
              ("Где купить", "https://robimgood.beer/where-can-I-buy"), ("Контакты", "https://robimgood.beer/contact")]
FB = '<svg viewBox="0 0 24 24" width="14" height="14" fill="#fff"><path d="M14 8V6c0-.9.6-1 1-1h3V1h-4c-4 0-5 3-5 5v2H6v4h3v11h5V12h3.5l.5-4z"/></svg>'
IG = '<svg viewBox="0 0 24 24" width="14" height="14" fill="#fff"><path d="M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 8.2a3.2 3.2 0 1 1 0-6.4 3.2 3.2 0 0 1 0 6.4zM17.3 5.5a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4zM12 2c-2.7 0-3 0-4.1.1C4.3 2.2 2.2 4.3 2.1 7.9 2 9 2 9.3 2 12s0 3 .1 4.1c.1 3.6 2.2 5.7 5.8 5.8 1.1.1 1.4.1 4.1.1s3 0 4.1-.1c3.6-.1 5.7-2.2 5.8-5.8.1-1.1.1-1.4.1-4.1s0-3-.1-4.1c-.1-3.6-2.2-5.7-5.8-5.8C15 2 14.7 2 12 2zm0 1.8c2.7 0 3 0 4 .1 2.7.1 4 1.4 4.1 4.1.1 1 .1 1.3.1 4s0 3-.1 4c-.1 2.7-1.4 4-4.1 4.1-1 .1-1.3.1-4 .1s-3 0-4-.1c-2.7-.1-4-1.4-4.1-4.1-.1-1-.1-1.3-.1-4s0-3 .1-4C3.9 5.3 5.3 4 8 3.9c1-.1 1.3-.1 4-.1z"/></svg>'
ACTIVE = ' class="is-active" aria-current="page"'
desk_links = "".join(f'<a href="{u}"{ACTIVE if "mestaprodazh" in u else ""}>{t}</a>' for t, u in NAV)
mob_links = "".join(f'<li><a href="{u}">{t}</a></li>' for t, u in NAV_MOBILE)

header = f"""<header class="t228">
  <a class="t228__logo" href="https://robimgood.beer/"><img src="https://static.tildacdn.biz/tild3965-6637-4262-a534-663832396664/for_tilda.png" alt="Robim Good Brewery"></a>
  <nav class="t228__nav" aria-label="Меню сайта">{desk_links}</nav>
  <div class="t228__soc">
    <a href="https://www.facebook.com/robimgoodbrewery" target="_blank" rel="noopener" aria-label="Facebook">{FB}</a>
    <a href="https://www.instagram.com/robimgoodbrewery" target="_blank" rel="noopener" aria-label="Instagram">{IG}</a>
  </div>
</header>
<header class="t280" id="t280">
  <a class="t280__logo" href="https://robimgood.beer">RobimGood</a>
  <button class="t280__burger" type="button" aria-label="Навигационное меню" aria-expanded="false" aria-controls="t280-menu"><span></span><span></span><span></span><span></span></button>
  <div class="t280__menu" id="t280-menu">
    <ul>{mob_links}</ul>
    <div class="t280__soc">
      <a href="https://www.facebook.com/robimgoodbrewery" target="_blank" rel="noopener" aria-label="Facebook">{FB}</a>
      <a href="https://www.instagram.com/robimgoodbrewery" target="_blank" rel="noopener" aria-label="Instagram">{IG}</a>
    </div>
  </div>
</header>"""

header_css = """
  body { margin: 0; }
  .t228, .t280 { font-family: 'Fira Sans Condensed', Arial, sans-serif; }
  /* Компьютер: T228 */
  .t228 { position: fixed; inset: 0 0 auto 0; z-index: 990; height: 80px; background: rgba(0,0,0,.5);
    display: flex; align-items: center; padding: 0 40px; }
  .t228__logo img { display: block; height: 80px; }
  .t228__nav { flex: 1; display: flex; justify-content: center; flex-wrap: wrap; }
  .t228__nav a { color: #fff; text-decoration: none; font-weight: 600; font-size: 16px; padding: 0 15px; line-height: 44px; transition: color .3s ease-in-out; }
  .t228__nav a:hover, .t228__nav a.is-active { color: #fab040; }
  .t228__soc { display: flex; gap: 14px; }
  .t228__soc a, .t280__soc a { width: 30px; height: 30px; border-radius: 50%; background: #000; display: grid; place-items: center; }
  @media (max-width: 1199px) { .t228__nav a { padding: 0 9px; font-size: 15px; } .t228 { padding: 0 20px; } }
  @media (max-width: 980px) { .t228 { position: static; height: auto; min-height: 80px; flex-wrap: wrap; padding: 8px 20px; } }
  /* Телефон: T280 */
  .t280 { display: none; }
  @media (max-width: 640px) {
    .t228 { display: none; }
    .t280 { display: flex; position: fixed; inset: 0 0 auto 0; z-index: 990; height: 80px; align-items: center; justify-content: space-between; padding: 0 20px; }
    .t280__logo { position: relative; z-index: 2; font-size: 18px; font-weight: 500; text-transform: uppercase; letter-spacing: 2px; color: #000; text-decoration: none; }
    .t280__burger { position: relative; z-index: 2; width: 44px; height: 44px; margin-right: -8px; border: 0; background: none; padding: 12px 8px; cursor: pointer; }
    .t280__burger span { position: absolute; left: 8px; width: 28px; height: 3px; background: #000; transition: .25s ease-in-out; }
    .t280__burger span:nth-child(1) { top: 12px; } .t280__burger span:nth-child(2), .t280__burger span:nth-child(3) { top: 20px; } .t280__burger span:nth-child(4) { top: 28px; }
    .t280.is-open .t280__burger span:nth-child(1), .t280.is-open .t280__burger span:nth-child(4) { top: 20px; width: 0; left: 22px; }
    .t280.is-open .t280__burger span:nth-child(2) { transform: rotate(45deg); }
    .t280.is-open .t280__burger span:nth-child(3) { transform: rotate(-45deg); }
    .t280__menu { position: fixed; inset: 0; background: #ebebeb; display: flex; flex-direction: column; justify-content: center; padding: 80px 20px 40px;
      opacity: 0; visibility: hidden; transition: opacity .3s ease, visibility .3s; }
    .t280.is-open .t280__menu { opacity: 1; visibility: visible; }
    .t280__menu ul { list-style: none; margin: 0; padding: 0; text-align: center; }
    .t280__menu li a { display: block; padding: 6px 0; color: #000; text-decoration: none; font-weight: 300; font-size: 30px; line-height: 1.35; }
    .t280__soc { display: flex; justify-content: center; gap: 12px; margin-top: 32px; }
  }
"""

header_js = """<script>
  (function () {
    var h = document.getElementById('t280'), b = h.querySelector('.t280__burger');
    b.addEventListener('click', function () { var o = h.classList.toggle('is-open'); b.setAttribute('aria-expanded', o); document.body.style.overflow = o ? 'hidden' : ''; });
  })();
</script>"""

for src, block_out, preview_out in VARIANTS:
    pts = fallback_tochka if src == "block-v3.html" else fallback
    block = ((HERE / "src" / src).read_text(encoding="utf-8")
             .replace("{{FALLBACK_JSON}}", pts).replace("{{UNTAPPD_JSON}}", untappd_json))
    # Фото банок встраиваются в блок один раз (объект RG_IMG), чтобы не загружать их на Tilda отдельно.
    used = sorted(set(re.findall(r'data-rg-img="([\w-]+)"', block)))
    images = {n: "data:image/webp;base64," + base64.b64encode((HERE / "img" / f"{n}.webp").read_bytes()).decode() for n in used}
    block = block.replace("{{IMAGES_JSON}}", json.dumps(images))
    (DIST / block_out).write_text(block, encoding="utf-8")
    preview = f"""<!doctype html>
    <html lang="ru">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <title>Где купить Robim Good в банке — Минск и вся Беларусь</title>
    <meta name="description" content="Магазины и бары, где продают баночное пиво Robim Good: Zero IPA, Zero Lager, FACTORY I.P.A Vista и TOMATO BBQ. Найдите ближайшую точку.">
    <style>{header_css}</style>
    </head>
    <body>
    {header}
    {block}
    {header_js}
    </body>
    </html>
    """
    (DIST / preview_out).write_text(preview, encoding="utf-8")
    print(f"{block_out}: {len(block) // 1024} КБ")
print(f"Резервный список: {len(rows)} точек")

