from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import os, json, smtplib, re
from email.mime.text import MIMEText

URL = "https://www.itopya.com/the-vok-v7-amd-ryzen-5-7600-gigabyte-geforce-rtx-5070-12gb-16gb-ddr5-1tb-m2-ssd-oem-paket_h31967"
DOSYA = "son_fiyat.json"

MAIL = os.environ["MAIL_GONDEREN"]
SIFRE = os.environ["MAIL_SIFRE"]
ALICI = os.environ["MAIL_ALICI"]

def mail_gonder(konu, icerik):
    msg = MIMEText(icerik)
    msg["Subject"] = konu
    msg["From"] = MAIL
    msg["To"] = ALICI

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(MAIL, SIFRE)
    s.send_message(msg)
    s.quit()

def fiyat_yazisini_temizle(txt: str):
    # 59.661,92 ₺ gibi yazıları temizler
    txt = txt.strip()
    sadece = re.sub(r"[^\d,\.]", "", txt)
    if not sadece:
        return None
    # TR format: 59.661,92 -> 59661.92
    val = float(sadece.replace(".", "").replace(",", "."))
    return val

def eski_fiyat_oku():
    if not os.path.exists(DOSYA):
        return None
    try:
        with open(DOSYA, "r", encoding="utf-8") as f:
            return json.load(f).get("fiyat")
    except Exception:
        return None

def yeni_fiyat_yaz(fiyat):
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump({"fiyat": fiyat}, f)

def fiyat_bul(page):
    # Birkaç olası selector deniyoruz (site değişirse de şans)
    adaylar = [
        "span.price",
        "fiyatspan",
        "[data-testid='price']",
        ".product-price span",
        ".price",
    ]

    for sel in adaylar:
        try:
            page.wait_for_selector(sel, timeout=15000)
            txt = page.locator(sel).first.inner_text().strip()
            f = fiyat_yazisini_temizle(txt)
            if f is not None:
                return f, txt, sel
        except PWTimeout:
            continue
        except Exception:
            continue
    return None, None, None

def main():
    fiyat = None
    ham = None
    sel = None
    hata = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="tr-TR",
        )
        page = context.new_page()

        try:
            page.goto(URL, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)

            # Eğer site bot sayfası / captcha gösterirse anlamak için:
            page.screenshot(path="ekran.png", full_page=True)
            html = page.content()
            with open("sayfa.html", "w", encoding="utf-8") as f:
                f.write(html)

            fiyat, ham, sel = fiyat_bul(page)

        except Exception as e:
            hata = str(e)

        finally:
            browser.close()

    onceki = eski_fiyat_oku()

    if fiyat is None:
        konu = "⚠️ Fiyat okunamadı (Actions)"
        icerik = (
            "GitHub Actions ortamında fiyat etiketi bulunamadı.\n"
            "Muhtemel sebep: bot koruması / JS / selector değişimi.\n\n"
            f"URL: {URL}\n"
            f"Hata: {hata or 'yok'}\n\n"
            "Repo > Actions run > Artifacts kısmından ekran.png ve sayfa.html indirip bakabilirsin.\n"
        )
        mail_gonder(konu, icerik)
        print("Fiyat okunamadı, mail atıldı.")
        return

    # fiyat bulundu
    durum = "DÜŞMEDİ ❌"
    if onceki is None:
        durum = "İLK KAYIT ✅"
    elif fiyat < onceki:
        durum = "DÜŞTÜ 🔥"

    konu = f"📦 Fiyat Durumu: {durum}"
    icerik = (
        f"Selector: {sel}\n"
        f"Ham: {ham}\n\n"
        f"Önceki: {onceki if onceki is not None else 'yok'} ₺\n"
        f"Yeni: {fiyat} ₺\n"
        f"Durum: {durum}\n\n"
        f"{URL}\n"
    )

    mail_gonder(konu, icerik)
    yeni_fiyat_yaz(fiyat)
    print("Fiyat bulundu, mail gönderildi, json güncellendi.")

if __name__ == "__main__":
    main()
