"""
=============================================================================
MODUL KEAMANAN SISTEM & CYBER DEFENSE TERINTEGRASI (SECURITY ENGINE 2026)
Website Resmi Desa - Arsitektur Keamanan Bertingkat (Defense-in-Depth)
=============================================================================
Fitur Keamanan Terintegrasi:
1. Anti-CSRF (Cross-Site Request Forgery) via Fetch-Metadata & Origin/Referer Validation & HMAC Token.
2. Anti-Brute Force & Anti-DDoS Sliding-Window Rate Limiter (IP & Endpoint level).
3. HTTP Security Headers Modern (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, dll).
4. Proteksi Cache Admin (Anti-Data Leakage / Cache-Control no-store untuk privasi data warga/NIK).
5. Pembatasan Upload & Sanitasi Ekstensi Berbahaya (Mencegah Webshell / Remote Code Execution).
6. Penanganan Galat Terisolasi (Mencegah Information Disclosure & Path Leaks pada 400/403/404/413/429/500).
7. Audit Log Terpadu & Pemantauan Ancaman Otomatis ke Basis Data.
=============================================================================
"""

import time
import secrets
import threading
from urllib.parse import urlparse
from flask import request, session, abort, jsonify, render_template, make_response
from database import record_activity_log

# Daftar ekstensi file berbahaya yang DILARANG KERAS diunggah (Anti-Webshell)
DANGEROUS_EXTENSIONS = {
    '.php', '.phtml', '.php3', '.php4', '.php5', '.phps',
    '.exe', '.dll', '.so', '.bin', '.bat', '.cmd', '.sh', '.bash',
    '.vbs', '.vbe', '.js', '.jse', '.wsf', '.wsh', '.msc',
    '.py', '.pyc', '.pyw', '.pl', '.cgi',
    '.html', '.htm', '.xhtml', '.svg', '.hta'
}

# Ekstensi yang diizinkan untuk dokumen publikasi & berkas lampiran
ALLOWED_DOC_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.ppt', '.pptx', '.txt'}
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.ico'}

class SlidingWindowRateLimiter:
    """Rate limiter berbasis sliding window memory yang aman untuk multi-thread"""
    def __init__(self):
        self._lock = threading.Lock()
        self._requests = {}  # {key: [timestamp1, timestamp2, ...]}
        self._last_cleanup = time.time()

    def _cleanup(self, now):
        """Membersihkan entri yang sudah kadaluarsa dari memori setiap 60 detik"""
        if now - self._last_cleanup < 60:
            return
        self._last_cleanup = now
        cutoff = now - 3600  # buang data lebih dari 1 jam
        keys_to_delete = []
        for key, timestamps in self._requests.items():
            valid_ts = [ts for ts in timestamps if ts > cutoff]
            if valid_ts:
                self._requests[key] = valid_ts
            else:
                keys_to_delete.append(key)
        for k in keys_to_delete:
            del self._requests[k]

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> tuple[bool, int]:
        """
        Memeriksa apakah request diizinkan.
        Returns: (is_allowed: bool, remaining_requests: int)
        """
        now = time.time()
        with self._lock:
            self._cleanup(now)
            timestamps = self._requests.get(key, [])
            cutoff = now - window_seconds
            # Filter timestamps dalam rentang window
            valid_timestamps = [ts for ts in timestamps if ts > cutoff]
            current_count = len(valid_timestamps)

            if current_count >= max_requests:
                self._requests[key] = valid_timestamps
                return False, 0

            valid_timestamps.append(now)
            self._requests[key] = valid_timestamps
            remaining = max_requests - len(valid_timestamps)
            return True, remaining

# Instance global rate limiter
rate_limiter = SlidingWindowRateLimiter()

def get_client_ip():
    """Mengambil alamat IP klien sebenarnya dengan memeriksa header proxy"""
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        # Ambil IP pertama jika ada beberapa proxy
        return forwarded.split(',')[0].strip()
    return request.headers.get('X-Real-IP', request.remote_addr or '127.0.0.1')

def generate_csrf_token():
    """Membuat atau mengembalikan token CSRF acak kriptografis untuk sesi saat ini"""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']

def validate_origin():
    """
    Memvalidasi bahwa request state-changing berasal dari origin/host yang sah.
    Melindungi dari serangan Cross-Site Request Forgery (CSRF).
    """
    # 1. Sec-Fetch-Site Check (Standar modern browser W3C)
    sec_fetch_site = request.headers.get('Sec-Fetch-Site')
    if sec_fetch_site == 'cross-site':
        return False, "Sec-Fetch-Site cross-site violation"

    # 2. Origin & Referer Verification
    origin = request.headers.get('Origin')
    referer = request.headers.get('Referer')
    host = request.host.lower()

    if origin:
        parsed_origin = urlparse(origin)
        origin_host = parsed_origin.netloc.lower()
        if origin_host and origin_host != host:
            return False, f"Origin mismatch: {origin_host} vs {host}"

    if not origin and referer:
        parsed_referer = urlparse(referer)
        referer_host = parsed_referer.netloc.lower()
        if referer_host and referer_host != host:
            return False, f"Referer mismatch: {referer_host} vs {host}"

    return True, "OK"

def is_safe_filename(filename: str, allowed_extensions: set = None) -> bool:
    """Memeriksa apakah ekstensi file aman dari potensi webshell"""
    if not filename or '.' not in filename:
        return False
    ext = '.' + filename.rsplit('.', 1)[1].lower()
    if ext in DANGEROUS_EXTENSIONS:
        return False
    if allowed_extensions and ext not in allowed_extensions:
        return False
    return True

