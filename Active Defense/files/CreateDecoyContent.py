from pathlib import Path
import json
import time
import os

# Daftar file umpan yang akan dibuat
DECOY_FILES = {
    "daftar_gaji_2025.xlsx": "Data gaji rahasia karyawan.",
    "kredensial_database.txt": "DB_HOST=192.168.1.50\nDB_USER=root\nDB_PASS=SangatRahasia123!",
    "rencana_akuisisi.docx": "Dokumen strategi akuisisi perusahaan kompetitor.",
    "vpn_config.ovpn": "client\ndev tun\nremote 202.10.20.30 1194\nnobind\n<ca>\nFake Certificate Data\n</ca>"
}

METADATA_FILE = "decoy_metadata.json"

def create_decoys():
    metadata = {}
    
    # Membuat direktori jika belum ada
    folder_umpan = Path("files/honeypots")
    folder_umpan.mkdir(exist_ok=True, parents=True)
    
    print("[*] Membuat file umpan...")
    
    for filename, content in DECOY_FILES.items():
        file_path = folder_umpan / filename
        
        # Tulis konten ke file
        file_path.write_text(content)
        
        # Ambil metadata awal
        stats = file_path.stat()
        metadata[str(file_path)] = {
            "last_atime": stats.st_atime, # Access time
            "last_mtime": stats.st_mtime  # Modify time
        }
        print(f"   [+] Dibuat: {file_path}")

    # Simpan metadata ke JSON
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=4)
    
    print(f"[*] Metadata disimpan ke {METADATA_FILE}")

if __name__ == "__main__":
    create_decoys()
