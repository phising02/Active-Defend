from scapy.all import sniff, IP, TCP, Raw
import logging
import sys
import os

# Menambahkan root project ke sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from TelegramNotifier import send_telegram_alert
except ImportError:
    def send_telegram_alert(a, b): pass
try:
    from database import insert_alert
except ImportError:
    def insert_alert(a, b, c="N/A", d="MEDIUM"): pass

# Konfigurasi Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [COOKIE ALERT] - %(message)s',
    handlers=[
        logging.FileHandler("cookie_alerts.log"),
        logging.StreamHandler()
    ]
)

DECOY_COOKIE_VALUE = "decoy_secret_777"

def process_packet(packet):
    if packet.haslayer(TCP) and packet.haslayer(Raw):
        payload = packet[Raw].load.decode(errors='ignore')
        
        # Mengecek apakah ada cookie decoy di dalam payload HTTP
        if f"session_id={DECOY_COOKIE_VALUE}" in payload:
            attacker_ip = packet[IP].src
            target_host = "Unknown"
            
            # Mencoba mengekstrak Host dari header HTTP
            for line in payload.split("\r\n"):
                if line.startswith("Host:"):
                    target_host = line.split(":", 1)[1].strip()
                    break
            
            msg = f"Penyusup {attacker_ip} menggunakan cookie decoy di {target_host}"
            logging.warning(
                f"PENGGUNAAN COOKIE DECOY TERDETEKSI!\n"
                f"   [!] Penyerang IP : {attacker_ip}\n"
                f"   [!] Target Host : {target_host}\n"
                f"   [!] Cookie      : session_id={DECOY_COOKIE_VALUE}\n"
                f"----------------------------------------------------"
            )
            send_telegram_alert("WEB SESSION DECOY", msg)
            insert_alert("cookie", msg, attacker_ip=attacker_ip, severity="HIGH")

def start_sniffer():
    print(f"[*] Menunggu penggunaan cookie decoy '{DECOY_COOKIE_VALUE}' di jaringan...")
    print("[*] Pastikan Anda menjalankan ini sebagai Administrator.")
    # Sniffing pada port 80 (HTTP) untuk mendeteksi cookie dalam teks biasa
    sniff(filter="tcp port 80", prn=process_packet, store=0)

if __name__ == "__main__":
    try:
        start_sniffer()
    except PermissionError:
        print("[!] Error: Izin ditolak. Jalankan terminal sebagai Administrator.")
    except Exception as e:
        print(f"[!] Terjadi kesalahan: {e}")
