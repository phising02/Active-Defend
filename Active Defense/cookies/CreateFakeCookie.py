import sqlite3
import os
import glob
from pathlib import Path

def find_firefox_cookies():
    # Menentukan path profile Firefox di Windows
    appdata = os.environ.get('APPDATA')
    if not appdata:
        print("[!] Environment variable APPDATA tidak ditemukan.")
        return None
    
    profiles_path = Path(appdata) / "Mozilla" / "Firefox" / "Profiles"
    if not profiles_path.exists():
        print(f"[!] Path profiles tidak ditemukan: {profiles_path}")
        return None

    # Mencari file cookies.sqlite di semua folder profil
    cookies_files = list(profiles_path.glob("*/cookies.sqlite"))
    return cookies_files

def inject_decoy_cookie(db_path):
    print(f"[*] Mencoba menyuntikkan ke: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Data cookie decoy
        # Domain: .fake.com
        # Name: session_id
        # Value: decoy_secret_777
        decoy_data = (
            '.fake.com',        # host
            'session_id',        # name
            'decoy_secret_777',  # value
            '/',                # path
            1999999999,          # expiry (jauh di masa depan)
            0,                   # isSecure
            1                    # isHttpOnly
        )

        query = """
        INSERT OR REPLACE INTO moz_cookies 
        (host, name, value, path, expiry, isSecure, isHttpOnly) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(query, decoy_data)
        conn.commit()
        conn.close()
        print(f"[+] Berhasil menyuntikkan cookie decoy ke {os.path.basename(db_path)}")
        
    except sqlite3.OperationalError as e:
        if "locked" in str(e):
            print(f"[!] Error: Database terkunci. Pastikan Firefox sudah ditutup.")
        else:
            print(f"[!] Error SQLite: {e}")
    except Exception as e:
        print(f"[!] Terjadi kesalahan: {e}")

if __name__ == "__main__":
    cookies_paths = find_firefox_cookies()
    if cookies_paths:
        for path in cookies_paths:
            inject_decoy_cookie(path)
    else:
        print("[!] Tidak ada profil Firefox yang ditemukan.")
