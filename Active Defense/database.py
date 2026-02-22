import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "active_defense.db")

def get_connection():
    """Buat koneksi ke database SQLite."""
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inisialisasi tabel database jika belum ada."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type  TEXT NOT NULL,
            message     TEXT NOT NULL,
            attacker_ip TEXT DEFAULT 'N/A',
            severity    TEXT DEFAULT 'MEDIUM',
            timestamp   TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_alert(alert_type, message, attacker_ip="N/A", severity="MEDIUM"):
    """Simpan alert baru ke database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO alerts (alert_type, message, attacker_ip, severity, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (alert_type, message, attacker_ip, severity, ts))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Error saat menyimpan alert: {e}")

def get_alerts(limit=200, alert_type=None):
    """Ambil daftar alert dari database, terbaru duluan."""
    conn = get_connection()
    cursor = conn.cursor()
    if alert_type:
        cursor.execute("SELECT * FROM alerts WHERE alert_type=? ORDER BY id DESC LIMIT ?", (alert_type, limit))
    else:
        cursor.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_stats():
    """Ambil ringkasan statistik alert."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT alert_type, COUNT(*) as total
        FROM alerts
        GROUP BY alert_type
    """)
    stats = {row['alert_type']: row['total'] for row in cursor.fetchall()}
    conn.close()
    return stats

def get_hourly_stats():
    """Ambil jumlah alert per jam dalam 24 jam terakhir."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%H', timestamp) as hour, COUNT(*) as total
        FROM alerts
        WHERE timestamp >= datetime('now', '-24 hours')
        GROUP BY hour
        ORDER BY hour
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def export_csv():
    """Export semua alert ke string CSV."""
    import csv
    import io
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Tipe", "Pesan", "IP Penyerang", "Severity", "Waktu"])
    for row in rows:
        writer.writerow([row["id"], row["alert_type"], row["message"], row["attacker_ip"], row["severity"], row["timestamp"]])
    return output.getvalue()

# Inisialisasi database saat module diimport
init_db()

if __name__ == "__main__":
    print(f"[*] Database diinisialisasi di: {DB_PATH}")
    # Test insert
    insert_alert("TEST", "Ini pesan uji coba dari database.py", "127.0.0.1", "LOW")
    print(f"[*] Alert tersimpan. Stats: {get_stats()}")
