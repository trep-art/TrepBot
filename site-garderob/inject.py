#!/usr/bin/env python3
"""Вшивает фотографии из photos/ в index.src.html и сохраняет index.html.

Артефакты и статические хостинги не дают грузить картинки с чужих доменов
(фото из Telegram по прямой ссылке не откроются), поэтому каждое фото
встраивается в саму страницу как data:URI. Папка photos/ — исходники,
index.html — собранный файл, который и публикуется.

Запуск: python3 inject.py
"""
import base64, pathlib, re
HERE = pathlib.Path(__file__).parent
src = (HERE / "index.src.html").read_text(encoding="utf-8")

def sub(m):
    name = m.group(1)
    f = HERE / "photos" / f"{name}.jpg"
    if not f.exists():
        raise SystemExit(f"нет файла photos/{name}.jpg")
    return "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode()

out = re.sub(r"\{\{PHOTO:([a-z0-9-]+)\}\}", sub, src)
left = re.findall(r"\{\{[^}]+\}\}", out)
if left:
    raise SystemExit(f"остались незаполненные метки: {set(left)}")
(HERE / "index.html").write_text(out, encoding="utf-8")
print(f"index.html собран: {len(out)//1024} КБ")
