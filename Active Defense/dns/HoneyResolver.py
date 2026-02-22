import socket
from dnslib import DNSRecord, QTYPE, RR, A
import logging
import sys
import os

# Menambahkan root project ke sys.path agar bisa import TelegramNotifier & database
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
    format='%(asctime)s - [DNS ALERT] - %(message)s',
    handlers=[
        logging.FileHandler("dns_honeypot.log"),
        logging.StreamHandler()
    ]
)

# Konfigurasi Honeypot
HONEYPOT_IP = "10.0.0.0"
VALID_SUBDOMAINS = {
    "www.example.com.": "192.168.1.10",
    "smtp.example.com.": "192.168.1.11",
}

def dns_resolver(data, client_addr=None):
    request = DNSRecord.parse(data)
    reply = request.reply()
    qname = str(request.q.qname)
    qtype = QTYPE[request.q.qtype]
    client_ip = client_addr[0] if client_addr else "N/A"

    if qname in VALID_SUBDOMAINS:
        ip_addr = VALID_SUBDOMAINS[qname]
        reply.add_answer(RR(qname, QTYPE.A, rdata=A(ip_addr)))
        logging.info(f"Permintaan Valid: {qname} -> {ip_addr}")
    else:
        reply.add_answer(RR(qname, QTYPE.A, rdata=A(HONEYPOT_IP)))
        msg = f"Subdomain tidak dikenal '{qname}' dari IP {client_ip} dialihkan ke {HONEYPOT_IP}"
        logging.warning(f"DETEKSI PENYELIDIKAN: {msg}")
        send_telegram_alert("DNS DECEPTION", msg)
        insert_alert("dns", msg, attacker_ip=client_ip, severity="HIGH")

    return reply.pack()

def start_dns_server(ip="127.0.0.1", port=53):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_socket.bind((ip, port))
        print(f"[*] HoneyResolver berjalan di {ip}:{port}...")
    except PermissionError:
        print("[!] Error: Anda mungkin perlu menjalankan ini sebagai Administrator untuk menggunakan port 53.")
        port = 5353
        udp_socket.bind((ip, port))
        print(f"[*] HoneyResolver (Fallback) berjalan di {ip}:{port}...")

    while True:
        data, addr = udp_socket.recvfrom(1024)
        response = dns_resolver(data, client_addr=addr)
        udp_socket.sendto(response, addr)

if __name__ == "__main__":
    try:
        start_dns_server()
    except KeyboardInterrupt:
        print("\n[*] Menghentikan server...")
