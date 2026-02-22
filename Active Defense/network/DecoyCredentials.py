import socket
import time
import random

# Konfigurasi Umpan
TARGET_IP = "10.0.0.99" # IP yang tidak ada di jaringan
DECOY_USER = "admin_super"
DECOY_PASS_LIST = ["P@ssword123", "SuperSecure321", "LoginAdmin#1"]

def send_decoy_ftp():
    password = random.choice(DECOY_PASS_LIST)
    print(f"[*] Menyebarkan umpan kredensial FTP: {DECOY_USER}:{password}")
    
    try:
        # Mencoba koneksi FTP (ini akan gagal, tapi paket akan terlihat oleh sniffer penyerang)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((TARGET_IP, 21))
        
        # Simulasi Protokol FTP Sederhana
        s.recv(1024)
        s.send(f"USER {DECOY_USER}\r\n".encode())
        s.recv(1024)
        s.send(f"PASS {password}\r\n".encode())
        s.close()
    except:
        # Kita mengharapkan kegagalan koneksi karena target IP tidak ada.
        # Yang penting adalah paket "USER" dan "PASS" terdeteksi di jaringan.
        pass

def send_decoy_telnet():
    password = random.choice(DECOY_PASS_LIST)
    print(f"[*] Menyebarkan umpan kredensial Telnet: {DECOY_USER}:{password}")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((TARGET_IP, 23))
        
        # Simulasi pengiriman kredensial Telnet dalam teks biasa
        s.send(f"login: {DECOY_USER}\n".encode())
        s.send(f"password: {password}\n".encode())
        s.close()
    except:
        pass

if __name__ == "__main__":
    print("[*] DecoyCredentials aktif. Menyebarkan 'noise' kredensial di jaringan...")
    while True:
        # Mengirim umpan setiap 30-60 detik secara acak
        send_decoy_ftp()
        send_decoy_telnet()
        delay = random.randint(30, 60)
        print(f"[*] Menunggu {delay} detik sebelum pengiriman berikutnya...")
        time.sleep(delay)
