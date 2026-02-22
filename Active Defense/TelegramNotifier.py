import requests
import logging
import time
import os
from pathlib import Path

# Coba baca dari file .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # python-dotenv belum diinstal, gunakan nilai hardcode sebagai fallback

# Konfigurasi Telegram — dibaca dari .env atau fallback ke hardcode
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7507933195:AAF4MvWv4YCqfJ5Rp-5tB06HzHn7A_k_qvk")
CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "7356160018")

def send_telegram_alert(alert_type, message):
    if not CHAT_ID:
        logging.info("Telegram Chat ID belum dikonfigurasi. Lewati pengiriman pesan.")
        return

    # Menggunakan HTML agar lebih aman dari karakter khusus dibanding Markdown
    text = f"🚨 <b>NOTIFIKASI PERTAHANAN AKTIF</b> 🚨\n\n" \
           f"📌 <b>Tipe:</b> {alert_type}\n" \
           f"⚠️ <b>Pesan:</b> {message}\n" \
           f"⏰ <b>Waktu:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logging.error(f"Gagal mengirim Telegram: {response.text}")
    except Exception as e:
        logging.error(f"Error saat mengirim notifikasi Telegram: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if CHAT_ID:
        send_telegram_alert("TEST", "Pesan uji coba dari Sistem Active Defense v2.0.")
        print("[*] Pesan uji coba terkirim!")
    else:
        print("[!] Chat ID belum diisi. Silakan cek file .env")
