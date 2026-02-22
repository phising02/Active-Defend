from flask import Flask, render_template, jsonify, Response, request, redirect, url_for, session
from flask_socketio import SocketIO
from functools import wraps
import time
import os
import sys
import requests as req

# Setup path agar bisa import database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from database import init_db, get_alerts, get_stats, get_hourly_stats, export_csv

app = Flask(__name__)
app.secret_key = "aktif-defense-secret-key-v2-2026"
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Build version untuk cache-busting — berubah tiap restart server
BUILD_VER = str(int(time.time()))

# Password dashboard
DASHBOARD_PASSWORD = "admin123"

LOG_FILES = {
    "dns_honeypot.log": "dns",
    "cookie_alerts.log": "cookie",
    "port_scan_alerts.log": "scan",
    "file_access_alerts.log": "file"
}

# ─── Cache & Context ──────────────────────────────────────────────────────────
@app.after_request
def add_no_cache(response):
    """Paksa browser selalu ambil file terbaru."""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.context_processor
def inject_globals():
    return {'v': BUILD_VER}

# ─── GeoIP Lookup ─────────────────────────────────────────────────────────────
_geoip_cache = {}
def get_geoip(ip):
    if ip in _geoip_cache or ip in ("N/A", "127.0.0.1", "localhost"):
        return _geoip_cache.get(ip, {})
    try:
        r = req.get(f"http://ip-api.com/json/{ip}?fields=country,city,countryCode", timeout=3)
        if r.status_code == 200:
            data = r.json()
            _geoip_cache[ip] = data
            return data
    except Exception:
        pass
    return {}

# ─── Log Watcher ──────────────────────────────────────────────────────────────
def watch_log(filename, log_type):
    print(f"[*] Monitor [{log_type.upper()}] -> {filename}")
    full_path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(full_path):
        open(full_path, 'a').close()
    last_size = os.path.getsize(full_path)
    while True:
        try:
            current_size = os.path.getsize(full_path)
            if current_size > last_size:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_size)
                    new_content = f.read()
                    last_size = current_size
                    for line in new_content.splitlines():
                        if line.strip() and "---" not in line:
                            socketio.emit('new_alert', {
                                'type': log_type,
                                'message': line.strip(),
                                'timestamp': time.strftime('%H:%M:%S')
                            })
            elif current_size < last_size:
                last_size = current_size
            socketio.sleep(1)
        except Exception:
            socketio.sleep(1)

def heartbeat():
    while True:
        socketio.emit('heartbeat', {'time': time.strftime('%H:%M:%S')})
        socketio.sleep(10)

# ─── Auth Decorator ───────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ─── Auth Routes ──────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Jika sudah login, langsung ke dashboard
    if session.get('logged_in'):
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        if request.form.get('password') == DASHBOARD_PASSWORD:
            session['logged_in'] = True
            session.permanent = True
            print("[*] Login berhasil!")
            return redirect(url_for('index'))
        error = "Password salah!"
        print("[!] Login gagal — password salah")
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── Main Routes ──────────────────────────────────────────────────────────────
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# ─── API Endpoints ────────────────────────────────────────────────────────────
@app.route('/api/alerts')
@login_required
def api_alerts():
    alert_type = request.args.get('type')
    alerts = get_alerts(limit=200, alert_type=alert_type)
    return jsonify(alerts)

@app.route('/api/stats')
@login_required
def api_stats():
    return jsonify(get_stats())

@app.route('/api/hourly')
@login_required
def api_hourly():
    return jsonify(get_hourly_stats())

@app.route('/api/export/csv')
@login_required
def api_export_csv():
    csv_data = export_csv()
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=active_defense_alerts.csv'}
    )

# ─── Runner ───────────────────────────────────────────────────────────────────
def run_watchers():
    print("[*] Memulai semua watcher log...")
    for filename, log_type in LOG_FILES.items():
        socketio.start_background_task(watch_log, filename, log_type)
    socketio.start_background_task(heartbeat)

if __name__ == '__main__':
    init_db()
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    run_watchers()
    print(f"[*] Dashboard v2.0 berjalan di http://127.0.0.1:5000  [build={BUILD_VER}]")
    socketio.run(app, host='127.0.0.1', port=5000, debug=False, allow_unsafe_werkzeug=True)
