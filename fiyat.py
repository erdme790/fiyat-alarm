from playwright.sync_api import sync_playwright
import json, os, smtplib
from email.mime.text import MIMEText

URL = "https://www.itopya.com/the-vok-v7-amd-ryzen-5-7600-gigabyte-geforce-rtx-5070-12gb-16gb-ddr5-1tb-m2-ssd-oem-paket_h31967"
DOSYA = "son_fiyat.json"

MAIL = os.environ["MAIL_GONDEREN"]
SIFRE = os.environ["MAIL_SIFRE"]
ALICI = os.environ["MAIL_ALICI"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=60000)
    page.wait_for_timeout(5000)

    fiyat_text = page.locator("fiyatspan").inner_text()
    browser.close()

print("Ham fiyat:", fiyat_text)

fiyat = float(fiyat_text.replace(".", "").replace(",", "."))
print("Temiz fiyat:", fiyat)

if not os.path.exists(DOSYA):
    with open(DOSYA, "w") as f:
        json.dump({"fiyat": fiyat}, f)
    print("İlk fiyat kaydedildi")
    exit()

onceki = json.load(open(DOSYA))["fiyat"]
durum = "DÜŞMEDİ"

if fiyat < onceki:
    durum = "DÜŞTÜ 🔥"

msg = MIMEText(
    f"Eski: {onceki} ₺\nYeni: {fiyat} ₺\nDurum: {durum}\n\n{URL}"
)

msg["Subject"] = f"Fiyat {durum}"
msg["From"] = MAIL
msg["To"] = ALICI

s = smtplib.SMTP("smtp.gmail.com", 587)
s.starttls()
s.login(MAIL, SIFRE)
s.send_message(msg)
s.quit()

json.dump({"fiyat": fiyat}, open(DOSYA, "w"))
print("Mail gönderildi ✅")
