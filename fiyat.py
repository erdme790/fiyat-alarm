import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import re

URL = "BURAYA_URUN_LINKI"
DOSYA = "fiyat.txt"

MAIL = os.environ["MAIL"]
SIFRE = os.environ["SIFRE"]

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=headers)
soup = BeautifulSoup(r.text, "html.parser")

# ⬇️ BURAYI SİTEYE GÖRE GÜNCELLE
fiyat_yazi = soup.select_one("span.price").get_text(strip=True)

print("Ham fiyat:", fiyat_yazi)

fiyat = float(
    re.sub(r"[^\d,]", "", fiyat_yazi)
    .replace(".", "")
    .replace(",", ".")
)

print("Güncel fiyat:", fiyat)

if os.path.exists(DOSYA):
    with open(DOSYA) as f:
        onceki = float(f.read())
else:
    onceki = fiyat

mesaj_icerik = f"""
Ürün kontrol edildi.

Önceki fiyat: {onceki} ₺
Güncel fiyat: {fiyat} ₺

{URL}
"""

mesaj = MIMEText(mesaj_icerik)
mesaj["Subject"] = "📦 Fiyat Kontrol Sonucu"
mesaj["From"] = MAIL
mesaj["To"] = MAIL

s = smtplib.SMTP("smtp.gmail.com", 587)
s.starttls()
s.login(MAIL, SIFRE)
s.send_message(mesaj)
s.quit()

with open(DOSYA, "w") as f:
    f.write(str(fiyat))

print("Mail gönderildi ✅")