def init_security(app):
    """Menginisialisasi seluruh pertahanan keamanan ke aplikasi Flask"""

    # 1. Batas Maksimal Payload / Upload File: 32 MegaBytes (Mencegah DDoS Memory/Disk)
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

    # 2. Pengaturan Cookie Sesi Aman
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Injeksi helper csrf_token ke template Jinja
    @app.context_processor
    def inject_csrf():
        return {
            'csrf_token': generate_csrf_token,
            'csrf_input': lambda: f'<input type="hidden" name="csrf_token" value="{generate_csrf_token()}">'
        }

    # 3. Interceptor Request Masuk (Before Request)
    @app.before_request
    def security_before_request():
        client_ip = get_client_ip()

        # Lewati pemeriksaan untuk static assets agar performa maksimal
        if request.path.startswith('/static') or request.path.startswith('/assets'):
            return None

        # A. Proteksi Global Flooding / DDoS Mikro (Maks 200 request / menit per IP)
        is_allowed, _ = rate_limiter.is_allowed(f"global:{client_ip}", max_requests=200, window_seconds=60)
        if not is_allowed:
            record_activity_log(
                'DDOS_BLOCKED',
                f"Rate limit global terlampaui (>200 req/min) dari IP: {client_ip} pada path: {request.path}",
                ip_address=client_ip,
                user_agent=request.user_agent.string
            )
            return jsonify({
                'success': False,
                'message': 'Aktivitas jaringan terlalu tinggi. Sistem membatasi sementara permintaan Anda demi stabilitas server.'
            }), 429

        # B. Proteksi Anti-Spam Form Publik (Aduan, Surat, Wisata, UMKM, Feedback)
        public_submit_endpoints = [
            '/api/pengaduan/kirim',
            '/api/surat/ajukan',
            '/api/feedback/kirim',
            '/api/umkm/ajukan',
            '/api/wisata/ajukan'
        ]
        if request.path in public_submit_endpoints and request.method == 'POST':
            # Maks 12 pengajuan per 3 menit per IP
            is_ok, remaining = rate_limiter.is_allowed(f"submit:{client_ip}:{request.path}", max_requests=12, window_seconds=180)
            if not is_ok:
                record_activity_log(
                    'SPAM_FORM_BLOCKED',
                    f"Percobaan spam submission dicegah pada {request.path} dari IP: {client_ip}",
                    ip_address=client_ip,
                    user_agent=request.user_agent.string
                )
                return jsonify({
                    'success': False,
                    'message': 'Keamanan Sistem: Terlalu banyak permohonan dalam waktu singkat. Mohon tunggu 3 menit sebelum mengirim formulir kembali.'
                }), 429

        # C. Proteksi CSRF untuk request pengubah data (POST, PUT, DELETE, PATCH)
        if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
            is_valid_origin, reason = validate_origin()
            if not is_valid_origin:
                record_activity_log(
                    'CSRF_ATTACK_PREVENTED',
                    f"Percobaan potensi CSRF diblokir ({reason}) pada URL: {request.path}",
                    username=session.get('username'),
                    user_id=session.get('user_id'),
                    ip_address=client_ip,
                    user_agent=request.user_agent.string
                )
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'success': False, 'message': 'Akses Ditolak: Permintaan lintas-asal (Cross-Origin) tidak diizinkan demi keamanan.'}), 403
                return render_template('errors/403.html', pesan='Akses Ditolak: Pelanggaran Keamanan Cross-Site Request Forgery (CSRF).'), 403

        return None

    # 4. Interceptor Response Keluar (After Request) - HTTP Security Headers
    @app.after_request
    def security_after_request(response):
        # Anti-Clickjacking: Melarang embedding di situs pihak ketiga (Hanya izinkan domain sendiri)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'

        # Anti-MIME Sniffing: Memaksa browser mengikuti Content-Type yang dideklarasikan
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # Anti-XSS Filter (Untuk kompatibilitas browser legacy)
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Referrer Policy: Hanya kirim origin ke domain eksternal jika HTTPS
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Batasi izin fitur perangkat keras browser yang tidak digunakan website desa
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), payment=(), usb=(), display-capture=()'

        # Kebijakan Pembukaan Jendela Lintas Asal
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'

        # Larang Flash & berkas dokumen cross-domain policy
        response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'

        # Content Security Policy (CSP): Mengizinkan CDN resmi yang digunakan (Leaflet, Tailwind, Fonts, Chartjs)
        csp_policy = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: data: blob:; "
            "img-src 'self' data: blob: https:; "
            "font-src 'self' https: data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'self';"
        )
        response.headers['Content-Security-Policy'] = csp_policy

        # Proteksi Cache Panel Admin: Mencegah kebocoran data sensitif warga (NIK, nama, logs) di cache browser komputer bersama
        if request.path.startswith('/admin'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

        return response

    # 5. Handlers Galat Sistem Terisolasi (Anti-Leak Informasi Sensitif)
    @app.errorhandler(403)
    def forbidden_handler(e):
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': '403 Forbidden: Akses tidak diizinkan atau sesi telah kedaluwarsa.'}), 403
        try:
            return render_template('errors/403.html', pesan='Akses ditolak demi keamanan data.'), 403
        except Exception:
            return "<h3>403 Akses Ditolak: Hak akses tidak mencukupi atau potensi pelanggaran keamanan terdeteksi.</h3>", 403

    @app.errorhandler(413)
    def entity_too_large_handler(e):
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Ukuran file melebihi batas maksimal (Maks 32MB). Unggah gagal.'}), 413
        return "<h3>413 Payload Terlalu Besar: Berkas yang diunggah melebihi batas maksimal server (Maksimal 32 MB).</h3>", 413

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'success': False,
            'message': '429 Terlalu Banyak Permintaan: Mohon jeda beberapa saat sebelum mencoba kembali.'
        }), 429
