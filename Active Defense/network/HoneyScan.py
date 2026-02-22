from scapy.all import sniff, IP, TCP, send
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
    format='%(asctime)s - [SCAN ALERT] - %(message)s',
    handlers=[
        logging.FileHandler("port_scan_alerts.log"),
        logging.StreamHandler()
    ]
)

# Port-port yang akan dijadikan jebakan
DECOY_PORTS = [8080, 8443, 8888, 21, 23]

def handle_syn_packet(packet):
    # Cek apakah paket adalah TCP SYN
    if packet.haslayer(TCP) and packet[TCP].flags == "S":
        target_port = packet[TCP].dport
        
        if target_port in DECOY_PORTS:
            attacker_ip = packet[IP].src  # ambil IP penyerang
            msg = f"Detecting SCAN: {attacker_ip} mencoba mengakses port jebakan {target_port}"
            logging.warning(f"DETEKSI PEMINDAIAN: {msg}")
            send_telegram_alert("PORT SCAN DECEPTION", msg)
            insert_alert("scan", msg, attacker_ip=attacker_ip, severity="CRITICAL")
            
            # MEMALSUKAN RESPON SYN/ACK
            # Ini akan membuat port terlihat "TERBUKA" bagi pemindai
            ip_layer = IP(src=packet[IP].dst, dst=packet[IP].src)
            tcp_layer = TCP(
                sport=packet[TCP].dport,
                dport=packet[TCP].sport,
                flags="SA", # SYN-ACK
                seq=1000,
                ack=packet[TCP].seq + 1
            )
            
            # Kirim paket balasan
            send(ip_layer/tcp_layer, verbose=False)
            logging.info(f"Mengirim SYN/ACK palsu ke {attacker_ip} pada port {target_port}")

def start_honey_scan():
    print(f"[*] HoneyScan aktif. Port jebakan: {DECOY_PORTS}")
    print("[*] Menunggu pemindaian SYN...")
    # Menangkap paket TCP SYN yang ditujukan ke port jebakan
    filter_ports = " or ".join([f"dst port {p}" for p in DECOY_PORTS])
    sniff(filter=f"tcp[tcpflags] & tcp-syn != 0 and ({filter_ports})", prn=handle_syn_packet, store=0)

if __name__ == "__main__":
    try:
        start_honey_scan()
    except PermissionError:
        print("[!] Error: Jalankan sebagai Administrator untuk melakukan raw packet manipulation.")
    except Exception as e:
        print(f"[!] Terjadi kesalahan: {e}")
