import requests
import time

TOKEN = "7507933195:AAF4MvWv4YCqfJ5Rp-5tB06HzHn7A_k_qvk"

def get_chat_id():
    print("[*] Menunggu pesan masuk di bot Telegram Anda...")
    print("[*] Silakan kirim pesan apa saja (misal: /start) ke bot @JebakanMadu_bot sekarang.")
    
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    
    while True:
        try:
            response = requests.get(url).json()
            if response["result"]:
                # Mengambil chat id dari pesan terakhir
                chat_id = response["result"][-1]["message"]["chat"]["id"]
                user_name = response["result"][-1]["message"]["chat"]["first_name"]
                print(f"\n[+] BERHASIL! Ditemukan Chat ID untuk {user_name}: {chat_id}")
                print("[*] Catat nomor Chat ID di atas untuk dimasukkan ke sistem.")
                break
        except Exception as e:
            print(f"[!] Terjadi kesalahan: {e}")
            break
        
        time.sleep(2)

if __name__ == "__main__":
    get_chat_id()
