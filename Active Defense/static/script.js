const socket = io();
let currentFilter = 'all';
let hourlyChart = null;
const counts = { dns: 0, cookie: 0, scan: 0, file: 0 };

// ─── SocketIO Events ─────────────────────────────────────────────────────────
socket.on('connect', () => {
    document.getElementById('connection-status').innerHTML = '<span class="status-dot"></span> CONNECTED';
    document.getElementById('connection-status').style.color = '#238636';
    loadStats();
    loadHourlyChart();
});

socket.on('disconnect', () => {
    document.getElementById('connection-status').innerHTML = '<span class="status-dot" style="background:#f85149"></span> DISCONNECTED';
    document.getElementById('connection-status').style.color = '#f85149';
});

socket.on('new_alert', (data) => {
    if (counts.hasOwnProperty(data.type)) {
        counts[data.type]++;
        const el = document.getElementById(`${data.type}-count`);
        if (el) el.innerText = counts[data.type];
        const card = document.getElementById(`${data.type}-card`);
        if (card) {
            card.style.transform = 'scale(1.06)';
            setTimeout(() => card.style.transform = '', 250);
        }
    }
    addFeedItem(data, 'live');
    // Refresh chart & stats secara berkala
    loadStats();
});

socket.on('heartbeat', () => { });

// ─── Feed ─────────────────────────────────────────────────────────────────────
function addFeedItem(data, target = 'live') {
    const feed = document.getElementById('tab-live');
    const item = document.createElement('div');
    item.className = `feed-item ${data.type}`;
    item.dataset.type = data.type;

    const severity = getSeverity(data.type);
    item.innerHTML = `
        <span class="time">${data.timestamp || ''}</span>
        <span class="badge badge-${severity.toLowerCase()}">${severity}</span>
        <span class="type-tag">${data.type.toUpperCase()}</span>
        <span class="msg">${escapeHtml(data.message)}</span>
    `;

    if (currentFilter !== 'all' && data.type !== currentFilter) {
        item.style.display = 'none';
    }

    feed.insertBefore(item, feed.firstChild);
    if (feed.children.length > 100) feed.removeChild(feed.lastChild);
}

function getSeverity(type) {
    const map = { dns: 'HIGH', cookie: 'HIGH', scan: 'CRITICAL', file: 'HIGH' };
    return map[type] || 'MEDIUM';
}

// ─── Filter ───────────────────────────────────────────────────────────────────
function filterFeed(type, btn) {
    currentFilter = type;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('#tab-live .feed-item').forEach(item => {
        item.style.display = (type === 'all' || item.dataset.type === type) ? '' : 'none';
    });
}

// ─── Tabs ─────────────────────────────────────────────────────────────────────
function switchTab(tab, btn) {
    document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-live').style.display = tab === 'live' ? '' : 'none';
    document.getElementById('tab-history').style.display = tab === 'history' ? '' : 'none';
    if (tab === 'history') loadHistory();
}

// ─── History ──────────────────────────────────────────────────────────────────
async function loadHistory() {
    const container = document.getElementById('history-content');
    container.innerHTML = '<p class="loading-text">Memuat...</p>';
    try {
        const res = await fetch('/api/alerts');
        const alerts = await res.json();
        if (alerts.length === 0) {
            container.innerHTML = '<p class="loading-text">Belum ada riwayat alert.</p>';
            return;
        }
        let html = '<table class="history-table"><thead><tr><th>Waktu</th><th>Tipe</th><th>Severity</th><th>IP</th><th>Pesan</th></tr></thead><tbody>';
        alerts.forEach(a => {
            html += `<tr>
                <td>${a.timestamp}</td>
                <td><span class="type-tag ${a.alert_type}">${a.alert_type.toUpperCase()}</span></td>
                <td><span class="badge badge-${a.severity ? a.severity.toLowerCase() : 'medium'}">${a.severity || 'MEDIUM'}</span></td>
                <td>${a.attacker_ip || 'N/A'}</td>
                <td>${escapeHtml(a.message)}</td>
            </tr>`;
        });
        html += '</tbody></table>';
        container.innerHTML = html;
    } catch (e) {
        container.innerHTML = '<p class="loading-text">Gagal memuat riwayat.</p>';
    }
}

// ─── Stats ────────────────────────────────────────────────────────────────────
async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const stats = await res.json();
        Object.entries(stats).forEach(([type, total]) => {
            const el = document.getElementById(`${type}-count`);
            if (el) el.innerText = total;
            if (counts.hasOwnProperty(type)) counts[type] = total;
        });
    } catch (e) { }
}

// ─── Grafik Hourly ────────────────────────────────────────────────────────────
async function loadHourlyChart() {
    try {
        const res = await fetch('/api/hourly');
        const data = await res.json();
        const labels = data.map(d => `${d.hour}:00`);
        const values = data.map(d => d.total);

        const ctx = document.getElementById('hourlyChart').getContext('2d');
        if (hourlyChart) hourlyChart.destroy();
        hourlyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Jumlah Alert',
                    data: values,
                    backgroundColor: 'rgba(88, 166, 255, 0.5)',
                    borderColor: '#58a6ff',
                    borderWidth: 2,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#8b949e' }, grid: { color: '#21262d' } },
                    y: { ticks: { color: '#8b949e' }, grid: { color: '#21262d' }, beginAtZero: true }
                }
            }
        });
    } catch (e) { }
}

// ─── Theme Toggle ─────────────────────────────────────────────────────────────
function toggleTheme() {
    document.body.classList.toggle('light-mode');
    localStorage.setItem('theme', document.body.classList.contains('light-mode') ? 'light' : 'dark');
}

// Terapkan tema tersimpan
if (localStorage.getItem('theme') === 'light') document.body.classList.add('light-mode');

// ─── Utility ──────────────────────────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
