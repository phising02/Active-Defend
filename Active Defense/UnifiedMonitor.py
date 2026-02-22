import time
import os
import threading
from colorama import init, Fore, Style

# Inisialisasi Colorama untuk warna di terminal
init(autoreset=True)

# Daftar file log yang akan dipantau
LOG_FILES = {
    "dns_honeypot.log": Fore.CYAN + "[DNS]",
    "cookie_alerts.log": Fore.YELLOW + "[COOKIE]",
    "port_scan_alerts.log": Fore.MAGENTA + "[SCAN]",
    "file_access_alerts.log": Fore.RED + "[FILE]"
}

def tail_file(filename, prefix):
    # Membaca dari akhir file
    try:
        with open(filename, 'r') as f:
            # Pindah ke akhir file
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    continue
                # Menampilkan baris baru dengan prefix dan warna
                print(f"{prefix} {line.strip()}")
    except FileNotFoundError:
        # Jika file belum ada, tunggu sebentar
        time.sleep(5)
        tail_file(filename, prefix)

def start_unified_monitor():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*70)
    print("       MONITOR TERPADU SISTEM PERTAHANAN AKTIF (REAL-TIME)")
    print("="*70)
    print(f"[*] Menunggu aktivitas dari {len(LOG_FILES)} modul...")
    print("[*] Tekan Ctrl+C untuk kembali ke Menu Utama\n")

    threads = []
    
    # Memastikan file log ada (buat jika belum ada agar tail tidak error)
    for log_file in LOG_FILES:
        if not os.path.exists(log_file):
            with open(log_file, 'a') as f:
                pass

    # Menjalankan tail_file untuk setiap log di thread terpisah
    for log_file, prefix in LOG_FILES.items():
        t = threading.Thread(target=tail_file, args=(log_file, prefix), daemon=True)
        t.start()
        threads.append(t)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Menutup Monitor Terpadu...")

if __name__ == "__main__":
    start_unified_monitor()
