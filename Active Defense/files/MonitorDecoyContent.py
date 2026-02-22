import time
import os
import json
import sys
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

# Setup Path for TelegramNotifier & database
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
    format='%(asctime)s - [FILE ALERT] - %(message)s',
    handlers=[
        logging.FileHandler("file_access_alerts.log"),
        logging.StreamHandler()
    ]
)

# Nama file dan direktori - menggunakan path absolut agar lebih aman
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_FILE = os.path.join(BASE_DIR, "decoy_metadata.json")
MONITOR_DIR = os.path.join(BASE_DIR, "files", "honeypots")

class DecoyHandler(FileSystemEventHandler):
    def __init__(self, metadata):
        self.metadata = metadata
        self.last_alert_time = {}

    def on_modified(self, event):
        if event.is_directory: return
        self.process_event(event, "MODIFIKASI")

    def on_created(self, event):
        if event.is_directory: return
        self.process_event(event, "FILE BARU/AKSES")

    def on_moved(self, event):
        if event.is_directory: return
        self.process_event(event, "DIPINDAHKAN", is_move=True)

    def on_deleted(self, event):
        if event.is_directory: return
        self.process_event(event, "DIHAPUS")

    def process_event(self, event, action, is_move=False):
        path_to_check = event.dest_path if is_move else event.src_path
        file_abspath = os.path.abspath(path_to_check)
        
        # LOG DIAGNOSTIK: Muncul di jendela CMD Monitor
        print(f"[*] Event sistem terdeteksi: {action} pada {os.path.basename(file_abspath)}")
        
        found_in_metadata = False
        for meta_path in self.metadata.keys():
            full_meta_path = os.path.abspath(os.path.join(BASE_DIR, meta_path))
            if file_abspath == full_meta_path:
                found_in_metadata = True
                break
        
        if found_in_metadata:
            current_time = time.time()
            if file_abspath in self.last_alert_time and (current_time - self.last_alert_time[file_abspath] < 3):
                return
            
            self.last_alert_time[file_abspath] = current_time
            file_name = os.path.basename(file_abspath)
            msg = f"AKTIVITAS TERDETEKSI: File '{file_name}' telah diinteraksi ({action})!"
            
            logging.warning(msg)
            print(f"[!] POSITIF HONEYPOT: Mengirim alert untuk {file_name}")
            send_telegram_alert("DECOY CONTENT", msg)
            insert_alert("file", msg, severity="HIGH")
        else:
            print(f"[-] Bukan file honeypot, abaikan.")

def start_monitor():
    if not os.path.exists(METADATA_FILE):
        print(f"[!] Metadata {METADATA_FILE} tidak ditemukan.")
        return

    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)

    if not os.path.exists(MONITOR_DIR):
        os.makedirs(MONITOR_DIR)

    event_handler = DecoyHandler(metadata)
    observer = Observer()
    observer.schedule(event_handler, MONITOR_DIR, recursive=False)
    
    print(f"[*] Honeypot File Monitor AKTIF (Watchdog) pada: {MONITOR_DIR}")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_monitor()
