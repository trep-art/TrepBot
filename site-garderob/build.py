#!/usr/bin/env python3
"""Собирает index.html в готовый к публикации сайт: dist/

index.html написан как артефакт — без <!doctype>, <html> и <head>: их
добавляет платформа Claude. Для настоящего хостинга нужен полный документ
с мета-тегами, Open Graph и разметкой Schema.org, иначе Яндекс и Google
не поймут, что это за страница и чей это магазин.

Запуск:
    python3 inject.py   # сначала вшить фото: photos/ + index.src.html -> index.html
    python3 build.py    # затем собрать dist/

Результат: dist/ — index.html, robots.txt, sitemap.xml, favicon.svg, og.jpg
"""
import pathlib, re, json, datetime, shutil

HERE = pathlib.Path(__file__).parent
DIST = HERE / "dist"

# ─── ЗАМЕНИТЬ НА ДАННЫЕ КЛИЕНТА ПЕРЕД ПУБЛИКАЦИЕЙ ───────────────────────
SITE  = "https://garderob-store.ru"       # домен клиента, без слэша на конце
BRAND = "Garderob Store"
DESC  = ("Garderob Store — женская одежда, обувь и аксессуары в Казани и Набережных "
         "Челнах. Новинки несколько раз в неделю, примерка без предоплаты, "
         "бронь вещи на 24 часа. Девять залов, доставка по России.")
TG_CHANNEL = "https://t.me/garderob_store_chelny"
TG_MANAGER = "https://t.me/garderobstore_chelnyy"
GIS = "https://2gis.ru/nabchelny/geo/70000001084250399"
MAIN_PHONE = "+79393069177"

SHOPS = [
    ("Казань", "ул. Четаева, 35",            "+79053190593"),
    ("Казань", "ул. Спартаковская, 2",        "+79393069177"),
    ("Казань", "ул. Декабристов, 127",        "+79393695002"),
    ("Казань", "ул. Зорге, 60",               "+79393413310"),
    ("Казань", "ул. Декабристов, 83",         "+79655835259"),
    ("Казань", "пр. Победы, 139к1",           "+79656009028"),
    ("Набережные Челны", "пр. Вахитова, 32 (21/25), ЖК «Цезарь»", MAIN_PHONE),
    ("Набережные Челны", "Сармановский тракт, 53",                MAIN_PHONE),
    ("Набережные Челны", "ул. Яшьлек, 6Б/1",                      MAIN_PHONE),
]
HOURS = [{"@type": "OpeningHoursSpecification",
          "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
          "opens": "10:00", "closes": "21:00"}]
# ────────────────────────────────────────────────────────────────────────

body = (HERE / "index.html").read_text(encoding="utf-8")
title = re.search(r"<title>(.*?)</title>", body, re.S).group(1).strip()
body = re.sub(r'<meta name="claude:[^>]*>\s*', "", body)
body = re.sub(r"<title>.*?</title>\s*", "", body, count=1, flags=re.S)

graph = [{
    "@type": "ClothingStore",
    "@id": f"{SITE}/#brand",
    "name": BRAND,
    "description": DESC,
    "url": f"{SITE}/",
    "telephone": MAIN_PHONE,
    "image": f"{SITE}/og.jpg",
    "priceRange": "149–8990 ₽",
    "currenciesAccepted": "RUB",
    "paymentAccepted": "Наличные, банковская карта, СБП",
    "areaServed": ["Казань", "Набережные Челны", "Россия"],
    "sameAs": [TG_CHANNEL, GIS],
    "openingHoursSpecification": HOURS,
    "address": {"@type": "PostalAddress", "addressLocality": SHOPS[0][0],
                "streetAddress": SHOPS[0][1], "addressCountry": "RU"},
}]
for i, (city, street, phone) in enumerate(SHOPS, 1):
    graph.append({
        "@type": "ClothingStore",
        "@id": f"{SITE}/#shop-{i}",
        "name": f"{BRAND} — {street}",
        "parentOrganization": {"@id": f"{SITE}/#brand"},
        "url": f"{SITE}/",
        "telephone": phone,
        "openingHoursSpecification": HOURS,
        "address": {"@type": "PostalAddress", "addressLocality": city,
                    "streetAddress": street, "addressCountry": "RU"},
    })
# Оценки (aggregateRating) намеренно не размечены: это допустимо только при
# реальных отзывах на сайте, иначе поисковики снимают расширенный сниппет.
jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph},
                    ensure_ascii=False, indent=1)

head = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} — женская одежда и обувь в Казани и Набережных Челнах</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{SITE}/">
<meta name="theme-color" content="#F7F5F2">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{BRAND} — примерьте то, что завтра уже разберут">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{SITE}/">
<meta property="og:image" content="{SITE}/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
  :root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
  body{{margin:0;font:14px system-ui,sans-serif}}
  img{{max-width:100%}}
  [hidden]{{display:none!important}}
</style>
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
"""

DIST.mkdir(exist_ok=True)
(DIST / "index.html").write_text(head + body + "\n</body>\n</html>\n", encoding="utf-8")

(DIST / "robots.txt").write_text(
    "User-agent: *\nAllow: /\n"
    "Clean-param: utm_source&utm_medium&utm_campaign&yclid&gclid\n"
    f"Sitemap: {SITE}/sitemap.xml\n", encoding="utf-8")

today = datetime.date.today().isoformat()
(DIST / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f"  <url><loc>{SITE}/</loc><lastmod>{today}</lastmod>"
    "<changefreq>weekly</changefreq><priority>1.0</priority></url>\n"
    "</urlset>\n", encoding="utf-8")

for extra in ("favicon.svg", "og.jpg"):
    f = HERE / extra
    if f.exists():
        shutil.copy(f, DIST / extra)

print("dist собран:", (DIST / "index.html").stat().st_size // 1024, "КБ")
