import requests
from bs4 import BeautifulSoup
import json
import os
import smtplib
from email.mime.text import MIMEText

URL = "https://www.itopya.com/the-vok-v7-amd-ryzen-5-7600-gigabyte-geforce-rtx-5070-12gb-16gb-ddr5-1tb-m2-ssd-oem-paket_h31967"
DOSYA = "son_fiyat.json"

MAIL = os.environ.get("MAIL_GONDEREN")
SIFRE = os.environ.get("MAIL_SIFRE")
ALICI = os.environ.get("MAIL_ALICI")

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=headers)
soup = BeautifulSoup(r.text, "html.parser")

etiket = soup.find("fiyatspan")

if not etiket:
    print("❌ Fiyat etiketi bulunamadı")
    exit(1)

fiyat_yazi = etiket.text.strip()
print("Ham fiyat:", fiyat_yazi)

fiyat = float(fiyat_yazi.replace(".", "").replace(",", "."))
print("Temiz fiyat:", fiyat)

# ilk çalıştırma
if not os.path.exists(DOSYA):
    with open(DOSYA, "w") as f:
        json.dump({"fiyat": fiyat}, f)
    print("İlk fiyat kaydedildi.")
    exit()

with open(DOSYA, "r") as f:
    onceki = json.load(f)["fiyat"]

durum = "DÜŞMEDİ"
if fiyat < onceki:
    durum = "DÜŞTÜ 🔥"

mesaj = MIMEText(
    f"Ürün fiyat kontrolü\n\n"
    f"Eski: {onceki} ₺\n"
    f"Yeni: {fiyat} ₺\n"
    f"Durum: {durum}\n\n"
    f"{URL}"
)

mesaj["Subject"] = f"Fiyat {durum}"
mesaj["From"] = MAIL
mesaj["To"] = ALICI

s = smtplib.SMTP("smtp.gmail.com", 587)
s.starttls()
s.login(MAIL, SIFRE)
s.send_message(mesaj)
s.quit()

with open(DOSYA, "w") as f:
    json.dump({"fiyat": fiyat}, f)

print("Mail gönderildi ✅")
