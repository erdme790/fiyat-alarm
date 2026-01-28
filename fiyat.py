import requests
from bs4 import BeautifulSoup
import json
import os

URL = "BURAYA_ÜRÜN_LINKİ"
DOSYA = "onceki_fiyat.json"

html = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(html, "html.parser")

fiyat_yazi = soup.find("fiyatspan").text.strip()
fiyat = float(fiyat_yazi.replace(".", "").replace(",", "."))

print("Güncel fiyat:", fiyat)

if os.path.exists(DOSYA):
    with open(DOSYA, "r") as f:
        eski = json.load(f)["fiyat"]

    if fiyat < eski:
        print("🚨 FİYAT DÜŞTÜ! MAIL ATILDI (simülasyon)")
    else:
        print("❌ Fiyat düşmedi ama yine mail atıldı (simülasyon)")
else:
    print("İlk fiyat kaydedildi.")

with open(DOSYA, "w") as f:
    json.dump({"fiyat": fiyat}, f)
