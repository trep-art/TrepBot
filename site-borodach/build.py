#!/usr/bin/env python3
"""Собирает index.html в готовую к публикации страницу dist/index.html.

index.html написан как артефакт: без <!doctype>, <html> и <head> — их
добавляет платформа Claude. Для настоящего хостинга нужен полный документ
с мета-тегами, Open Graph и разметкой Schema.org, иначе поисковики и
соцсети не поймут, что это за страница. Этот скрипт оборачивает тело
страницы в такой документ, не дублируя вёрстку.

Запуск:  python3 build.py
Результат: dist/index.html, dist/robots.txt, dist/sitemap.xml
"""
import pathlib, re, shutil, datetime, json

HERE = pathlib.Path(__file__).parent
DIST = HERE / "dist"

# ─── ЗАМЕНИТЕ НА СВОИ ДАННЫЕ ПЕРЕД ПУБЛИКАЦИЕЙ ──────────────────────────
SITE   = "https://borodach-barber.ru"      # ваш домен, без слэша на конце
NAME   = "Барбершоп «Бородач»"
CITY   = "Москва"
STREET = "ул. Покровка, 14"
ZIP    = "101000"
PHONE  = "+74951122424"
LAT, LON = "55.758600", "37.645400"        # координаты из 2ГИС/Яндекс.Карт
DESC   = ("Барбершоп «Бородач» на Покровке: стрижка, борода опасной бритвой, "
          "камуфляж седины. Первый визит — бритьё и укладка в подарок. "
          "Запись онлайн, Москва, с 2014 года.")
# Ссылки на свои карточки в справочниках — связывают сайт и организацию
SAME_AS = [
    "https://2gis.ru/moscow/firm/0000000000000000",
    "https://yandex.ru/maps/org/borodach/0000000000/",
]
# ────────────────────────────────────────────────────────────────────────

body = (HERE / "index.html").read_text(encoding="utf-8")
title = re.search(r"<title>(.*?)</title>", body, re.S).group(1).strip()
# служебные теги артефакта в обычном браузере не нужны
body = re.sub(r'<meta name="claude:[^>]*>\s*', "", body)
body = re.sub(r"<title>.*?</title>\s*", "", body, count=1, flags=re.S)

jsonld = f"""{{
  "@context": "https://schema.org",
  "@type": "HairSalon",
  "@id": "{SITE}/#barbershop",
  "name": "{NAME}",
  "url": "{SITE}/",
  "telephone": "{PHONE}",
  "priceRange": "1200–7900 ₽",
  "currenciesAccepted": "RUB",
  "paymentAccepted": "Наличные, банковская карта, СБП",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "{STREET}",
    "addressLocality": "{CITY}",
    "postalCode": "{ZIP}",
    "addressCountry": "RU"
  }},
  "geo": {{ "@type": "GeoCoordinates", "latitude": "{LAT}", "longitude": "{LON}" }},
  "openingHoursSpecification": [
    {{ "@type": "OpeningHoursSpecification",
       "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
       "opens": "10:00", "closes": "22:00" }},
    {{ "@type": "OpeningHoursSpecification",
       "dayOfWeek": ["Saturday","Sunday"],
       "opens": "11:00", "closes": "21:00" }}
  ],
  "sameAs": {json.dumps(SAME_AS, ensure_ascii=False)},
  "makesOffer": [
    {{ "@type": "Offer", "itemOffered": {{ "@type": "Service", "name": "Стрижка «Классика»" }},
       "price": "2400", "priceCurrency": "RUB" }},
    {{ "@type": "Offer", "itemOffered": {{ "@type": "Service", "name": "Стрижка и борода «Бородач»" }},
       "price": "3900", "priceCurrency": "RUB" }},
    {{ "@type": "Offer", "itemOffered": {{ "@type": "Service", "name": "«Полный ритуал»" }},
       "price": "6500", "priceCurrency": "RUB" }}
  ]
}}"""
# aggregateRating НЕ добавлен намеренно: разметку оценок можно ставить только
# при реальных отзывах на сайте, иначе Яндекс и Google снимают сниппет.

head = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} — стрижка и борода на Покровке, {CITY}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{SITE}/">
<meta name="theme-color" content="#0A0A0B">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{title} — стрижка, после которой здороваются первыми">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{SITE}/">
<meta property="og:image" content="{SITE}/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
  :root{{color-scheme:dark;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
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
    f"User-agent: *\nAllow: /\nClean-param: utm_source&utm_medium&utm_campaign&yclid&gclid\n"
    f"Sitemap: {SITE}/sitemap.xml\n", encoding="utf-8")

today = datetime.date.today().isoformat()
(DIST / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f"  <url><loc>{SITE}/</loc><lastmod>{today}</lastmod>"
    "<changefreq>weekly</changefreq><priority>1.0</priority></url>\n"
    "</urlset>\n", encoding="utf-8")

favicon = (HERE / "favicon.svg")
if favicon.exists():
    shutil.copy(favicon, DIST / "favicon.svg")

print("Готово:", DIST / "index.html")
