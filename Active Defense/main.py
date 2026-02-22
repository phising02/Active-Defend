import subprocess
import sys
import os

def print_banner():
    print("="*60)
    print("      EKOSISTEM PERTAHANAN AKTIF (ACTIVE DEFENSE) v1.0")
    print("="*60)
    print("PEMANTAUAN:")
    print("M. Buka MONITOR TERPADU (Satu Pintu - Terminal)")
    print("W. Buka WEB DASHBOARD (Premium GUI - Browser)")
    print("-" * 60)
    print("LAYANAN DECOY (Jalankan satu per satu):")
    print("1. DNS Honeypot (HoneyResolver)")
    print("2. Cookie Decoy Sniffer (DetectDecoyCookies)")
    print("3. Port Scan Deception (HoneyScan)")
    print("4. Network Credentials Umpan (DecoyCredentials)")
    print("5. File Access Monitor (MonitorDecoyContent)")
    print("-" * 60)
    print("PERSIAPAN (Jalankan sekali):")
    print("6. Injeksi Cookie ke Firefox")
    print("7. Inisialisasi File Umpan")
    print("0. Keluar")
    print("-" * 60)

def run_module(script_path):
    print(f"[*] Menjalankan {script_path}...")
    try:
        # Penanganan khusus Windows 'start' command untuk path yang mengandung spasi
        # Judul jendela harus diapit kutipan, dan perintah eksekusi juga diapit kutipan dengan benar
        # Cara paling stabil di Windows: start "Judul" "PathPython" "PathScript"
        title = os.path.basename(script_path)
        # Kami menggunakan format ini untuk memastikan CMD tidak bingung dengan spasi di tengah path
        command = f'start "{title}" "{sys.executable}" "{script_path}"'
        subprocess.Popen(command, shell=True)
    except Exception as e:
        print(f"[!] Gagal menjalankan modul: {e}")

if __name__ == "__main__":
    try:
        while True:
            print_banner()
            choice = input("Pilih modul yang ingin dijalankan (0-7 / M / W): ").lower()
            
            if choice == 'm':
                run_module("UnifiedMonitor.py")
            elif choice == 'w':
                run_module("DashboardServer.py")
                # Mencoba membuka browser otomatis
                import webbrowser
                import threading
                # Beri waktu 3 detik agar server Flask siap sebelum browser terbuka
                threading.Timer(3, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
            elif choice == '1':
                run_module("dns/HoneyResolver.py")
            elif choice == '2':
                run_module("cookies/DetectDecoyCookies.py")
            elif choice == '3':
                run_module("network/HoneyScan.py")
            elif choice == '4':
                run_module("network/DecoyCredentials.py")
            elif choice == '5':
                run_module("files/MonitorDecoyContent.py")
            elif choice == '6':
                subprocess.run([sys.executable, "cookies/CreateFakeCookie.py"])
            elif choice == '7':
                subprocess.run([sys.executable, "files/CreateDecoyContent.py"])
            elif choice == '0':
                print("[*] Keluar...")
                break
            else:
                print("[!] Pilihan tidak valid.")
            
            print("\n" + "-"*60)
            input("Tekan Enter untuk kembali ke menu...")
            os.system('cls' if os.name == 'nt' else 'clear')
    except KeyboardInterrupt:
        print("\n\n[*] Program dihentikan oleh pengguna. Keluar...")
        sys.exit(0)
