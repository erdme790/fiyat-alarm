import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.itopya.com/the-vok-v7-amd-ryzen-5-7600-gigabyte-geforce-rtx-5070-12gb-16gb-ddr5-1tb-m2-ssd-oem-paket_h31967"

r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

# 🎯 DOĞRU SEÇİCİ
fiyat_yazi = soup.select_one("span.price").get_text(strip=True)

print("Ham fiyat:", fiyat_yazi)

fiyat = float(
    re.sub(r"[^\d,]", "", fiyat_yazi)
    .replace(".", "")
    .replace(",", ".")
)

print("Fiyat (sayı):", fiyat)
