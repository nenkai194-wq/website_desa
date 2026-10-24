from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import json
import random
import os
import time
import io
import csv
import sqlite3
from database import get_db, init_db, record_activity_log, record_visitor_hit, get_visitor_stats
from datetime import datetime, timedelta
import zipfile
import shutil
from statistik_helper import (
    generate_template_excel,
    generate_template_csv,
    export_sls_excel,
    parse_uploaded_sls_file,
    sync_aggregate_statistics,
    generate_template_umur_excel,
    generate_template_umur_csv,
    export_umur_excel,
    parse_uploaded_umur_file,
    sync_aggregate_umur,
    PENDIDIKAN_COLUMNS,
    generate_template_pendidikan_excel,
    generate_template_pendidikan_csv,
    export_pendidikan_excel,
    parse_uploaded_pendidikan_file,
    generate_template_perkawinan_excel,
    generate_template_perkawinan_csv,
    export_perkawinan_excel,
    export_perkawinan_csv,
    parse_uploaded_perkawinan_file,
    generate_template_pencatatan_nikah_excel,
    generate_template_pencatatan_nikah_csv,
    export_pencatatan_nikah_excel,
    export_pencatatan_nikah_csv,
    parse_uploaded_pencatatan_nikah_file,
    AGAMA_COLUMNS,
    generate_template_agama_excel,
    generate_template_agama_csv,
    export_agama_excel,
    export_agama_csv,
    parse_uploaded_agama_file,
    BANSOS_COLUMNS,
    generate_template_bansos_excel,
    generate_template_bansos_csv,
    export_bansos_excel,
    export_bansos_csv,
    parse_uploaded_bansos_file,
    ANAK_COLUMNS,
    generate_template_anak_excel,
    generate_template_anak_csv,
    export_anak_excel,
    export_anak_csv,
    parse_uploaded_anak_file,
    GIZI_BURUK_COLUMNS,
    generate_template_gizi_buruk_excel,
    generate_template_gizi_buruk_csv,
    export_gizi_buruk_excel,
    export_gizi_buruk_csv,
    parse_uploaded_gizi_buruk_file,
    STUNTING_COLUMNS,
    generate_template_stunting_excel,
    generate_template_stunting_csv,
    export_stunting_excel,
    export_stunting_csv,
    parse_uploaded_stunting_file
)
from peta_helper import buat_geojson_sls_dengan_penduduk, unduh_kml_dari_url, DEFAULT_KML_URL
from security_engine import init_security

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'desa_kersik_secure_entropy_key_2026_tasikmalaya_papayan')

# Inisialisasi Arsitektur Keamanan Modern 2026 (Anti-CSRF, Rate Limiting, Security Headers, Audit Monitoring)
init_security(app)
init_db()
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=3)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'uploads')
DOCS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'docs', 'publikasi')
BACKUP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOCS_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOCS_FOLDER'] = DOCS_FOLDER
app.config['BACKUP_FOLDER'] = BACKUP_FOLDER

@app.route('/assets/<path:filename>')
def assets_fallback(filename):
    return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'), filename)

def hitung_status_waktu_popup(popup_dict):
    """
    Menentukan status tayang dinamis pop-up berdasarkan status manual dan rentang waktu.
    Mengembalikan dict:
      'status_waktu': 'Tayang' | 'Terjadwal' | 'Kedaluwarsa' | 'Draf'
      'label': teks label tampilan
      'badge_class': kelas warna CSS
      'is_aktif': boolean (apakah berhak tampil di frontend saat ini)
      'keterangan_waktu': uraian info waktu
    """
    if not popup_dict:
        return {'status_waktu': 'Draf', 'label': 'Tidak Tayang (Draf)', 'badge_class': 'bg-slate-100 text-slate-600 border-slate-300', 'is_aktif': False, 'keterangan_waktu': 'Nonaktif'}
    
    status_manual = popup_dict.get('status', 'Tayang')
    if status_manual != 'Tayang':
        return {
            'status_waktu': 'Draf',
            'label': 'Tidak Tayang (Draf)',
            'badge_class': 'bg-slate-100 text-slate-600 border-slate-300',
            'is_aktif': False,
            'keterangan_waktu': 'Dinonaktifkan manual oleh admin'
        }

    t_mulai = (popup_dict.get('tanggal_mulai') or '').strip()
    t_selesai = (popup_dict.get('tanggal_selesai') or '').strip()

    if not t_mulai and not t_selesai:
        return {
            'status_waktu': 'Tayang',
            'label': 'Tayang (Aktif)',
            'badge_class': 'bg-emerald-100 text-emerald-900 border-emerald-300',
            'is_aktif': True,
            'keterangan_waktu': 'Tanpa batas waktu (selalu aktif)'
        }

    now = datetime.now()
    dt_mulai = None
    dt_selesai = None

    if t_mulai:
        try:
            clean_m = t_mulai.replace('T', ' ')
            if len(clean_m) == 10:
                clean_m += ' 00:00:00'
            elif len(clean_m) == 16:
                clean_m += ':00'
            dt_mulai = datetime.strptime(clean_m, '%Y-%m-%d %H:%M:%S')
        except Exception:
            pass

    if t_selesai:
        try:
            clean_s = t_selesai.replace('T', ' ')
            if len(clean_s) == 10:
                clean_s += ' 23:59:59'
            elif len(clean_s) == 16:
                clean_s += ':59'
            dt_selesai = datetime.strptime(clean_s, '%Y-%m-%d %H:%M:%S')
        except Exception:
            pass

    if dt_mulai and now < dt_mulai:
        return {
            'status_waktu': 'Terjadwal',
            'label': 'Terjadwal',
            'badge_class': 'bg-sky-100 text-sky-800 border-sky-300',
            'is_aktif': False,
            'keterangan_waktu': f"Mulai tayang {dt_mulai.strftime('%d/%m/%Y %H:%M')} WIB"
        }

    if dt_selesai and now > dt_selesai:
        return {
            'status_waktu': 'Kedaluwarsa',
            'label': 'Kedaluwarsa (Terhenti Otomatis)',
            'badge_class': 'bg-rose-100 text-rose-800 border-rose-300',
            'is_aktif': False,
            'keterangan_waktu': f"Otomatis terhenti sejak {dt_selesai.strftime('%d/%m/%Y %H:%M')} WIB"
        }

    info_s = f"Berakhir pada {dt_selesai.strftime('%d/%m/%Y %H:%M')} WIB" if dt_selesai else 'Aktif'
    return {
        'status_waktu': 'Tayang',
        'label': 'Tayang (Aktif)',
        'badge_class': 'bg-emerald-100 text-emerald-900 border-emerald-300',
        'is_aktif': True,
        'keterangan_waktu': info_s
    }

@app.context_processor
def inject_global_data():
    data = {
        'is_superadmin': session.get('role') == 'superadmin',
        'current_role': session.get('role', 'tamu'),
        'current_nama': session.get('nama', 'Pengguna')
    }
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
        row = cursor.fetchone()
        data['profil_global'] = dict(row or {})

        cursor.execute("SELECT * FROM running_texts WHERE is_active = 1 ORDER BY urutan ASC, id ASC")
        data['running_texts_global'] = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM kategori_pengaduan ORDER BY urutan ASC, id ASC")
        data['kategori_pengaduan_global'] = [dict(r) for r in cursor.fetchall()]

        # Popup Informasi Aktif (Tayang & Masih dalam batas waktu yang valid)
        cursor.execute("SELECT * FROM popup_informasi WHERE status = 'Tayang' ORDER BY urutan ASC, id DESC")
        pop_candidates = [dict(r) for r in cursor.fetchall()]
        popup_list_aktif = []
        for p in pop_candidates:
            st = hitung_status_waktu_popup(p)
            if st['is_aktif']:
                p['status_info'] = st
                popup_list_aktif.append(p)
        data['popup_list_aktif_global'] = popup_list_aktif
        data['popup_aktif_global'] = popup_list_aktif[0] if popup_list_aktif else None

        # Banner Slider Aktif (Tayang)
        cursor.execute("SELECT * FROM banner_slider WHERE is_active = 1 ORDER BY urutan ASC, id ASC")
        data['banner_sliders_global'] = [dict(r) for r in cursor.fetchall()]

        # Hitung Pengajuan Galeri Warga Pending
        try:
            cursor.execute("SELECT COUNT(*) FROM galeri WHERE status = 'Menunggu Persetujuan'")
            data['pending_galeri_count_global'] = cursor.fetchone()[0] or 0
        except Exception:
            data['pending_galeri_count_global'] = 0

        conn.close()
    except Exception:
        data['profil_global'] = {}
        data['running_texts_global'] = []
        data['kategori_pengaduan_global'] = []
        data['popup_aktif_global'] = None
        data['banner_sliders_global'] = []
        data['pending_galeri_count_global'] = 0

    try:
        data['statistik_pengunjung'] = get_visitor_stats()
    except Exception:
        data['statistik_pengunjung'] = {
            'hari_ini': 142,
            'minggu_ini': 986,
            'bulan_ini': 3840,
            'total': 28519,
            'hari_ini_fmt': '142',
            'minggu_ini_fmt': '986',
            'bulan_ini_fmt': '3.840',
            'total_fmt': '28.519'
        }
    return data

@app.before_request
def track_visitor_hit():
    """Mencatat jumlah kunjungan ke halaman publik secara otomatis"""
    if request.method == 'GET' and not (
        request.path.startswith('/static') or 
        request.path.startswith('/admin') or 
        request.path.startswith('/api')
    ):
        try:
            record_visitor_hit()
        except Exception:
            pass

# Decorator Hak Akses 1: Login Required (Admin & Super Admin)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu untuk mengakses panel admin.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator Hak Akses 2: Super Admin Required (Khusus Super Admin)
def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('admin_login'))
        if session.get('role') != 'superadmin':
            record_activity_log(
                'ACCESS_DENIED',
                f"Percobaan akses ke fitur khusus Super Admin ({request.path}) ditolak.",
                username=session.get('username'),
                user_id=session.get('user_id'),
                ip_address=request.headers.get('X-Forwarded-For', request.remote_addr),
                user_agent=request.user_agent.string
            )
            flash('Akses Ditolak: Fitur ini hanya dapat diakses oleh Super Admin (Kepala Desa / Administrator Utama).', 'danger')
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Helper Keamanan Login: Rate Limiting & Anti-Brute Force
def check_login_rate_limit(ip_address, username):
    """Mencegah serangan brute force:
       - Akun spesifik diblokir jika salah password >= 5 kali berturut-turut dalam 15 menit.
       - IP publik diblokir jika melakukan spam serangan >= 25 kali dalam 15 menit.
       - Localhost (127.0.0.1, ::1, localhost) TIDAK PERNAH diblokir berdasarkan IP
         agar pengembang / administrator lokal tidak terblokir dari komputernya sendiri.
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 1. Cek kegagalan per-username spesifik
        failed_user = 0
        if username:
            cursor.execute('''
            SELECT COUNT(*) FROM login_attempts 
            WHERE username = ? 
              AND is_success = 0 
              AND attempted_at >= datetime('now', '-15 minutes')
            ''', (username,))
            failed_user = cursor.fetchone()[0] or 0
            if failed_user >= 5:
                conn.close()
                return True, failed_user

        # 2. Cek kegagalan per-IP (hanya untuk IP eksternal non-localhost)
        is_localhost = ip_address in ('127.0.0.1', '::1', 'localhost', 'testclient')
        if not is_localhost:
            cursor.execute('''
            SELECT COUNT(*) FROM login_attempts 
            WHERE ip_address = ? 
              AND is_success = 0 
              AND attempted_at >= datetime('now', '-15 minutes')
            ''', (ip_address,))
            failed_ip = cursor.fetchone()[0] or 0
            if failed_ip >= 25:
                conn.close()
                return True, failed_ip

        conn.close()
        return False, failed_user
    except Exception:
        return False, 0

def record_login_attempt(ip_address, username, is_success):
    """Mencatat percobaan login untuk audit keamanan"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO login_attempts (ip_address, username, is_success)
        VALUES (?, ?, ?)
        ''', (ip_address, username, 1 if is_success else 0))
        conn.commit()
        conn.close()
    except Exception:
        pass

# ==========================================
# PUBLIC FRONTEND ROUTES
# ==========================================

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Profil Desa
    cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
    profil = dict(cursor.fetchone() or {})

    # 2. Perangkat Desa (SOTK)
    cursor.execute("SELECT * FROM perangkat_desa ORDER BY urutan ASC")
    perangkat = [dict(row) for row in cursor.fetchall()]

    # 2.1 Sejarah Desa (Hanya yang berstatus Tayang)
    cursor.execute("SELECT * FROM sejarah_desa WHERE status = 'Tayang' ORDER BY urutan ASC, id ASC")
    sejarah_list = [dict(row) for row in cursor.fetchall()]

    # 2.2 Kepala Desa dari Masa ke Masa (Disusun mulai dari kades yang menjabat sekarang ke kades lampau)
    cursor.execute("""
        SELECT * FROM kades_masa_ke_masa 
        WHERE status = 'Tayang'
        ORDER BY CASE WHEN status_jabatan = 'Menjabat' THEN 0 ELSE 1 END,
                 tahun_mulai DESC, urutan ASC, id DESC
    """)
    kades_riwayat_list = [dict(row) for row in cursor.fetchall()]

    # Otomatis ambil data Kepala Desa dari tabel SOTK (perangkat_desa)
    kades_sotk = None
    for p in perangkat:
        jab = (p.get('jabatan') or '').strip().lower()
        if 'kepala desa' in jab or 'kuwu' in jab or 'pembekal' in jab:
            kades_sotk = p
            break
    if not kades_sotk and perangkat:
        kades_sotk = perangkat[0]

    # Sinkronkan jika foto kades di profil belum sama dengan SOTK
    if kades_sotk and kades_sotk.get('foto'):
        profil['foto_kades'] = kades_sotk['foto']
        if kades_sotk.get('nama'):
            profil['nama_kades'] = kades_sotk['nama']
        if kades_sotk.get('periode'):
            profil['periode_kades'] = kades_sotk['periode']

    # 3. Wisata (Hanya yang disetujui / approved oleh admin)
    cursor.execute("SELECT * FROM wisata WHERE status = 'Disetujui' OR status IS NULL ORDER BY urutan ASC")
    wisata = [dict(row) for row in cursor.fetchall()]
    for w in wisata:
        if w.get('fasilitas'):
            w['fasilitas_list'] = [f.strip() for f in w['fasilitas'].split(',')]

    # 4. UMKM (Hanya yang disetujui / approved oleh admin)
    cursor.execute("SELECT * FROM umkm WHERE status = 'Disetujui' OR status IS NULL ORDER BY id DESC")
    umkm = [dict(row) for row in cursor.fetchall()]

    # 5. Berita (Hanya yang statusnya Tayang di website)
    cursor.execute("SELECT * FROM berita WHERE status = 'Tayang' OR status IS NULL ORDER BY id DESC LIMIT 6")
    berita = [dict(row) for row in cursor.fetchall()]

    # 6. APBDes
    cursor.execute("SELECT * FROM apbdes WHERE id = 1")
    apbdes_row = cursor.fetchone()
    apbdes = {}
    if apbdes_row:
        apbdes = dict(apbdes_row)
        apbdes['sumber'] = json.loads(apbdes.get('data_sumber_json') or '[]')
        apbdes['belanja'] = json.loads(apbdes.get('data_belanja_json') or '[]')

    # 7. Statistik Kependudukan & Deret Waktu Tahunan (Data Series)
    cursor.execute("SELECT id, tahun, total_penduduk, laki_laki, perempuan, kepala_keluarga, penduduk_sementara, mutasi_penduduk FROM statistik ORDER BY tahun ASC")
    raw_series = [dict(row) for row in cursor.fetchall()]
    statistik_series = []
    prev_tot = None
    for s in raw_series:
        tot = s.get('total_penduduk', 0)
        l = s.get('laki_laki', 0)
        p = s.get('perempuan', 0)
        kk = s.get('kepala_keluarga', 0)
        sr = round((l / p * 100), 1) if p > 0 else 0
        pl = round((l / tot * 100), 1) if tot > 0 else 0
        pp = round((p / tot * 100), 1) if tot > 0 else 0
        rkk = round((tot / kk), 1) if kk > 0 else 0
        growth = None
        if prev_tot and prev_tot > 0:
            growth = round(((tot - prev_tot) / prev_tot * 100), 1)
        prev_tot = tot
        s_data = {
            'id': s.get('id'),
            'tahun': s.get('tahun'),
            'total_penduduk': tot,
            'laki_laki': l,
            'perempuan': p,
            'kepala_keluarga': kk,
            'sex_ratio': sr,
            'persen_laki': pl,
            'persen_perempuan': pp,
            'rata_kk': rkk,
            'growth_yoy': growth
        }
        statistik_series.append(s_data)

    tahun_list = [s['tahun'] for s in reversed(statistik_series) if s.get('tahun')]
    if not tahun_list:
        tahun_list = [2026]

    requested_year = request.args.get('tahun', type=int)
    if requested_year and requested_year in tahun_list:
        active_year = requested_year
    else:
        active_year = tahun_list[0] if tahun_list else 2026

    # Ambil baris statistik untuk tahun aktif
    cursor.execute("SELECT * FROM statistik WHERE tahun = ? ORDER BY id ASC LIMIT 1", (active_year,))
    stat_row = cursor.fetchone()
    if not stat_row:
        cursor.execute("SELECT * FROM statistik ORDER BY tahun DESC, id ASC LIMIT 1")
        stat_row = cursor.fetchone()

    statistik = {}
    if stat_row:
        statistik = dict(stat_row)
        active_year = statistik.get('tahun') or active_year
        statistik['usia'] = json.loads(statistik.get('data_usia_json') or '[]')
        statistik['pekerjaan'] = json.loads(statistik.get('data_pekerjaan_json') or '[]')

    # 7b. Rincian Statistik SLS (RT/RW)
    cursor.execute("SELECT * FROM statistik_sls WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (active_year,))
    statistik_sls = [dict(row) for row in cursor.fetchall()]

    # 7c. Rincian Statistik Kelompok Umur (Piramida Penduduk)
    cursor.execute("SELECT * FROM statistik_umur WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (active_year,))
    statistik_umur = [dict(row) for row in cursor.fetchall()]

    # 7d. Rincian Statistik Pendidikan per SLS
    cursor.execute("SELECT * FROM statistik_pendidikan WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (active_year,))
    statistik_pendidikan = [dict(row) for row in cursor.fetchall()]

    # 7e. Rincian Statistik Status Perkawinan per SLS
    cursor.execute("SELECT * FROM statistik_perkawinan WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (active_year,))
    statistik_perkawinan = [dict(row) for row in cursor.fetchall()]

    # 7f. Rincian Statistik Status Pencatatan Perkawinan per SLS
    cursor.execute("SELECT * FROM statistik_pencatatan_nikah WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (active_year,))
    statistik_pencatatan_nikah = [dict(row) for row in cursor.fetchall()]

    # 7g. Rincian Statistik Agama dan Kepercayaan per SLS
    cursor.execute("SELECT * FROM statistik_agama WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (active_year,))
    statistik_agama = [dict(row) for row in cursor.fetchall()]

    # 7h. Rincian Statistik Penerima Bantuan Sosial (Bansos) per SLS
    cursor.execute("SELECT * FROM statistik_bansos WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (active_year,))
    statistik_bansos = [dict(row) for row in cursor.fetchall()]

    # 7i. Rincian Statistik Kesehatan & Kesejahteraan Anak (Yatim Piatu, Gizi Buruk, Stunting)
    cursor.execute("SELECT * FROM statistik_anak WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (active_year,))
    statistik_anak = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM statistik_gizi_buruk WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (active_year,))
    statistik_gizi_buruk = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM statistik_stunting WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (active_year,))
    statistik_stunting = [dict(row) for row in cursor.fetchall()]

    # 8. Buku Publikasi Desa
    cursor.execute("SELECT * FROM buku_publikasi WHERE status = 'Tayang' ORDER BY is_featured DESC, id DESC LIMIT 4")
    buku_publikasi = [dict(row) for row in cursor.fetchall()]

    # 8.1 Pembangunan Desa (Proyek & Kegiatan yang Sedang dan Sudah Dikerjakan)
    cursor.execute("""
        SELECT * FROM pembangunan_desa 
        WHERE status_tayang = 'Tayang' 
        ORDER BY urutan ASC, id DESC
    """)
    pembangunan_list = []
    for row in cursor.fetchall():
        item = dict(row)
        try:
            item['foto_list'] = json.loads(item.get('data_foto_json') or '[]')
        except Exception:
            item['foto_list'] = []
        pembangunan_list.append(item)

    # 9. Kategori Pengaduan & Daftar Monitoring Aduan
    cursor.execute("SELECT * FROM kategori_pengaduan ORDER BY urutan ASC, id ASC")
    kategori_pengaduan_list = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT id, no_tiket, nama, kontak, kategori, pesan, lampiran, status, uraian_tindak_lanjut, created_at FROM pengaduan ORDER BY id DESC LIMIT 20")
    monitoring_aduan_list = [dict(row) for row in cursor.fetchall()]

    # 10. Banner Slider Hero
    cursor.execute("SELECT * FROM banner_slider WHERE is_active = 1 ORDER BY urutan ASC, id ASC")
    sliders = [dict(row) for row in cursor.fetchall()]

    # 11. Galeri Foto Kegiatan & Sub-Galeri Piagam Penghargaan
    cursor.execute("SELECT * FROM galeri WHERE tipe = 'kegiatan' AND status = 'Tayang' ORDER BY tanggal DESC, id DESC")
    galeri_list = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM galeri WHERE tipe = 'penghargaan' AND status = 'Tayang' ORDER BY tahun_penghargaan DESC, tanggal DESC, id DESC")
    penghargaan_list = [dict(row) for row in cursor.fetchall()]

    conn.close()

    try:
        sls_geojson = buat_geojson_sls_dengan_penduduk(active_year)
    except Exception as e:
        print("Warning: Gagal membuat sls_geojson di beranda:", e)
        sls_geojson = {}

    return render_template(
        'index.html',
        sls_geojson=sls_geojson,
        profil=profil,
        sliders=sliders,
        galeri_list=galeri_list,
        penghargaan_list=penghargaan_list,
        kades_sotk=kades_sotk,
        perangkat=perangkat,
        sejarah_list=sejarah_list,
        kades_riwayat_list=kades_riwayat_list,
        wisata=wisata,
        umkm=umkm,
        berita=berita,
        buku_publikasi=buku_publikasi,
        pembangunan_list=pembangunan_list,
        kategori_pengaduan_list=kategori_pengaduan_list,
        monitoring_aduan_list=monitoring_aduan_list,
        apbdes=apbdes,
        statistik=statistik,
        statistik_series=statistik_series,
        tahun_list=tahun_list,
        active_year=active_year,
        statistik_sls=statistik_sls,
        statistik_umur=statistik_umur,
        statistik_pendidikan=statistik_pendidikan,
        pendidikan_columns=PENDIDIKAN_COLUMNS,
        statistik_perkawinan=statistik_perkawinan,
        statistik_pencatatan_nikah=statistik_pencatatan_nikah,
        statistik_agama=statistik_agama,
        agama_columns=AGAMA_COLUMNS,
        statistik_bansos=statistik_bansos,
        bansos_columns=BANSOS_COLUMNS,
        statistik_anak=statistik_anak,
        anak_columns=ANAK_COLUMNS,
        statistik_gizi_buruk=statistik_gizi_buruk,
        gizi_buruk_columns=GIZI_BURUK_COLUMNS,
        statistik_stunting=statistik_stunting,
        stunting_columns=STUNTING_COLUMNS
    )


@app.route('/surat/<no_reg>/cetak')
def cetak_surat(no_reg):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM layanan_surat WHERE no_reg = ?", (no_reg,))
    surat = cursor.fetchone()
    cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
    profil = cursor.fetchone()
    conn.close()

    if not surat:
        return "Surat dengan nomor registrasi tersebut tidak ditemukan.", 404

    return render_template('surat_cetak.html', surat=dict(surat), profil=dict(profil or {}))

# ==========================================
# PUBLIC API ENDPOINTS
# ==========================================

@app.route('/api/surat/ajukan', methods=['POST'])
def api_ajukan_surat():
    # Cek status maintenance layanan surat
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status_maintenance_surat, pesan_maintenance_surat FROM profil_desa WHERE id = 1")
    row_prof = cursor.fetchone()
    if row_prof and ('status_maintenance_surat' in row_prof.keys()) and row_prof['status_maintenance_surat'] == 1:
        pesan = row_prof['pesan_maintenance_surat'] or 'Layanan Sedang Maintenace. Mohon maaf atas ketidaknyamananya !!!'
        conn.close()
        return jsonify({'success': False, 'message': pesan}), 503

    data = request.get_json(silent=True) or request.form
    jenis_surat = data.get('jenis_surat')
    nik = data.get('nik')
    nama = data.get('nama') or data.get('nama_lengkap')
    wa = data.get('wa') or data.get('no_hp') or data.get('telepon')
    dusun = data.get('dusun') or ''
    rt = data.get('rt') or data.get('alamat') or ''
    keperluan = data.get('keperluan')

    if not (jenis_surat and nik and nama and wa and keperluan):
        conn.close()
        return jsonify({'success': False, 'message': 'Mohon lengkapi seluruh formulir bertanda bintang (*).'}), 400

    no_reg = f"PPY-2026-{random.randint(1000, 9999)}"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO layanan_surat (no_reg, jenis_surat, nik, nama, wa, dusun, rt, keperluan, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Menunggu')
    ''', (no_reg, jenis_surat, nik, nama, wa, dusun, rt, keperluan))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': 'Permohonan surat berhasil dikirim ke Kantor Desa Papayan.',
        'no_reg': no_reg,
        'cetak_url': url_for('cetak_surat', no_reg=no_reg)
    })

@app.route('/api/pengaduan/kirim', methods=['POST'])
def api_kirim_pengaduan():
    # Support form-data and json
    if request.is_json:
        data = request.get_json(silent=True) or {}
        nama = (data.get('nama') or '').strip()
        kontak = (data.get('kontak') or data.get('no_hp') or data.get('telepon') or '').strip()
        kategori = (data.get('kategori') or 'Umum').strip()
        pesan = (data.get('pesan') or data.get('pengaduan') or '').strip()
        lampiran_path = None
    else:
        nama = (request.form.get('nama') or '').strip()
        kontak = (request.form.get('kontak') or request.form.get('no_hp') or request.form.get('telepon') or '').strip()
        kategori = (request.form.get('kategori') or 'Umum').strip()
        pesan = (request.form.get('pesan') or request.form.get('pengaduan') or '').strip()

        lampiran_path = None
        file_lampiran = request.files.get('lampiran')
        if file_lampiran and file_lampiran.filename:
            ext = os.path.splitext(file_lampiran.filename)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.pdf', '.webp']:
                filename = f"lampiran_{int(time.time())}_{secure_filename(file_lampiran.filename)}"
                os.makedirs('static/uploads/pengaduan', exist_ok=True)
                full_path = os.path.join('static', 'uploads', 'pengaduan', filename)
                file_lampiran.save(full_path)
                lampiran_path = full_path.replace('\\', '/')

    if not (nama and kontak and pesan):
        return jsonify({'success': False, 'message': 'Mohon lengkapi Nama, Nomor Telepon/WA, dan Detail Aduan Anda.'}), 400

    no_tiket = f"ADUAN-{random.randint(10000, 99990)}"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO pengaduan (no_tiket, nama, kontak, kategori, pesan, lampiran, status, uraian_tindak_lanjut)
    VALUES (?, ?, ?, ?, ?, ?, 'Belum Ditanggapi', '')
    ''', (no_tiket, nama, kontak, kategori, pesan, lampiran_path))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': f'Aspirasi berhasil diterima. Nomor tiket Anda: {no_tiket}',
        'no_tiket': no_tiket
    })

# Endpoint Pengiriman Feedback Penilaian Kepuasan Pengunjung
@app.route('/api/feedback/kirim', methods=['POST'])
def api_kirim_feedback():
    if request.is_json:
        data = request.get_json(silent=True) or {}
        rating = data.get('rating')
        pekerjaan = (data.get('pekerjaan') or '').strip()
        aspek_peningkatan = data.get('aspek_peningkatan') or []
        saran = (data.get('saran') or '').strip()
    else:
        rating = request.form.get('rating')
        pekerjaan = (request.form.get('pekerjaan') or '').strip()
        aspek_peningkatan = request.form.getlist('aspek_peningkatan') or request.form.get('aspek_peningkatan', '').split(',')
        saran = (request.form.get('saran') or '').strip()

    try:
        rating = int(rating)
    except (ValueError, TypeError):
        rating = None

    if not rating or rating < 1 or rating > 5:
        return jsonify({'success': False, 'message': 'Mohon berikan penilaian kepuasan Anda (pilih salah satu ikon emotikon).'}), 400

    if isinstance(aspek_peningkatan, list):
        aspek_str = ', '.join([str(a).strip() for a in aspek_peningkatan if str(a).strip()])
    else:
        aspek_str = str(aspek_peningkatan).strip()

    ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '')
    user_agent = request.headers.get('User-Agent', '')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO feedback_kepuasan (rating, pekerjaan, aspek_peningkatan, saran, ip_address, user_agent)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (rating, pekerjaan, aspek_str, saran, ip_address, user_agent))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': 'Terima kasih atas penilaian dan masukan Anda! Feedback Anda sangat membantu kami dalam menyempurnakan website desa ini.'
    })

@app.route('/api/pengaduan/kategori')
def api_kategori_pengaduan():
    """Mengembalikan daftar kategori pengaduan yang aktif"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nama, keterangan, urutan FROM kategori_pengaduan ORDER BY urutan ASC, id ASC")
    kategori_list = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({'success': True, 'data': kategori_list})

@app.route('/api/pengaduan/tracking/<no_tiket>')
def api_tracking_pengaduan(no_tiket):
    """Lacak status dan uraian tindak lanjut pengaduan berdasarkan nomor tiket"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, no_tiket, nama, kategori, pesan, lampiran, status, uraian_tindak_lanjut, created_at FROM pengaduan WHERE no_tiket = ?", (no_tiket.strip().upper(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({'success': True, 'data': dict(row)})
    return jsonify({'success': False, 'message': 'Nomor tiket aduan tidak ditemukan.'}), 404

@app.route('/api/surat/tracking/<no_reg>')
def api_tracking_surat(no_reg):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM layanan_surat WHERE no_reg = ?", (no_reg,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({'success': True, 'data': dict(row)})
    return jsonify({'success': False, 'message': 'Nomor registrasi surat tidak ditemukan.'}), 404

@app.route('/api/statistik-kunjungan')
def api_statistik_kunjungan():
    """Mengembalikan statistik kunjungan hari ini, minggu ini, bulan ini, dan total kunjungan"""
    stats = get_visitor_stats()
    return jsonify({'success': True, 'data': stats})

@app.route('/peta')
def peta_desa():
    """Halaman Peta Wilayah & Sistem Informasi Geografis Tematik Kependudukan SLS (RT/RW) Desa"""
    tahun = request.args.get('tahun', type=int) or 2026
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
    profil = cursor.fetchone()

    cursor.execute("SELECT DISTINCT tahun FROM statistik_sls ORDER BY tahun DESC")
    tahun_list = [r[0] for r in cursor.fetchall() if r[0]]
    if not tahun_list:
        tahun_list = [2026, 2025]
    if tahun not in tahun_list:
        tahun = tahun_list[0]

    # Pre-build data for all available years so client-side switching works instantly with ZERO 404
    data_semua_tahun = {}
    for th in tahun_list:
        cursor.execute("SELECT * FROM statistik_sls WHERE tahun = ? ORDER BY no_urut ASC", (th,))
        th_sls_list = [dict(r) for r in cursor.fetchall()]
        th_geojson = buat_geojson_sls_dengan_penduduk(th)
        data_semua_tahun[th] = {
            'sls_list': th_sls_list,
            'geojson': th_geojson,
            'total_jiwa': sum(r.get('total', 0) for r in th_sls_list),
            'total_l': sum(r.get('laki_laki', 0) for r in th_sls_list),
            'total_p': sum(r.get('perempuan', 0) for r in th_sls_list),
            'total_kk': sum(r.get('keluarga', 0) for r in th_sls_list)
        }

    sls_list = data_semua_tahun[tahun]['sls_list']
    total_jiwa = data_semua_tahun[tahun]['total_jiwa']
    total_l = data_semua_tahun[tahun]['total_l']
    total_p = data_semua_tahun[tahun]['total_p']
    total_kk = data_semua_tahun[tahun]['total_kk']
    geojson_data = data_semua_tahun[tahun]['geojson']

    # Titik wisata / fasilitas (filter khusus koordinat wilayah Papayan)
    cursor.execute("""
        SELECT id, nama, kategori, lokasi, latitude, longitude, gambar 
        FROM wisata 
        WHERE (status = 'Disetujui' OR status IS NULL)
          AND latitude BETWEEN -7.65 AND -7.30
          AND longitude BETWEEN 108.05 AND 108.35
    """)
    wisata_list = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return render_template(
        'peta.html',
        profil=profil,
        tahun=tahun,
        tahun_list=tahun_list,
        sls_list=sls_list,
        total_jiwa=total_jiwa,
        total_l=total_l,
        total_p=total_p,
        total_kk=total_kk,
        wisata_list=wisata_list,
        geojson_data=geojson_data,
        data_semua_tahun=data_semua_tahun
    )

@app.route('/api/peta/sls-geojson')
def api_peta_sls_geojson():
    """Mengembalikan FeatureCollection GeoJSON poligon batas RT/RW digabung data demografi penduduk"""
    tahun = request.args.get('tahun', type=int) or 2026
    data = buat_geojson_sls_dengan_penduduk(tahun)
    return jsonify(data)

@app.route('/admin/peta')
@login_required
def admin_peta():
    """Menu Pengelolaan Peta Wilayah, Poligon SLS & Titik Koordinat RT"""
    tahun = request.args.get('tahun', type=int) or 2026
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
    profil = cursor.fetchone()

    cursor.execute("SELECT DISTINCT tahun FROM statistik_sls ORDER BY tahun DESC")
    tahun_list = [r[0] for r in cursor.fetchall() if r[0]]
    if not tahun_list:
        tahun_list = [2026]

    cursor.execute("SELECT * FROM statistik_sls WHERE tahun = ? ORDER BY no_urut ASC", (tahun,))
    sls_list = [dict(r) for r in cursor.fetchall()]

    conn.close()

    geojson_data = buat_geojson_sls_dengan_penduduk(tahun)

    return render_template(
        'admin/peta.html',
        profil=profil,
        tahun=tahun,
        tahun_list=tahun_list,
        sls_list=sls_list,
        geojson_data=geojson_data
    )

@app.route('/admin/peta/sync-kml', methods=['POST'])
@login_required
def admin_peta_sync_kml():
    """Mengunduh dan memperbarui poligon dari URL KML Google Maps"""
    kml_url = request.form.get('kml_url', '').strip() or DEFAULT_KML_URL
    try:
        unduh_kml_dari_url(kml_url)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE profil_desa SET kml_url = ? WHERE id = 1", (kml_url,))
        conn.commit()
        conn.close()
        # Regenerate cache
        buat_geojson_sls_dengan_penduduk(2026)
        flash('Poligon KML batas RT/RW berhasil disinkronkan dan diperbarui dari Google Maps!', 'success')
    except Exception as e:
        flash(f'Gagal menyinkronkan KML dari Google Maps: {str(e)}', 'danger')

    return redirect(url_for('admin_peta'))

@app.route('/admin/peta/simpan-batas', methods=['POST'])
@login_required
def admin_peta_simpan_batas():
    """Menyimpan batas wilayah sebelah utara, selatan, timur, dan barat"""
    batas_utara = request.form.get('batas_utara', '').strip()
    batas_selatan = request.form.get('batas_selatan', '').strip()
    batas_timur = request.form.get('batas_timur', '').strip()
    batas_barat = request.form.get('batas_barat', '').strip()

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE profil_desa 
            SET batas_utara = ?, batas_selatan = ?, batas_timur = ?, batas_barat = ?
            WHERE id = 1
        """, (batas_utara, batas_selatan, batas_timur, batas_barat))
        conn.commit()
        conn.close()

        record_activity_log(
            'UPDATE_BATAS_WILAYAH',
            f"Memperbarui batas wilayah desa: Utara ({batas_utara}), Selatan ({batas_selatan}), Barat ({batas_barat}), Timur ({batas_timur})",
            username=session.get('username')
        )
        flash('Data batas wilayah desa (Utara, Selatan, Barat, Timur) berhasil disimpan dan diperbarui di halaman peta!', 'success')
    except Exception as e:
        flash(f'Gagal menyimpan batas wilayah: {str(e)}', 'danger')

    return redirect(url_for('admin_peta'))

# ==========================================
# ADMIN AUTHENTICATION
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'user_id' in session:
        return redirect(url_for('admin_dashboard'))

    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr) or '127.0.0.1'
    if ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
    profil_row = cursor.fetchone()
    profil = dict(profil_row or {})
    conn.close()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # 1. Cek Rate Limiting / Brute-force Protection (Maks 5 kegagalan dalam 15 menit)
        is_locked, failed_attempts = check_login_rate_limit(ip_address, username)
        if is_locked:
            record_activity_log(
                'LOGIN_BLOCKED',
                f"Sistem memblokir sementara percobaan login brute-force untuk username: {username} dari IP: {ip_address}",
                ip_address=ip_address,
                user_agent=request.user_agent.string
            )
            flash('Keamanan Sistem: Terlalu banyak percobaan gagal login (5 kali). Akses Anda dikunci sementara selama 15 menit demi melindungi keamanan data desa.', 'danger')
            return render_template('admin/login.html', is_locked=True, profil=profil)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        # 2. Verifikasi Password
        if user and check_password_hash(user['password_hash'], password):
            # Cek Status Keaktifan Akun
            if user['status'] != 'aktif':
                record_activity_log(
                    'LOGIN_REJECTED',
                    f"Percobaan login ke akun non-aktif: {username}",
                    username=username,
                    user_id=user['id'],
                    ip_address=ip_address,
                    user_agent=request.user_agent.string
                )
                conn.close()
                flash('Akun ini sedang dinonaktifkan oleh Super Admin. Silakan hubungi Administrator Desa.', 'danger')
                return render_template('admin/login.html', profil=profil)

            # Catat login sukses & reset counter
            record_login_attempt(ip_address, username, True)
            cursor.execute("DELETE FROM login_attempts WHERE username = ? AND is_success = 0", (username,))
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user['id'],))
            conn.commit()
            conn.close()

            record_activity_log(
                'LOGIN_SUCCESS',
                f"Pengguna berhasil login sebagai {user['role'].upper()}",
                username=user['username'],
                user_id=user['id'],
                ip_address=ip_address,
                user_agent=request.user_agent.string
            )

            # Regenerasi session untuk mencegah Session Fixation
            session.clear()
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['nama'] = user['nama']
            session['role'] = user['role']

            flash(f"Selamat datang, {user['nama']}. Anda login sebagai {('Super Admin (Akses Penuh)' if user['role'] == 'superadmin' else 'Admin (Operator Pelayanan)')}.", 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            conn.close()
            # Catat login gagal
            record_login_attempt(ip_address, username, False)
            record_activity_log(
                'LOGIN_FAILED',
                f"Percobaan login gagal ke-{failed_attempts + 1} untuk username: {username}",
                ip_address=ip_address,
                user_agent=request.user_agent.string
            )
            sisa = 5 - (failed_attempts + 1)
            if sisa > 0:
                flash(f'Username atau kata sandi salah. Sisa percobaan login: {sisa} kali sebelum akun dikunci sementara.', 'danger')
            else:
                flash('Batas percobaan gagal telah tercapai (5 kali). Akses dikunci sementara selama 15 menit.', 'danger')

    return render_template('admin/login.html', profil=profil)

@app.route('/admin/buka-kunci', methods=['GET', 'POST'])
def admin_buka_kunci():
    """Membuka kunci proteksi brute-force untuk pemulihan akses administrator"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM login_attempts WHERE is_success = 0")
        conn.commit()
        conn.close()
        flash('Kunci keamanan login berhasil dibuka kembali. Silakan pilih level dan masukkan akun Anda.', 'success')
    except Exception as e:
        flash(f'Gagal mereset kunci keamanan: {str(e)}', 'danger')
    return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr) or '127.0.0.1'
    if session.get('username'):
        record_activity_log(
            'LOGOUT',
            f"User {session.get('username')} keluar dari sesi admin.",
            username=session.get('username'),
            user_id=session.get('user_id'),
            ip_address=ip_address,
            user_agent=request.user_agent.string
        )
    session.clear()
    flash('Anda telah keluar dari sesi admin dengan aman.', 'info')
    return redirect(url_for('admin_login'))

# ==========================================
# ADMIN DASHBOARD & CMS
# ==========================================

@app.route('/admin')
@login_required
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Permohonan Surat
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN status='Menunggu' THEN 1 ELSE 0 END), SUM(CASE WHEN status='Diproses' THEN 1 ELSE 0 END), SUM(CASE WHEN status='Selesai' THEN 1 ELSE 0 END) FROM layanan_surat")
    s_row = cursor.fetchone() or (0, 0, 0, 0)
    total_surat = s_row[0] or 0
    surat_pending = s_row[1] or 0
    surat_proses = s_row[2] or 0
    surat_selesai = s_row[3] or 0

    # 2. Aspirasi & Pengaduan
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN status='Belum Ditanggapi' OR status='Menunggu' THEN 1 ELSE 0 END), SUM(CASE WHEN status='Perlu Perlakuan Khusus' THEN 1 ELSE 0 END), SUM(CASE WHEN status='Sudah Diselesaikan' OR status='Selesai' THEN 1 ELSE 0 END) FROM pengaduan")
    p_row = cursor.fetchone() or (0, 0, 0, 0)
    total_aduan = p_row[0] or 0
    aduan_pending = p_row[1] or 0
    aduan_khusus = p_row[2] or 0
    aduan_selesai = p_row[3] or 0

    # 3. Feedback Kepuasan Warga
    cursor.execute("SELECT COUNT(*), COALESCE(AVG(rating), 5.0), COALESCE(SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END), 0) FROM feedback_kepuasan")
    fb_row = cursor.fetchone() or (0, 5.0, 0)
    total_feedback = fb_row[0] or 0
    avg_feedback_rating = round(fb_row[1], 1) if total_feedback > 0 else 5.0
    puas_feedback_pct = round((fb_row[2] / total_feedback * 100), 1) if total_feedback > 0 else 100.0

    # 4. Berita, Galeri & Piagam Prestasi
    cursor.execute("SELECT COUNT(*) FROM berita")
    total_berita = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*), COALESCE(SUM(CASE WHEN tipe = 'penghargaan' OR kategori = 'Piagam & Penghargaan' THEN 1 ELSE 0 END), 0), COALESCE(SUM(CASE WHEN status = 'Menunggu' OR status = 'pending' THEN 1 ELSE 0 END), 0) FROM galeri")
    g_row = cursor.fetchone() or (0, 0, 0)
    total_galeri = g_row[0] or 0
    total_prestasi = g_row[1] or 0
    pending_galeri = g_row[2] or 0

    # 5. UMKM, Wisata & Publikasi Digital
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(CASE WHEN status='Disetujui' OR status='disetujui' OR status='aktif' THEN 1 ELSE 0 END), 0), COALESCE(SUM(CASE WHEN status='Menunggu Approval' OR status='pending' THEN 1 ELSE 0 END), 0) FROM umkm")
    u_row = cursor.fetchone() or (0, 0, 0)
    total_umkm = u_row[0] or 0
    umkm_disetujui = u_row[1] or 0
    umkm_pending = u_row[2] or 0

    cursor.execute("SELECT COUNT(*), COALESCE(SUM(CASE WHEN status='Disetujui' OR status='disetujui' OR status='aktif' THEN 1 ELSE 0 END), 0) FROM wisata")
    w_row = cursor.fetchone() or (0, 0)
    total_wisata = w_row[0] or 0
    wisata_aktif = w_row[1] or 0

    cursor.execute("SELECT COUNT(*), COALESCE(SUM(jumlah_unduh), 0), COALESCE(SUM(jumlah_baca), 0) FROM buku_publikasi")
    pub_row = cursor.fetchone() or (0, 0, 0)
    total_publikasi = pub_row[0] or 0
    publikasi_unduh = pub_row[1] or 0
    publikasi_baca = pub_row[2] or 0

    cursor.execute("SELECT COUNT(*) FROM perangkat_desa")
    total_perangkat = cursor.fetchone()[0] or 0

    # 6. Pembangunan & Realisasi Fisik
    cursor.execute("""
        SELECT 
            COUNT(*),
            COALESCE(SUM(anggaran), 0),
            COALESCE(SUM(CASE WHEN status_progres = 'Selesai' THEN anggaran ELSE (anggaran * progres_persen / 100.0) END), 0),
            COALESCE(SUM(CASE WHEN status_progres = 'Selesai' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN status_progres = 'Sedang Dikerjakan' OR status_progres = 'Sedang Berjalan' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN status_progres = 'Rencana' THEN 1 ELSE 0 END), 0),
            COALESCE(AVG(progres_persen), 0)
        FROM pembangunan_desa
    """)
    pb_row = cursor.fetchone() or (0, 0, 0, 0, 0, 0, 0)
    pembangunan_total = pb_row[0] or 0
    pembangunan_anggaran = pb_row[1] or 0
    pembangunan_realisasi = pb_row[2] or 0
    pembangunan_selesai = pb_row[3] or 0
    pembangunan_berjalan = pb_row[4] or 0
    pembangunan_rencana = pb_row[5] or 0
    pembangunan_avg_progres = round(pb_row[6], 1) if pembangunan_total > 0 else 0

    # 7. Media Interaktif & Trafik
    cursor.execute("SELECT COUNT(*) FROM running_texts WHERE is_active = 1")
    rt_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM banner_slider WHERE is_active = 1")
    slider_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM popup_informasi WHERE status = 'aktif'")
    popup_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT total_hits FROM visitor_totals WHERE id = 1")
    v_row = cursor.fetchone()
    total_hits = v_row[0] if v_row else 28933

    # 8. Kependudukan (Statistik Penduduk 2026 atau data terbaru)
    cursor.execute("SELECT * FROM statistik WHERE total_penduduk > 0 ORDER BY tahun DESC LIMIT 1")
    stat_row = cursor.fetchone()
    if not stat_row:
        cursor.execute("SELECT * FROM statistik ORDER BY tahun DESC LIMIT 1")
        stat_row = cursor.fetchone()
    stat_penduduk = dict(stat_row or {})

    cursor.execute("SELECT COUNT(*) FROM statistik_sls WHERE tahun = ?", (stat_penduduk.get('tahun', 2026),))
    total_sls = cursor.fetchone()[0] or 26

    # 9. Stunting, Gizi Buruk, Anak Yatim (tahun aktif)
    tahun_stat = stat_penduduk.get('tahun', 2026)
    cursor.execute("SELECT SUM(anak_stunting), SUM(jumlah_anak_balita) FROM statistik_stunting WHERE tahun = ?", (tahun_stat,))
    stunt_res = cursor.fetchone()
    total_stunting = (stunt_res[0] if stunt_res and stunt_res[0] is not None else 0)
    total_balita = (stunt_res[1] if stunt_res and stunt_res[1] is not None else 0)

    cursor.execute("SELECT SUM(anak_gizi_buruk) FROM statistik_gizi_buruk WHERE tahun = ?", (tahun_stat,))
    gizi_res = cursor.fetchone()
    total_gizi_buruk = (gizi_res[0] if gizi_res and gizi_res[0] is not None else 0)

    cursor.execute("SELECT SUM(anak_yatim), SUM(anak_piatu), SUM(yatim_piatu) FROM statistik_anak WHERE tahun = ?", (tahun_stat,))
    anak_res = cursor.fetchone()
    anak_yatim = (anak_res[0] if anak_res and anak_res[0] is not None else 0)
    anak_piatu = (anak_res[1] if anak_res and anak_res[1] is not None else 0)
    anak_yp = (anak_res[2] if anak_res and anak_res[2] is not None else 0)
    total_yatim_semua = anak_yatim + anak_piatu + anak_yp

    # 10. APBDes
    cursor.execute("SELECT * FROM apbdes WHERE id = 1")
    apbdes_row = cursor.fetchone()
    apbdes_data = dict(apbdes_row or {})

    # 11. Recent Items
    cursor.execute("SELECT * FROM layanan_surat ORDER BY id DESC LIMIT 5")
    recent_surat = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM pengaduan ORDER BY id DESC LIMIT 5")
    recent_aduan = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT id, nama_kegiatan, kategori, dusun, anggaran, progres_persen, status_progres FROM pembangunan_desa ORDER BY id DESC LIMIT 4")
    recent_pembangunan = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT id, judul, kategori, tipe, status, gambar, created_at FROM galeri ORDER BY id DESC LIMIT 4")
    recent_galeri = [dict(row) for row in cursor.fetchall()]

    # 12. Activity logs & Backups (untuk Super Admin widget)
    cursor.execute("SELECT * FROM activity_logs ORDER BY id DESC LIMIT 5")
    recent_logs = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0] or 0

    conn.close()

    backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
    total_backups = len([f for f in os.listdir(backup_dir) if os.path.isfile(os.path.join(backup_dir, f))]) if os.path.exists(backup_dir) else 0

    metrics = {
        'total_surat': total_surat,
        'surat_pending': surat_pending,
        'surat_proses': surat_proses,
        'surat_selesai': surat_selesai,
        'total_aduan': total_aduan,
        'aduan_pending': aduan_pending,
        'aduan_khusus': aduan_khusus,
        'aduan_selesai': aduan_selesai,
        'total_feedback': total_feedback,
        'avg_feedback_rating': avg_feedback_rating,
        'puas_feedback_pct': puas_feedback_pct,
        'total_berita': total_berita,
        'total_galeri': total_galeri,
        'total_prestasi': total_prestasi,
        'pending_galeri': pending_galeri,
        'total_umkm': total_umkm,
        'umkm_disetujui': umkm_disetujui,
        'umkm_pending': umkm_pending,
        'total_wisata': total_wisata,
        'wisata_aktif': wisata_aktif,
        'total_publikasi': total_publikasi,
        'publikasi_unduh': publikasi_unduh,
        'publikasi_baca': publikasi_baca,
        'total_perangkat': total_perangkat,
        'pembangunan_total': pembangunan_total,
        'pembangunan_anggaran': pembangunan_anggaran,
        'pembangunan_realisasi': pembangunan_realisasi,
        'pembangunan_selesai': pembangunan_selesai,
        'pembangunan_berjalan': pembangunan_berjalan,
        'pembangunan_rencana': pembangunan_rencana,
        'pembangunan_avg_progres': pembangunan_avg_progres,
        'rt_count': rt_count,
        'slider_count': slider_count,
        'popup_count': popup_count,
        'total_hits': total_hits,
        'stat_penduduk': stat_penduduk,
        'total_sls': total_sls,
        'total_stunting': total_stunting,
        'total_balita': total_balita,
        'total_gizi_buruk': total_gizi_buruk,
        'total_yatim_semua': total_yatim_semua,
        'anak_yatim': anak_yatim,
        'anak_piatu': anak_piatu,
        'anak_yp': anak_yp,
        'apbdes_data': apbdes_data,
        'total_users': total_users,
        'total_backups': total_backups
    }

    return render_template(
        'admin/dashboard.html',
        metrics=metrics,
        recent_surat=recent_surat,
        recent_aduan=recent_aduan,
        recent_pembangunan=recent_pembangunan,
        recent_galeri=recent_galeri,
        recent_logs=recent_logs
    )

# --- 1. MANAJEMEN LAYANAN SURAT ---
@app.route('/admin/surat')
@login_required
def admin_surat():
    status_filter = request.args.get('status')
    conn = get_db()
    cursor = conn.cursor()

    if status_filter:
        cursor.execute("SELECT * FROM layanan_surat WHERE status = ? ORDER BY id DESC", (status_filter,))
    else:
        cursor.execute("SELECT * FROM layanan_surat ORDER BY id DESC")
    
    surat_list = [dict(row) for row in cursor.fetchall()]

    # Status Maintenance Layanan Surat
    cursor.execute("SELECT status_maintenance_surat, pesan_maintenance_surat FROM profil_desa WHERE id = 1")
    row_profil = cursor.fetchone()
    status_maintenance = row_profil['status_maintenance_surat'] if (row_profil and 'status_maintenance_surat' in row_profil.keys()) else 1
    pesan_maintenance = (row_profil['pesan_maintenance_surat'] if (row_profil and 'pesan_maintenance_surat' in row_profil.keys()) else None) or 'Layanan Sedang Maintenace. Mohon maaf atas ketidaknyamananya !!!'

    conn.close()
    return render_template(
        'admin/surat.html',
        surat_list=surat_list,
        active_status=status_filter,
        status_maintenance=status_maintenance,
        pesan_maintenance=pesan_maintenance
    )

@app.route('/admin/surat/toggle-maintenance', methods=['POST'])
@login_required
def admin_toggle_maintenance_surat():
    action = request.form.get('action')  # 'lock', 'unlock', or 'update_message'
    pesan = request.form.get('pesan_maintenance_surat', '').strip()

    conn = get_db()
    cursor = conn.cursor()

    if action == 'update_message':
        if pesan:
            cursor.execute("UPDATE profil_desa SET pesan_maintenance_surat = ? WHERE id = 1", (pesan,))
            conn.commit()
            record_activity_log(
                'UPDATE_PESAN_MAINTENANCE_SURAT',
                f"Mengubah kalimat permohonan maaf pemeliharaan layanan surat: {pesan}",
                username=session.get('username')
            )
            flash('Kalimat permohonan maaf pemeliharaan layanan surat berhasil disimpan & diperbarui!', 'success')
        else:
            flash('Pesan permohonan maaf tidak boleh kosong.', 'danger')
        conn.close()
        return redirect(url_for('admin_surat'))

    new_status = 1 if action == 'lock' else 0
    if pesan:
        cursor.execute("UPDATE profil_desa SET status_maintenance_surat = ?, pesan_maintenance_surat = ? WHERE id = 1", (new_status, pesan))
    else:
        cursor.execute("UPDATE profil_desa SET status_maintenance_surat = ? WHERE id = 1", (new_status,))
    conn.commit()
    conn.close()

    if new_status == 1:
        record_activity_log('LOCK_LAYANAN_SURAT', f"Mengunci layanan surat dengan pesan: {pesan}", username=session.get('username'))
        flash('Layanan surat mandiri BERHASIL DIKUNCI (Mode Maintenance Aktif). Warga di frontend tidak dapat membuat surat sementara waktu.', 'warning')
    else:
        record_activity_log('UNLOCK_LAYANAN_SURAT', "Membuka kembali kunci layanan surat mandiri", username=session.get('username'))
        flash('Layanan surat mandiri BERHASIL DIBUKA KEMBALI (Mode Normal Aktif). Warga dapat mengajukan permohonan surat secara daring.', 'success')
    return redirect(url_for('admin_surat'))

@app.route('/admin/surat/<int:id>/update-status', methods=['POST'])
@login_required
def admin_update_surat_status(id):
    status = request.form.get('status')
    catatan = request.form.get('catatan_admin', '')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE layanan_surat SET status = ?, catatan_admin = ? WHERE id = ?", (status, catatan, id))
    conn.commit()
    conn.close()

    flash(f'Status permohonan surat berhasil diubah menjadi: {status}.', 'success')
    return redirect(url_for('admin_surat'))

@app.route('/admin/surat/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_surat(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM layanan_surat WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Data permohonan surat berhasil dihapus.', 'info')
    return redirect(url_for('admin_surat'))

# --- 2. MANAJEMEN PENGADUAN & ASPIRASI WARGA ---
@app.route('/admin/pengaduan')
@login_required
def admin_pengaduan():
    status_filter = request.args.get('status', '').strip()
    kategori_filter = request.args.get('kategori', '').strip()
    search_query = request.args.get('q', '').strip()

    conn = get_db()
    cursor = conn.cursor()

    # Query daftar aduan dengan filter
    query = "SELECT * FROM pengaduan WHERE 1=1"
    params = []

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    if kategori_filter:
        query += " AND kategori = ?"
        params.append(kategori_filter)
    if search_query:
        query += " AND (no_tiket LIKE ? OR nama LIKE ? OR pesan LIKE ? OR kontak LIKE ?)"
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term, like_term, like_term])

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    aduan_list = [dict(row) for row in cursor.fetchall()]

    # Summary KPI
    cursor.execute("SELECT COUNT(*) FROM pengaduan")
    total_aduan = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM pengaduan WHERE status = 'Belum Ditanggapi'")
    total_belum = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM pengaduan WHERE status = 'Perlu Perlakuan Khusus'")
    total_khusus = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM pengaduan WHERE status = 'Sudah Diselesaikan'")
    total_selesai = cursor.fetchone()[0] or 0

    # Daftar kategori pengaduan
    cursor.execute("SELECT * FROM kategori_pengaduan ORDER BY urutan ASC, id ASC")
    kategori_list = [dict(row) for row in cursor.fetchall()]

    # Daftar Feedback Kepuasan Pengunjung
    cursor.execute("SELECT * FROM feedback_kepuasan ORDER BY id DESC")
    feedback_list = [dict(row) for row in cursor.fetchall()]

    # Summary Feedback
    cursor.execute("SELECT COUNT(*), AVG(rating) FROM feedback_kepuasan")
    fb_row = cursor.fetchone()
    total_feedback = fb_row[0] or 0
    avg_rating = round(fb_row[1] or 0.0, 1)

    # Distribusi Rating Feedback
    cursor.execute("SELECT rating, COUNT(*) FROM feedback_kepuasan GROUP BY rating")
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r_val, count_val in cursor.fetchall():
        if r_val in rating_counts:
            rating_counts[r_val] = count_val

    rating_pct = {}
    for r_k in range(1, 6):
        rating_pct[r_k] = round((rating_counts[r_k] / total_feedback * 100), 1) if total_feedback > 0 else 0

    # Rekap Aspek Paling Sering Dipilih
    cursor.execute("SELECT aspek_peningkatan FROM feedback_kepuasan WHERE aspek_peningkatan IS NOT NULL AND aspek_peningkatan != ''")
    aspek_counter = {}
    for r_asp in cursor.fetchall():
        for item_asp in r_asp[0].split(','):
            c_item = item_asp.strip()
            if c_item:
                aspek_counter[c_item] = aspek_counter.get(c_item, 0) + 1
    top_aspek = sorted(aspek_counter.items(), key=lambda x: x[1], reverse=True)

    active_tab = request.args.get('tab', 'aduan').strip()

    conn.close()

    summary = {
        'total': total_aduan,
        'belum_ditanggapi': total_belum,
        'perlu_khusus': total_khusus,
        'sudah_selesai': total_selesai,
        'total_feedback': total_feedback,
        'avg_rating': avg_rating,
        'rating_counts': rating_counts,
        'rating_pct': rating_pct,
        'top_aspek': top_aspek
    }

    return render_template(
        'admin/pengaduan.html',
        aduan_list=aduan_list,
        kategori_list=kategori_list,
        feedback_list=feedback_list,
        summary=summary,
        status_filter=status_filter,
        kategori_filter=kategori_filter,
        search_query=search_query,
        active_tab=active_tab
    )

@app.route('/admin/pengaduan/<int:id>/tanggapi', methods=['POST'])
@login_required
def admin_tanggapi_pengaduan(id):
    status = request.form.get('status', 'Belum Ditanggapi').strip()
    uraian = (request.form.get('uraian_tindak_lanjut') or request.form.get('tanggapan_admin') or '').strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE pengaduan 
    SET status = ?, tanggapan_admin = ?, uraian_tindak_lanjut = ? 
    WHERE id = ?
    ''', (status, uraian, uraian, id))
    conn.commit()
    conn.close()

    flash('Status aduan dan uraian tindak lanjut penanganan berhasil diperbarui.', 'success')
    return redirect(url_for('admin_pengaduan'))

@app.route('/admin/pengaduan/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_pengaduan(id):
    conn = get_db()
    cursor = conn.cursor()
    # Hapus file lampiran jika ada
    cursor.execute("SELECT lampiran FROM pengaduan WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row and row['lampiran'] and os.path.exists(row['lampiran']):
        try:
            os.remove(row['lampiran'])
        except Exception:
            pass

    cursor.execute("DELETE FROM pengaduan WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Pengaduan berhasil dihapus.', 'info')
    return redirect(url_for('admin_pengaduan'))

# --- CRUD KATEGORI PENGADUAN ---
@app.route('/admin/pengaduan/kategori/tambah', methods=['POST'])
@login_required
def admin_tambah_kategori_pengaduan():
    nama = request.form.get('nama', '').strip()
    keterangan = request.form.get('keterangan', '').strip()
    urutan = request.form.get('urutan', type=int) or 0

    if not nama:
        flash('Nama kategori pengaduan tidak boleh kosong.', 'danger')
        return redirect(url_for('admin_pengaduan'))

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO kategori_pengaduan (nama, keterangan, urutan) VALUES (?, ?, ?)", (nama, keterangan, urutan))
        conn.commit()
        flash(f'Kategori "{nama}" berhasil ditambahkan.', 'success')
    except sqlite3.IntegrityError:
        flash(f'Kategori "{nama}" sudah ada dalam daftar.', 'warning')
    finally:
        conn.close()

    return redirect(url_for('admin_pengaduan'))

@app.route('/admin/pengaduan/kategori/<int:id>/edit', methods=['POST'])
@login_required
def admin_edit_kategori_pengaduan(id):
    nama = request.form.get('nama', '').strip()
    keterangan = request.form.get('keterangan', '').strip()
    urutan = request.form.get('urutan', type=int) or 0

    if not nama:
        flash('Nama kategori pengaduan tidak boleh kosong.', 'danger')
        return redirect(url_for('admin_pengaduan'))

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nama FROM kategori_pengaduan WHERE id = ?", (id,))
        old_row = cursor.fetchone()
        old_name = old_row['nama'] if old_row else None

        cursor.execute("UPDATE kategori_pengaduan SET nama = ?, keterangan = ?, urutan = ? WHERE id = ?", (nama, keterangan, urutan, id))
        if old_name and old_name != nama:
            cursor.execute("UPDATE pengaduan SET kategori = ? WHERE kategori = ?", (nama, old_name))
        conn.commit()
        flash(f'Kategori "{nama}" berhasil diperbarui.', 'success')
    except sqlite3.IntegrityError:
        flash(f'Nama kategori "{nama}" sudah digunakan kategori lain.', 'warning')
    finally:
        conn.close()

    return redirect(url_for('admin_pengaduan'))

@app.route('/admin/pengaduan/kategori/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_kategori_pengaduan(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nama FROM kategori_pengaduan WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        nama = row['nama']
        cursor.execute("DELETE FROM kategori_pengaduan WHERE id = ?", (id,))
        conn.commit()
        flash(f'Kategori "{nama}" berhasil dihapus dari daftar.', 'info')
    conn.close()
    return redirect(url_for('admin_pengaduan'))

# --- PENGATURAN & KELOLA FEEDBACK KEPUASAN PENGUNJUNG ---
@app.route('/admin/pengaduan/feedback/settings', methods=['POST'])
@login_required
def admin_update_feedback_settings():
    feedback_judul = request.form.get('feedback_judul', 'Feedback').strip()
    feedback_pertanyaan = request.form.get('feedback_pertanyaan', 'Seberapa puas Anda dengan website kami?').strip()
    feedback_opsi_pekerjaan = request.form.get('feedback_opsi_pekerjaan', '').strip()
    feedback_opsi_aspek = request.form.get('feedback_opsi_aspek', '').strip()
    feedback_placeholder_saran = request.form.get('feedback_placeholder_saran', '').strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE profil_desa SET
        feedback_judul = ?,
        feedback_pertanyaan = ?,
        feedback_opsi_pekerjaan = ?,
        feedback_opsi_aspek = ?,
        feedback_placeholder_saran = ?
    WHERE id = 1
    ''', (feedback_judul, feedback_pertanyaan, feedback_opsi_pekerjaan, feedback_opsi_aspek, feedback_placeholder_saran))
    conn.commit()
    conn.close()

    flash('Pengaturan variabel formulir feedback kepuasan berhasil disimpan.', 'success')
    return redirect(url_for('admin_pengaduan', tab='feedback'))

@app.route('/admin/pengaduan/feedback/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_feedback(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feedback_kepuasan WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Data masukan feedback berhasil dihapus.', 'info')
    return redirect(url_for('admin_pengaduan', tab='feedback'))

# --- 3. MANAJEMEN BERITA & GALERI DOKUMENTASI DESA ---
@app.route('/admin/berita')
@login_required
def admin_berita():
    active_view = request.args.get('view', 'berita')
    active_tab = request.args.get('tab', 'tayang')

    conn = get_db()
    cursor = conn.cursor()

    # 1. Sudah Approve & Tayang di Web Frontend
    cursor.execute("SELECT * FROM berita WHERE status = 'Tayang' OR status IS NULL ORDER BY id DESC")
    tayang_list = [dict(row) for row in cursor.fetchall()]

    # 2. Sudah Approve tapi Belum Tayang
    cursor.execute("SELECT * FROM berita WHERE status = 'Disetujui' ORDER BY id DESC")
    disetujui_list = [dict(row) for row in cursor.fetchall()]

    # 3. Masih Draft / Konsep
    cursor.execute("SELECT * FROM berita WHERE status = 'Draft' ORDER BY id DESC")
    draft_list = [dict(row) for row in cursor.fetchall()]

    # 4. Batal Tayang karena Masalah Redaksi
    cursor.execute("SELECT * FROM berita WHERE status = 'Batal Tayang' ORDER BY id DESC")
    batal_list = [dict(row) for row in cursor.fetchall()]

    # Semua Berita
    cursor.execute("SELECT * FROM berita ORDER BY id DESC")
    semua_list = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM kategori_berita ORDER BY urutan ASC, id ASC")
    kategori_list = [dict(row) for row in cursor.fetchall()]

    # --- DATA GALERI FOTO DOKUMENTASI KEGIATAN DESA ---
    cursor.execute("SELECT * FROM galeri WHERE tipe = 'kegiatan' AND status = 'Tayang' ORDER BY tanggal DESC, id DESC")
    galeri_tayang = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM galeri WHERE tipe = 'kegiatan' AND status = 'Menunggu Persetujuan' ORDER BY id DESC")
    galeri_pengajuan = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM galeri WHERE tipe = 'kegiatan' ORDER BY id DESC")
    galeri_semua = [dict(row) for row in cursor.fetchall()]

    # --- DATA SUB-GALERI PIAGAM & PENGHARGAAN PRESTASI PEMERINTAH DESA ---
    cursor.execute("SELECT * FROM galeri WHERE tipe = 'penghargaan' ORDER BY tahun_penghargaan DESC, tanggal DESC, id DESC")
    penghargaan_list = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
    row_profil = cursor.fetchone()
    profil = dict(row_profil) if row_profil else {}

    pending_galeri_count = len(galeri_pengajuan)
    conn.close()

    return render_template('admin/berita.html',
                           profil=profil,
                           active_view=active_view,
                           active_tab=active_tab,
                           tayang_list=tayang_list,
                           disetujui_list=disetujui_list,
                           draft_list=draft_list,
                           batal_list=batal_list,
                           semua_list=semua_list,
                           kategori_list=kategori_list,
                           galeri_tayang=galeri_tayang,
                           galeri_pengajuan=galeri_pengajuan,
                           galeri_semua=galeri_semua,
                           penghargaan_list=penghargaan_list,
                           pending_galeri_count=pending_galeri_count)

@app.route('/admin/galeri')
@login_required
def admin_galeri():
    view = request.args.get('view', 'galeri')
    tab = request.args.get('tab', 'tayang')
    return redirect(url_for('admin_berita', view=view, tab=tab))

def format_tanggal_indo(tgl_str):
    if not tgl_str:
        return datetime.now().strftime('%d %B %Y')
    bulan_indo = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
        5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
        9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }
    tgl_str = str(tgl_str).strip()
    try:
        parts = tgl_str.split('-')
        if len(parts) == 3 and len(parts[0]) == 4:
            thn = int(parts[0])
            bln = int(parts[1])
            tgl = int(parts[2])
            return f"{tgl} {bulan_indo.get(bln, '')} {thn}"
    except Exception:
        pass
    return tgl_str

@app.route('/admin/berita/tambah', methods=['POST'])
@login_required
def admin_tambah_berita():
    judul = request.form.get('judul')
    kategori = request.form.get('kategori')
    penulis = request.form.get('penulis') or session.get('nama', 'Admin')
    tanggal = format_tanggal_indo(request.form.get('tanggal'))
    isi = request.form.get('isi') or ''
    ringkasan = request.form.get('ringkasan') or (isi[:150] + '...' if len(isi) > 150 else isi)
    status = request.form.get('status') or 'Tayang'
    catatan_redaksi = request.form.get('catatan_redaksi') or ''

    gambar = request.form.get('gambar') or 'static/images/pantai_kersik.jpg'
    if 'gambar_file' in request.files:
        file = request.files['gambar_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                filename = secure_filename(f"berita_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                gambar = f"static/images/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO berita (judul, kategori, penulis, tanggal, gambar, ringkasan, isi, status, catatan_redaksi)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (judul, kategori, penulis, tanggal, gambar, ringkasan, isi, status, catatan_redaksi))
    conn.commit()
    conn.close()

    flash(f'Berita baru berhasil disimpan dengan status "{status}".', 'success')
    return redirect(url_for('admin_berita'))

@app.route('/admin/berita/<int:id>/edit', methods=['POST'])
@login_required
def admin_edit_berita(id):
    judul = request.form.get('judul')
    kategori = request.form.get('kategori')
    penulis = request.form.get('penulis')
    tanggal = format_tanggal_indo(request.form.get('tanggal'))
    isi = request.form.get('isi') or ''
    ringkasan = request.form.get('ringkasan') or (isi[:150] + '...' if len(isi) > 150 else isi)
    status = request.form.get('status') or 'Tayang'
    catatan_redaksi = request.form.get('catatan_redaksi') or ''

    gambar = request.form.get('gambar_lama') or request.form.get('gambar')
    if 'gambar_file' in request.files:
        file = request.files['gambar_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                filename = secure_filename(f"berita_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                gambar = f"static/images/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    if not gambar:
        cursor.execute("SELECT gambar FROM berita WHERE id = ?", (id,))
        row = cursor.fetchone()
        gambar = row['gambar'] if row and row['gambar'] else 'static/images/pantai_kersik.jpg'

    cursor.execute('''
    UPDATE berita SET judul=?, kategori=?, penulis=?, tanggal=?, gambar=?, ringkasan=?, isi=?, status=?, catatan_redaksi=?
    WHERE id=?
    ''', (judul, kategori, penulis, tanggal, gambar, ringkasan, isi, status, catatan_redaksi, id))
    conn.commit()
    conn.close()

    flash(f'Artikel berita berhasil diperbarui dengan status "{status}".', 'success')
    return redirect(url_for('admin_berita'))

@app.route('/admin/berita/<int:id>/status', methods=['POST'])
@login_required
def admin_ubah_status_berita(id):
    status_baru = request.form.get('status')
    catatan_redaksi = request.form.get('catatan_redaksi') or ''

    valid_statuses = ['Tayang', 'Disetujui', 'Draft', 'Batal Tayang']
    if status_baru not in valid_statuses:
        flash('Status publikasi tidak valid.', 'danger')
        return redirect(url_for('admin_berita'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE berita SET status = ?, catatan_redaksi = ? WHERE id = ?", (status_baru, catatan_redaksi, id))
    conn.commit()
    conn.close()

    pesan_map = {
        'Tayang': 'Artikel berhasil disetujui dan telah tayang di website desa!',
        'Disetujui': 'Status artikel diubah menjadi "Disetujui (Belum Tayang)".',
        'Draft': 'Artikel berhasil dipindahkan ke Draf (Konsep).',
        'Batal Tayang': 'Artikel berhasil dibatalkan tayang karena masalah redaksi.'
    }
    flash(pesan_map.get(status_baru, 'Status artikel berhasil diperbarui.'), 'success')
    return redirect(url_for('admin_berita'))

@app.route('/admin/berita/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_berita(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM berita WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Berita berhasil dihapus.', 'info')
    return redirect(url_for('admin_berita'))

# --- MANAJEMEN KATEGORI BERITA ---
@app.route('/admin/berita/kategori/tambah', methods=['POST'])
@login_required
def admin_tambah_kategori_berita():
    nama = request.form.get('nama', '').strip()
    if not nama:
        flash('Nama kategori tidak boleh kosong.', 'danger')
        return redirect(url_for('admin_berita'))

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(urutan) FROM kategori_berita")
        max_u = cursor.fetchone()[0] or 0
        cursor.execute("INSERT INTO kategori_berita (nama, urutan) VALUES (?, ?)", (nama, max_u + 1))
        conn.commit()
        flash(f'Kategori "{nama}" berhasil ditambahkan.', 'success')
    except sqlite3.IntegrityError:
        flash(f'Kategori "{nama}" sudah ada sebelumnya.', 'warning')
    finally:
        conn.close()
    return redirect(url_for('admin_berita'))

@app.route('/admin/berita/kategori/<int:id>/edit', methods=['POST'])
@login_required
def admin_edit_kategori_berita(id):
    nama_baru = request.form.get('nama', '').strip()
    if not nama_baru:
        flash('Nama kategori tidak boleh kosong.', 'danger')
        return redirect(url_for('admin_berita'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nama FROM kategori_berita WHERE id = ?", (id,))
    old_row = cursor.fetchone()
    if old_row:
        old_nama = old_row['nama']
        try:
            cursor.execute("UPDATE kategori_berita SET nama = ? WHERE id = ?", (nama_baru, id))
            # Sinkronkan juga berita yang memiliki kategori lama ini
            cursor.execute("UPDATE berita SET kategori = ? WHERE kategori = ?", (nama_baru, old_nama))
            conn.commit()
            flash(f'Kategori berhasil diubah menjadi "{nama_baru}" dan disinkronkan ke artikel terkait.', 'success')
        except sqlite3.IntegrityError:
            flash(f'Kategori dengan nama "{nama_baru}" sudah ada.', 'warning')
    conn.close()
    return redirect(url_for('admin_berita'))

@app.route('/admin/berita/kategori/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_kategori_berita(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kategori_berita WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Kategori berita berhasil dihapus.', 'info')
    return redirect(url_for('admin_berita'))

@app.route('/api/admin/berita/kategori/tambah', methods=['POST'])
@login_required
def api_tambah_kategori_berita():
    data = request.get_json(silent=True) or request.form
    nama = data.get('nama', '').strip()
    if not nama:
        return jsonify({'success': False, 'message': 'Nama kategori tidak boleh kosong.'}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(urutan) FROM kategori_berita")
        max_u = cursor.fetchone()[0] or 0
        cursor.execute("INSERT INTO kategori_berita (nama, urutan) VALUES (?, ?)", (nama, max_u + 1))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': new_id, 'nama': nama, 'message': f'Kategori "{nama}" berhasil ditambahkan!'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': f'Kategori "{nama}" sudah ada.'}), 400

# ==========================================
# MANAJEMEN GALERI FOTO & SUB-GALERI PIAGAM PENGHARGAAN
# ==========================================
@app.route('/admin/galeri/tambah', methods=['POST'])
@login_required
def admin_tambah_galeri():
    judul = request.form.get('judul', '').strip()
    kategori = request.form.get('kategori', 'Kegiatan Pemdes').strip()
    tipe = request.form.get('tipe', 'kegiatan').strip()
    if 'penghargaan' in kategori.lower() or tipe == 'penghargaan':
        tipe = 'penghargaan'
    else:
        tipe = 'kegiatan'

    deskripsi = request.form.get('deskripsi', '').strip()
    tanggal = request.form.get('tanggal') or datetime.now().strftime('%Y-%m-%d')
    pengunggah = request.form.get('pengunggah') or 'Pemerintah Desa'
    kontak_pengunggah = request.form.get('kontak_pengunggah', '-')
    status = request.form.get('status', 'Tayang')
    pemberi_penghargaan = request.form.get('pemberi_penghargaan', '').strip() if tipe == 'penghargaan' else None
    tahun_penghargaan = request.form.get('tahun_penghargaan', '').strip() if tipe == 'penghargaan' else None

    if not judul:
        flash('Judul foto / piagam wajib diisi.', 'danger')
        return redirect(url_for('admin_berita', view='penghargaan' if tipe == 'penghargaan' else 'galeri'))

    gambar = request.form.get('gambar_url', '').strip()
    if 'gambar_file' in request.files:
        file = request.files['gambar_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                prefix = 'piagam' if tipe == 'penghargaan' else 'galeri'
                filename = secure_filename(f"{prefix}_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                gambar = f"static/images/uploads/{filename}"

    if not gambar:
        gambar = "static/images/banner1.png"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO galeri (judul, deskripsi, kategori, tipe, gambar, tanggal, pengunggah, kontak_pengunggah, status, pemberi_penghargaan, tahun_penghargaan)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (judul, deskripsi, kategori, tipe, gambar, tanggal, pengunggah, kontak_pengunggah, status, pemberi_penghargaan, tahun_penghargaan))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    record_activity_log(
        action='TAMBAH_GALERI',
        details=f'Menambahkan {"piagam penghargaan" if tipe == "penghargaan" else "foto dokumentasi kegiatan"} ID {new_id}: "{judul[:40]}"',
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )

    item_name = "Piagam penghargaan" if tipe == "penghargaan" else "Foto dokumentasi kegiatan"
    flash(f'{item_name} berhasil ditambahkan dan berstatus "{status}".', 'success')
    return redirect(url_for('admin_berita', view='penghargaan' if tipe == 'penghargaan' else 'galeri', tab='tayang'))


@app.route('/admin/galeri/<int:id>/edit', methods=['POST'])
@login_required
def admin_edit_galeri(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM galeri WHERE id = ?", (id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        flash('Data galeri tidak ditemukan.', 'danger')
        return redirect(url_for('admin_berita', view='galeri'))

    item = dict(row)
    judul = request.form.get('judul', item['judul']).strip()
    kategori = request.form.get('kategori', item['kategori']).strip()
    tipe = request.form.get('tipe', item['tipe']).strip()
    if 'penghargaan' in kategori.lower() or tipe == 'penghargaan':
        tipe = 'penghargaan'
    else:
        tipe = 'kegiatan'

    deskripsi = request.form.get('deskripsi', item['deskripsi']).strip()
    tanggal = request.form.get('tanggal', item['tanggal'])
    pengunggah = request.form.get('pengunggah', item['pengunggah'])
    kontak_pengunggah = request.form.get('kontak_pengunggah', item['kontak_pengunggah'])
    status = request.form.get('status', item['status'])
    pemberi_penghargaan = request.form.get('pemberi_penghargaan', item['pemberi_penghargaan']) if tipe == 'penghargaan' else None
    tahun_penghargaan = request.form.get('tahun_penghargaan', item['tahun_penghargaan']) if tipe == 'penghargaan' else None

    gambar = request.form.get('gambar_url', '').strip() or item['gambar']
    if 'gambar_file' in request.files:
        file = request.files['gambar_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                prefix = 'piagam' if tipe == 'penghargaan' else 'galeri'
                filename = secure_filename(f"{prefix}_{id}_{int(time.time())}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                gambar = f"static/images/uploads/{filename}"

    cursor.execute('''
    UPDATE galeri 
    SET judul = ?, deskripsi = ?, kategori = ?, tipe = ?, gambar = ?, tanggal = ?, 
        pengunggah = ?, kontak_pengunggah = ?, status = ?, pemberi_penghargaan = ?, tahun_penghargaan = ?
    WHERE id = ?
    ''', (judul, deskripsi, kategori, tipe, gambar, tanggal, pengunggah, kontak_pengunggah, status, pemberi_penghargaan, tahun_penghargaan, id))
    conn.commit()
    conn.close()

    record_activity_log(
        action='EDIT_GALERI',
        details=f'Mengedit {"piagam" if tipe == "penghargaan" else "foto galeri"} ID {id}: "{judul[:40]}"',
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )

    flash('Perubahan data galeri berhasil disimpan.', 'success')
    return redirect(url_for('admin_berita', view='penghargaan' if tipe == 'penghargaan' else 'galeri'))


@app.route('/admin/galeri/<int:id>/approve', methods=['POST'])
@login_required
def admin_approve_galeri(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT judul, pengunggah FROM galeri WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE galeri SET status = 'Tayang' WHERE id = ?", (id,))
        conn.commit()
        record_activity_log(
            action='APPROVE_GALERI',
            details=f'Menyetujui pengajuan foto galeri warga ID {id}: "{row[0][:40]}" oleh {row[1]}',
            username=session.get('username'),
            user_id=session.get('user_id'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        flash(f'Foto dokumentasi "{row[0][:35]}" dari warga berhasil disetujui dan ditayangkan!', 'success')
    conn.close()
    return redirect(url_for('admin_berita', view='galeri', tab='tayang'))


@app.route('/admin/galeri/<int:id>/reject', methods=['POST'])
@login_required
def admin_reject_galeri(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT judul FROM galeri WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE galeri SET status = 'Ditolak' WHERE id = ?", (id,))
        conn.commit()
        record_activity_log(
            action='REJECT_GALERI',
            details=f'Menolak pengajuan foto galeri warga ID {id}: "{row[0][:40]}"',
            username=session.get('username'),
            user_id=session.get('user_id'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        flash(f'Pengajuan foto dokumentasi "{row[0][:35]}" telah ditolak.', 'info')
    conn.close()
    return redirect(url_for('admin_berita', view='galeri', tab='pengajuan'))


@app.route('/admin/galeri/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_galeri(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT judul, tipe FROM galeri WHERE id = ?", (id,))
    row = cursor.fetchone()
    tipe = 'kegiatan'
    if row:
        judul = row[0]
        tipe = row[1]
        cursor.execute("DELETE FROM galeri WHERE id = ?", (id,))
        conn.commit()
        record_activity_log(
            action='HAPUS_GALERI',
            details=f'Menghapus {"piagam" if tipe == "penghargaan" else "foto galeri"} ID {id}: "{judul[:40]}"',
            username=session.get('username'),
            user_id=session.get('user_id'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        flash(f'Data "{judul[:35]}" berhasil dihapus.', 'info')
    conn.close()
    return redirect(url_for('admin_berita', view='penghargaan' if tipe == 'penghargaan' else 'galeri'))


# --- ENDPOINT FRONTEND: PENGAJUAN FOTO DOKUMENTASI DARI WARGA ---
@app.route('/galeri/ajukan', methods=['POST'])
def galeri_ajukan_warga():
    nama_pengunggah = (request.form.get('pengunggah') or request.form.get('nama_pengunggah', '')).strip()
    kontak_pengunggah = (request.form.get('kontak_pengunggah') or request.form.get('wa', '')).strip()
    judul = request.form.get('judul', '').strip()
    kategori = request.form.get('kategori', 'Kegiatan Warga').strip()
    tanggal = request.form.get('tanggal') or datetime.now().strftime('%Y-%m-%d')
    deskripsi = request.form.get('deskripsi', '').strip()

    if not nama_pengunggah or not judul:
        flash('Mohon lengkapi Nama Pengunggah dan Judul Kegiatan Dokumentasi.', 'danger')
        return redirect(url_for('index') + '#berita')

    gambar = None
    if 'gambar_file' in request.files:
        file = request.files['gambar_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                filename = secure_filename(f"warga_galeri_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                gambar = f"static/images/uploads/{filename}"

    if not gambar:
        flash('Silakan pilih berkas foto dokumentasi kegiatan yang ingin diajukan.', 'danger')
        return redirect(url_for('index') + '#berita')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO galeri (judul, deskripsi, kategori, tipe, gambar, tanggal, pengunggah, kontak_pengunggah, status)
    VALUES (?, ?, ?, 'kegiatan', ?, ?, ?, ?, 'Menunggu Persetujuan')
    ''', (judul, deskripsi, kategori, gambar, tanggal, nama_pengunggah, kontak_pengunggah))
    conn.commit()
    conn.close()

    flash('Terima kasih! Foto dokumentasi kegiatan warga berhasil diajukan dan sedang menunggu persetujuan (approval) admin desa sebelum tampil di galeri publik.', 'success')
    return redirect(url_for('index') + '#berita')

# --- 4. MANAJEMEN UMKM ---
@app.route('/admin/umkm')
@login_required
def admin_umkm():
    conn = get_db()
    cursor = conn.cursor()
    # Produk Aktif yang telah disetujui
    cursor.execute("SELECT * FROM umkm WHERE status = 'Disetujui' OR status IS NULL ORDER BY id DESC")
    umkm_list = [dict(row) for row in cursor.fetchall()]

    # Pengajuan Warga yang menunggu analisa & approval
    cursor.execute("SELECT * FROM umkm WHERE status = 'Menunggu Approval' ORDER BY id DESC")
    pengajuan_list = [dict(row) for row in cursor.fetchall()]

    # Riwayat Pengajuan Ditolak (jika ada)
    cursor.execute("SELECT * FROM umkm WHERE status = 'Ditolak' ORDER BY id DESC")
    ditolak_list = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template('admin/umkm.html', 
                           umkm_list=umkm_list, 
                           pengajuan_list=pengajuan_list,
                           ditolak_list=ditolak_list,
                           total_pending=len(pengajuan_list))

@app.route('/admin/umkm/tambah', methods=['POST'])
@login_required
def admin_tambah_umkm():
    nama = request.form.get('nama')
    produsen = request.form.get('produsen')
    harga = int(request.form.get('harga') or 0)
    satuan = request.form.get('satuan')
    deskripsi = request.form.get('deskripsi')
    kontak_wa = request.form.get('kontak_wa', '').replace('+', '').replace('-', '').strip()
    alamat = (request.form.get('lokasi') or request.form.get('alamat') or '').strip()
    lokasi = alamat

    try:
        latitude = float(request.form.get('latitude')) if request.form.get('latitude') else None
    except (ValueError, TypeError):
        latitude = None

    try:
        longitude = float(request.form.get('longitude')) if request.form.get('longitude') else None
    except (ValueError, TypeError):
        longitude = None

    # Upload Foto 1 (Foto Utama)
    gambar1 = request.form.get('gambar1') or request.form.get('gambar') or 'static/images/produk_terasi.jpg'
    if 'gambar_file1' in request.files:
        f = request.files['gambar_file1']
        if f and f.filename != '':
            ext = os.path.splitext(f.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                fn = secure_filename(f"umkm_1_{int(time.time())}_{random.randint(100,999)}{ext}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                gambar1 = f"static/images/uploads/{fn}"

    # Upload Foto 2 (Variasi / Samping)
    gambar2 = request.form.get('gambar2') or None
    if 'gambar_file2' in request.files:
        f = request.files['gambar_file2']
        if f and f.filename != '':
            ext = os.path.splitext(f.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                fn = secure_filename(f"umkm_2_{int(time.time())}_{random.randint(100,999)}{ext}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                gambar2 = f"static/images/uploads/{fn}"

    # Upload Foto 3 (Kemasan / Detail)
    gambar3 = request.form.get('gambar3') or None
    if 'gambar_file3' in request.files:
        f = request.files['gambar_file3']
        if f and f.filename != '':
            ext = os.path.splitext(f.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                fn = secure_filename(f"umkm_3_{int(time.time())}_{random.randint(100,999)}{ext}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                gambar3 = f"static/images/uploads/{fn}"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO umkm (nama, produsen, harga, satuan, deskripsi, kontak_wa, gambar, gambar2, gambar3, latitude, longitude, alamat, lokasi)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nama, produsen, harga, satuan, deskripsi, kontak_wa, gambar1, gambar2, gambar3, latitude, longitude, alamat, lokasi))
    conn.commit()
    conn.close()

    flash('Produk UMKM berhasil ditambahkan lengkap dengan alamat / lokasi tertulis, foto galeri, dan titik lokasi peta.', 'success')
    return redirect(url_for('admin_umkm'))

@app.route('/admin/umkm/<int:id>/edit', methods=['POST'])
@login_required
def admin_edit_umkm(id):
    nama = request.form.get('nama')
    produsen = request.form.get('produsen')
    harga = int(request.form.get('harga') or 0)
    satuan = request.form.get('satuan')
    deskripsi = request.form.get('deskripsi')
    kontak_wa = request.form.get('kontak_wa', '').replace('+', '').replace('-', '').strip()
    alamat = (request.form.get('lokasi') or request.form.get('alamat') or '').strip()
    lokasi = alamat

    try:
        latitude = float(request.form.get('latitude')) if request.form.get('latitude') else None
    except (ValueError, TypeError):
        latitude = None

    try:
        longitude = float(request.form.get('longitude')) if request.form.get('longitude') else None
    except (ValueError, TypeError):
        longitude = None

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT gambar, gambar2, gambar3, latitude, longitude FROM umkm WHERE id = ?", (id,))
    current = cursor.fetchone()
    old_g1 = current['gambar'] if current and current['gambar'] else 'static/images/produk_terasi.jpg'
    old_g2 = current['gambar2'] if current and current['gambar2'] else None
    old_g3 = current['gambar3'] if current and current['gambar3'] else None

    # Foto 1
    gambar1 = request.form.get('gambar_lama1') or request.form.get('gambar1') or old_g1
    if 'gambar_file1' in request.files:
        f = request.files['gambar_file1']
        if f and f.filename != '':
            ext = os.path.splitext(f.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                fn = secure_filename(f"umkm_1_{int(time.time())}_{random.randint(100,999)}{ext}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                gambar1 = f"static/images/uploads/{fn}"

    # Foto 2
    gambar2 = request.form.get('gambar_lama2') or request.form.get('gambar2') or old_g2
    if 'gambar_file2' in request.files:
        f = request.files['gambar_file2']
        if f and f.filename != '':
            ext = os.path.splitext(f.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                fn = secure_filename(f"umkm_2_{int(time.time())}_{random.randint(100,999)}{ext}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                gambar2 = f"static/images/uploads/{fn}"

    # Foto 3
    gambar3 = request.form.get('gambar_lama3') or request.form.get('gambar3') or old_g3
    if 'gambar_file3' in request.files:
        f = request.files['gambar_file3']
        if f and f.filename != '':
            ext = os.path.splitext(f.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                fn = secure_filename(f"umkm_3_{int(time.time())}_{random.randint(100,999)}{ext}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                gambar3 = f"static/images/uploads/{fn}"

    cursor.execute('''
    UPDATE umkm SET nama=?, produsen=?, harga=?, satuan=?, deskripsi=?, kontak_wa=?, gambar=?, gambar2=?, gambar3=?, latitude=?, longitude=?, alamat=?, lokasi=?
    WHERE id=?
    ''', (nama, produsen, harga, satuan, deskripsi, kontak_wa, gambar1, gambar2, gambar3, latitude, longitude, alamat, lokasi, id))
    conn.commit()
    conn.close()

    flash('Produk UMKM berhasil diperbarui dengan alamat tertulis, variasi foto lengkap, dan titik peta.', 'success')
    return redirect(url_for('admin_umkm'))

@app.route('/admin/umkm/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_umkm(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM umkm WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Produk UMKM berhasil dihapus.', 'info')
    return redirect(url_for('admin_umkm'))

@app.route('/admin/umkm/<int:id>/approve', methods=['POST'])
@login_required
def admin_approve_umkm(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE umkm SET status = 'Disetujui', catatan_admin = 'Telah diverifikasi dan disetujui tayang oleh admin.' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Produk UMKM warga berhasil disetujui (Approved) dan langsung tayang di katalog website desa!', 'success')
    return redirect(url_for('admin_umkm'))

@app.route('/admin/umkm/<int:id>/tolak', methods=['POST'])
@login_required
def admin_tolak_umkm(id):
    alasan = request.form.get('alasan') or 'Belum memenuhi kriteria produk desa.'
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE umkm SET status = 'Ditolak', catatan_admin = ? WHERE id = ?", (alasan, id))
    conn.commit()
    conn.close()
    flash('Pengajuan produk UMKM warga telah ditolak.', 'warning')
    return redirect(url_for('admin_umkm'))

# Endpoint Publik: Warga mengajukan produk UMKM dari Frontend
@app.route('/api/umkm/ajukan', methods=['POST'])
def api_ajukan_umkm():
    nama = request.form.get('nama')
    produsen = request.form.get('produsen')
    nik_pemilik = request.form.get('nik_pemilik')
    harga = int(request.form.get('harga') or 0)
    satuan = request.form.get('satuan')
    deskripsi = request.form.get('deskripsi')
    kontak_wa = request.form.get('kontak_wa', '').replace('+', '').replace('-', '').strip()
    alamat = (request.form.get('lokasi') or request.form.get('alamat') or '').strip()
    lokasi = alamat

    try:
        latitude = float(request.form.get('latitude')) if request.form.get('latitude') else None
    except (ValueError, TypeError):
        latitude = None

    try:
        longitude = float(request.form.get('longitude')) if request.form.get('longitude') else None
    except (ValueError, TypeError):
        longitude = None

    if not (nama and produsen and harga and satuan and deskripsi and kontak_wa):
        return jsonify({'success': False, 'message': 'Mohon lengkapi seluruh formulir pengajuan produk bertanda bintang (*).'}), 400

    # Foto 1 (Wajib)
    gambar1 = 'static/images/produk_terasi.jpg'
    if 'gambar_file1' in request.files:
        f = request.files['gambar_file1']
        if f and f.filename != '':
            ext = os.path.splitext(f.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                fn = secure_filename(f"warga_umkm_1_{int(time.time())}_{random.randint(100,999)}{ext}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                gambar1 = f"static/images/uploads/{fn}"

    # Foto 2 (Opsional)
    gambar2 = None
    if 'gambar_file2' in request.files:
        f = request.files['gambar_file2']
        if f and f.filename != '':
            ext = os.path.splitext(f.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                fn = secure_filename(f"warga_umkm_2_{int(time.time())}_{random.randint(100,999)}{ext}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                gambar2 = f"static/images/uploads/{fn}"

    # Foto 3 (Opsional)
    gambar3 = None
    if 'gambar_file3' in request.files:
        f = request.files['gambar_file3']
        if f and f.filename != '':
            ext = os.path.splitext(f.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                fn = secure_filename(f"warga_umkm_3_{int(time.time())}_{random.randint(100,999)}{ext}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                gambar3 = f"static/images/uploads/{fn}"

    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO umkm (nama, produsen, harga, satuan, deskripsi, kontak_wa, gambar, gambar2, gambar3, latitude, longitude, status, nik_pemilik, created_at, alamat, lokasi)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Menunggu Approval', ?, ?, ?, ?)
    ''', (nama, produsen, harga, satuan, deskripsi, kontak_wa, gambar1, gambar2, gambar3, latitude, longitude, nik_pemilik, created_at, alamat, lokasi))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': f'Pengajuan produk "{nama}" berhasil dikirim! Tim administrator desa akan memeriksa dan menganalisa produk Anda sebelum disetujui untuk ditayangkan di website.'
    })

# --- 5. MANAJEMEN WISATA ---
@app.route('/admin/wisata')
@login_required
def admin_wisata():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wisata WHERE status = 'Disetujui' OR status IS NULL ORDER BY urutan ASC")
    wisata_list = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM wisata WHERE status = 'Menunggu Approval' ORDER BY id DESC")
    pengajuan_list = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM wisata WHERE status = 'Ditolak' ORDER BY id DESC")
    ditolak_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template('admin/wisata.html', 
                           wisata_list=wisata_list,
                           pengajuan_list=pengajuan_list,
                           ditolak_list=ditolak_list,
                           total_pending=len(pengajuan_list))

@app.route('/admin/wisata/tambah', methods=['POST'])
@login_required
def admin_tambah_wisata():
    nama = request.form.get('nama')
    kategori = request.form.get('kategori')
    deskripsi = request.form.get('deskripsi')
    fasilitas = request.form.get('fasilitas')
    tiket = request.form.get('tiket')
    lokasi = request.form.get('lokasi')

    try:
        latitude = float(request.form.get('latitude')) if request.form.get('latitude') else None
    except (ValueError, TypeError):
        latitude = None

    try:
        longitude = float(request.form.get('longitude')) if request.form.get('longitude') else None
    except (ValueError, TypeError):
        longitude = None

    gambar = request.form.get('gambar') or 'static/images/pantai_kersik.jpg'
    if 'gambar_file' in request.files:
        file = request.files['gambar_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                filename = secure_filename(f"wisata_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                gambar = f"static/images/uploads/{filename}"

    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO wisata (nama, kategori, deskripsi, fasilitas, tiket, lokasi, latitude, longitude, gambar, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Disetujui', ?)
    ''', (nama, kategori, deskripsi, fasilitas, tiket, lokasi, latitude, longitude, gambar, created_at))
    conn.commit()
    conn.close()

    flash('Destinasi wisata berhasil ditambahkan dan otomatis dipetakan ke peta desa.', 'success')
    return redirect(url_for('admin_wisata'))

@app.route('/admin/wisata/<int:id>/edit', methods=['POST'])
@login_required
def admin_edit_wisata(id):
    nama = request.form.get('nama')
    kategori = request.form.get('kategori')
    deskripsi = request.form.get('deskripsi')
    fasilitas = request.form.get('fasilitas')
    tiket = request.form.get('tiket')
    lokasi = request.form.get('lokasi')

    try:
        latitude = float(request.form.get('latitude')) if request.form.get('latitude') else None
    except (ValueError, TypeError):
        latitude = None

    try:
        longitude = float(request.form.get('longitude')) if request.form.get('longitude') else None
    except (ValueError, TypeError):
        longitude = None

    gambar = request.form.get('gambar_lama') or request.form.get('gambar')
    if 'gambar_file' in request.files:
        file = request.files['gambar_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                filename = secure_filename(f"wisata_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                gambar = f"static/images/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    if not gambar:
        cursor.execute("SELECT gambar FROM wisata WHERE id = ?", (id,))
        row = cursor.fetchone()
        gambar = row['gambar'] if row and row['gambar'] else 'static/images/pantai_kersik.jpg'

    cursor.execute('''
    UPDATE wisata SET nama=?, kategori=?, deskripsi=?, fasilitas=?, tiket=?, lokasi=?, latitude=?, longitude=?, gambar=?
    WHERE id=?
    ''', (nama, kategori, deskripsi, fasilitas, tiket, lokasi, latitude, longitude, gambar, id))
    conn.commit()
    conn.close()

    flash('Destinasi wisata berhasil diperbarui dan peta telah disinkronkan.', 'success')
    return redirect(url_for('admin_wisata'))

@app.route('/admin/wisata/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_wisata(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wisata WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Destinasi wisata berhasil dihapus.', 'info')
    return redirect(url_for('admin_wisata'))

@app.route('/admin/wisata/<int:id>/approve', methods=['POST'])
@login_required
def admin_approve_wisata(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE wisata SET status = 'Disetujui', catatan_admin = 'Telah diverifikasi dan disetujui tayang oleh admin.' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Pengajuan tempat destinasi wisata warga berhasil disetujui (Approved) dan langsung aktif serta terpetakan di website desa!', 'success')
    return redirect(url_for('admin_wisata'))

@app.route('/admin/wisata/<int:id>/tolak', methods=['POST'])
@login_required
def admin_tolak_wisata(id):
    alasan = request.form.get('alasan') or 'Belum memenuhi kriteria destinasi atau potensi desa.'
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE wisata SET status = 'Ditolak', catatan_admin = ? WHERE id = ?", (alasan, id))
    conn.commit()
    conn.close()
    flash('Pengajuan destinasi wisata warga telah ditolak.', 'warning')
    return redirect(url_for('admin_wisata'))

# Endpoint Publik: Warga mengajukan tempat destinasi wisata / potensi desa dari Frontend
@app.route('/api/wisata/ajukan', methods=['POST'])
def api_ajukan_wisata():
    nama = request.form.get('nama')
    kategori = request.form.get('kategori')
    deskripsi = request.form.get('deskripsi')
    fasilitas = request.form.get('fasilitas')
    tiket = request.form.get('tiket') or 'Gratis'
    lokasi = request.form.get('lokasi')
    nama_pengaju = request.form.get('nama_pengaju')
    kontak_pengaju = request.form.get('kontak_pengaju', '').replace('+', '').replace('-', '').strip()

    try:
        latitude = float(request.form.get('latitude')) if request.form.get('latitude') else None
    except (ValueError, TypeError):
        latitude = None

    try:
        longitude = float(request.form.get('longitude')) if request.form.get('longitude') else None
    except (ValueError, TypeError):
        longitude = None

    if not (nama and kategori and deskripsi and lokasi and nama_pengaju and kontak_pengaju):
        return jsonify({'success': False, 'message': 'Mohon lengkapi seluruh formulir pengajuan tempat destinasi bertanda bintang (*).'}), 400

    gambar = 'static/images/pantai_kersik.jpg'
    if 'gambar_file' in request.files:
        f = request.files['gambar_file']
        if f and f.filename != '':
            ext = os.path.splitext(f.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                fn = secure_filename(f"warga_wisata_{int(time.time())}_{random.randint(100,999)}{ext}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                gambar = f"static/images/uploads/{fn}"

    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO wisata (nama, kategori, deskripsi, fasilitas, tiket, lokasi, latitude, longitude, gambar, status, nama_pengaju, kontak_pengaju, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Menunggu Approval', ?, ?, ?)
    ''', (nama, kategori, deskripsi, fasilitas, tiket, lokasi, latitude, longitude, gambar, nama_pengaju, kontak_pengaju, created_at))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': f'Pengajuan tempat destinasi "{nama}" berhasil dikirim! Tim administrator desa akan memeriksa dan menganalisa lokasi sebelum disetujui untuk ditayangkan dan dipetakan di website desa.'
    })

# ==========================================
# 5.1 MANAJEMEN BUKU PUBLIKASI DESA
# ==========================================

@app.route('/admin/publikasi')
@login_required
def admin_publikasi():
    conn = get_db()
    cursor = conn.cursor()

    sort_by = request.args.get('sort', 'default')

    # Fetch Semua Buku
    cursor.execute("SELECT * FROM buku_publikasi")
    raw_all = [dict(r) for r in cursor.fetchall()]

    # Hitung total_akses per buku
    for b in raw_all:
        b['jumlah_unduh'] = b.get('jumlah_unduh') or 0
        b['jumlah_baca'] = b.get('jumlah_baca') or 0
        b['total_akses'] = b['jumlah_unduh'] + b['jumlah_baca']

    # Urutkan berdasarkan parameter sort
    if sort_by == 'terpopuler':
        raw_all.sort(key=lambda x: (x['total_akses'], x['id']), reverse=True)
    elif sort_by == 'unduh':
        raw_all.sort(key=lambda x: (x['jumlah_unduh'], x['id']), reverse=True)
    elif sort_by == 'baca':
        raw_all.sort(key=lambda x: (x['jumlah_baca'], x['id']), reverse=True)
    else:
        raw_all.sort(key=lambda x: (x.get('is_featured', 0), x['id']), reverse=True)

    tayang_list = [b for b in raw_all if b.get('status') == 'Tayang']
    draft_list = [b for b in raw_all if b.get('status') == 'Draft']
    semua_list = raw_all

    # Kategori
    cursor.execute("SELECT * FROM kategori_publikasi ORDER BY urutan ASC, nama ASC")
    kategori_list = [dict(r) for r in cursor.fetchall()]

    # Statistik Total
    total_unduh = sum(b['jumlah_unduh'] for b in semua_list)
    total_baca = sum(b['jumlah_baca'] for b in semua_list)
    total_interaksi = total_unduh + total_baca

    # Buku Terpopuler (paling sering dibaca & diunduh)
    buku_terpopuler = max(semua_list, key=lambda x: x['total_akses']) if semua_list else None

    conn.close()
    return render_template(
        'admin/publikasi.html',
        tayang_list=tayang_list,
        draft_list=draft_list,
        semua_list=semua_list,
        buku_data=semua_list,
        kategori_list=kategori_list,
        total_unduh=total_unduh,
        total_baca=total_baca,
        total_interaksi=total_interaksi,
        buku_terpopuler=buku_terpopuler,
        sort_by=sort_by
    )

@app.route('/admin/publikasi/tambah', methods=['POST'])
@login_required
def admin_tambah_publikasi():
    judul = request.form.get('judul', '').strip()
    kategori = request.form.get('kategori', '').strip()
    penulis = request.form.get('penulis', '').strip() or 'Pemerintah Desa'
    tahun = request.form.get('tahun', '').strip() or str(datetime.now().year)
    edisi = request.form.get('edisi', '').strip() or 'Edisi Tahunan'
    jumlah_halaman = int(request.form.get('jumlah_halaman') or 0)
    ukuran_file = request.form.get('ukuran_file', '').strip()
    sinopsis = request.form.get('sinopsis', '').strip()
    status = request.form.get('status') or 'Tayang'
    is_featured = 1 if request.form.get('is_featured') else 0

    if not judul or not kategori:
        flash('Judul dan Kategori buku publikasi wajib diisi.', 'danger')
        return redirect(url_for('admin_publikasi'))

    # Upload PDF
    file_pdf = ''
    if 'pdf_file' in request.files:
        f = request.files['pdf_file']
        if f and f.filename != '':
            ext = os.path.splitext(f.filename)[1].lower()
            if ext == '.pdf':
                fn = secure_filename(f"buku_{int(time.time())}_{random.randint(100,999)}{ext}")
                full_path = os.path.join(app.config['DOCS_FOLDER'], fn)
                f.save(full_path)
                file_pdf = f"static/docs/publikasi/{fn}"
                if not ukuran_file:
                    sz_mb = os.path.getsize(full_path) / (1024 * 1024)
                    ukuran_file = f"{sz_mb:.1f} MB" if sz_mb >= 1 else f"{int(os.path.getsize(full_path)/1024)} KB"

    if not file_pdf:
        # Fallback to sample
        file_pdf = 'static/docs/publikasi/buku_profil_desa_kersik_2026.pdf'
        if not ukuran_file:
            ukuran_file = '2.4 MB'

    # Upload Cover
    cover_buku = 'static/images/kantor_desa.jpg'
    if 'cover_file' in request.files:
        cf = request.files['cover_file']
        if cf and cf.filename != '':
            ext = os.path.splitext(cf.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                fn = secure_filename(f"cover_{int(time.time())}_{random.randint(100,999)}{ext}")
                cf.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                cover_buku = f"static/images/uploads/{fn}"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO buku_publikasi (
        judul, kategori, penulis, tahun, edisi, jumlah_halaman, ukuran_file,
        sinopsis, cover_buku, file_pdf, jumlah_unduh, status, is_featured
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
    ''', (judul, kategori, penulis, tahun, edisi, jumlah_halaman, ukuran_file, sinopsis, cover_buku, file_pdf, status, is_featured))
    conn.commit()
    conn.close()

    flash(f'Buku publikasi "{judul}" berhasil ditambahkan!', 'success')
    return redirect(url_for('admin_publikasi'))

@app.route('/admin/publikasi/<int:id>/edit', methods=['POST'])
@login_required
def admin_edit_publikasi(id):
    judul = request.form.get('judul', '').strip()
    kategori = request.form.get('kategori', '').strip()
    penulis = request.form.get('penulis', '').strip() or 'Pemerintah Desa'
    tahun = request.form.get('tahun', '').strip() or str(datetime.now().year)
    edisi = request.form.get('edisi', '').strip() or 'Edisi Tahunan'
    jumlah_halaman = int(request.form.get('jumlah_halaman') or 0)
    ukuran_file = request.form.get('ukuran_file', '').strip()
    sinopsis = request.form.get('sinopsis', '').strip()
    status = request.form.get('status') or 'Tayang'
    is_featured = 1 if request.form.get('is_featured') else 0

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM buku_publikasi WHERE id = ?", (id,))
    old = cursor.fetchone()
    if not old:
        conn.close()
        flash('Buku publikasi tidak ditemukan.', 'danger')
        return redirect(url_for('admin_publikasi'))

    file_pdf = old['file_pdf']
    if 'pdf_file' in request.files:
        f = request.files['pdf_file']
        if f and f.filename != '':
            ext = os.path.splitext(f.filename)[1].lower()
            if ext == '.pdf':
                fn = secure_filename(f"buku_{int(time.time())}_{random.randint(100,999)}{ext}")
                full_path = os.path.join(app.config['DOCS_FOLDER'], fn)
                f.save(full_path)
                file_pdf = f"static/docs/publikasi/{fn}"
                if not ukuran_file:
                    sz_mb = os.path.getsize(full_path) / (1024 * 1024)
                    ukuran_file = f"{sz_mb:.1f} MB" if sz_mb >= 1 else f"{int(os.path.getsize(full_path)/1024)} KB"

    cover_buku = old['cover_buku']
    if 'cover_file' in request.files:
        cf = request.files['cover_file']
        if cf and cf.filename != '':
            ext = os.path.splitext(cf.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                fn = secure_filename(f"cover_{int(time.time())}_{random.randint(100,999)}{ext}")
                cf.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                cover_buku = f"static/images/uploads/{fn}"

    if not ukuran_file:
        ukuran_file = old['ukuran_file'] or '2.0 MB'

    jumlah_unduh = request.form.get('jumlah_unduh')
    jumlah_baca = request.form.get('jumlah_baca')
    jumlah_unduh = int(jumlah_unduh) if jumlah_unduh is not None and jumlah_unduh != '' else (old['jumlah_unduh'] or 0)
    jumlah_baca = int(jumlah_baca) if jumlah_baca is not None and jumlah_baca != '' else (old['jumlah_baca'] or 0)

    cursor.execute('''
    UPDATE buku_publikasi SET
        judul = ?, kategori = ?, penulis = ?, tahun = ?, edisi = ?,
        jumlah_halaman = ?, ukuran_file = ?, sinopsis = ?, cover_buku = ?,
        file_pdf = ?, status = ?, is_featured = ?, jumlah_unduh = ?, jumlah_baca = ?
    WHERE id = ?
    ''', (judul, kategori, penulis, tahun, edisi, jumlah_halaman, ukuran_file, sinopsis, cover_buku, file_pdf, status, is_featured, jumlah_unduh, jumlah_baca, id))
    conn.commit()
    conn.close()

    flash(f'Buku publikasi "{judul}" berhasil diperbarui!', 'success')
    return redirect(url_for('admin_publikasi'))

@app.route('/admin/publikasi/<int:id>/status', methods=['POST'])
@login_required
def admin_ubah_status_publikasi(id):
    status_baru = request.form.get('status')
    if status_baru not in ['Tayang', 'Draft']:
        flash('Status tidak valid.', 'danger')
        return redirect(url_for('admin_publikasi'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE buku_publikasi SET status = ? WHERE id = ?", (status_baru, id))
    conn.commit()
    conn.close()
    flash(f'Status publikasi berhasil diubah menjadi "{status_baru}".', 'success')
    return redirect(url_for('admin_publikasi'))

@app.route('/admin/publikasi/<int:id>/featured', methods=['POST'])
@login_required
def admin_toggle_featured_publikasi(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT is_featured, judul FROM buku_publikasi WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        new_val = 0 if row['is_featured'] == 1 else 1
        cursor.execute("UPDATE buku_publikasi SET is_featured = ? WHERE id = ?", (new_val, id))
        conn.commit()
        msg = f'"{row["judul"]}" kini dijadikan Buku Publikasi Unggulan Utama!' if new_val == 1 else f'Status unggulan "{row["judul"]}" dinonaktifkan.'
        flash(msg, 'success')
    conn.close()
    return redirect(url_for('admin_publikasi'))

@app.route('/admin/publikasi/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_publikasi(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM buku_publikasi WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Buku publikasi berhasil dihapus.', 'info')
    return redirect(url_for('admin_publikasi'))

# --- Kategori Buku Publikasi ---
@app.route('/admin/publikasi/kategori/tambah', methods=['POST'])
@login_required
def admin_tambah_kategori_publikasi():
    nama = request.form.get('nama', '').strip()
    if not nama:
        flash('Nama kategori tidak boleh kosong.', 'danger')
        return redirect(url_for('admin_publikasi'))

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(urutan) FROM kategori_publikasi")
        max_u = cursor.fetchone()[0] or 0
        cursor.execute("INSERT INTO kategori_publikasi (nama, urutan) VALUES (?, ?)", (nama, max_u + 1))
        conn.commit()
        flash(f'Kategori publikasi "{nama}" berhasil ditambahkan.', 'success')
    except sqlite3.IntegrityError:
        flash(f'Kategori publikasi "{nama}" sudah ada.', 'warning')
    finally:
        conn.close()
    return redirect(url_for('admin_publikasi'))

@app.route('/admin/publikasi/kategori/<int:id>/edit', methods=['POST'])
@login_required
def admin_edit_kategori_publikasi(id):
    nama_baru = request.form.get('nama', '').strip()
    if not nama_baru:
        flash('Nama kategori tidak boleh kosong.', 'danger')
        return redirect(url_for('admin_publikasi'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nama FROM kategori_publikasi WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        old_nama = row['nama']
        try:
            cursor.execute("UPDATE kategori_publikasi SET nama = ? WHERE id = ?", (nama_baru, id))
            cursor.execute("UPDATE buku_publikasi SET kategori = ? WHERE kategori = ?", (nama_baru, old_nama))
            conn.commit()
            flash(f'Kategori diubah menjadi "{nama_baru}" dan disinkronkan ke seluruh buku terkait.', 'success')
        except sqlite3.IntegrityError:
            flash(f'Kategori "{nama_baru}" sudah ada.', 'warning')
    conn.close()
    return redirect(url_for('admin_publikasi'))

@app.route('/admin/publikasi/kategori/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_kategori_publikasi(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kategori_publikasi WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Kategori publikasi berhasil dihapus.', 'info')
    return redirect(url_for('admin_publikasi'))

# ==========================================
# 5.2 MANAJEMEN PEMBANGUNAN DESA (PROYEK & KEGIATAN)
# ==========================================

def simpan_foto_pembangunan(request, field_name, fallback_url=''):
    """Helper untuk upload file foto pembangunan atau fallback ke url/foto lama"""
    if field_name in request.files:
        f = request.files[field_name]
        if f and f.filename != '':
            ext = os.path.splitext(f.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp', '.svg']:
                fn = secure_filename(f"bangun_{int(time.time())}_{random.randint(100,999)}{ext}")
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], fn)
                f.save(full_path)
                return f"static/images/uploads/{fn}"
    text_url = request.form.get(f"{field_name}_url", "").strip()
    if text_url:
        return text_url
    return fallback_url or ''

@app.route('/admin/pembangunan')
@login_required
def admin_pembangunan():
    conn = get_db()
    cursor = conn.cursor()

    status_filter = request.args.get('status', 'Semua')
    dusun_filter = request.args.get('dusun', 'Semua')
    tahun_filter = request.args.get('tahun', 'Semua')

    query = "SELECT * FROM pembangunan_desa WHERE 1=1"
    params = []

    if status_filter != 'Semua':
        query += " AND status_progres = ?"
        params.append(status_filter)
    if dusun_filter != 'Semua':
        query += " AND dusun = ?"
        params.append(dusun_filter)
    if tahun_filter != 'Semua':
        try:
            th_val = int(tahun_filter)
            query += " AND tahun_anggaran = ?"
            params.append(th_val)
        except Exception:
            pass

    query += " ORDER BY urutan ASC, id DESC"
    cursor.execute(query, tuple(params))
    items = []
    for r in cursor.fetchall():
        d = dict(r)
        try:
            d['foto_list'] = json.loads(d.get('data_foto_json') or '[]')
        except Exception:
            d['foto_list'] = []
        items.append(d)

    # Fetch all for summary stats
    cursor.execute("SELECT * FROM pembangunan_desa")
    all_raw = [dict(r) for r in cursor.fetchall()]

    total_proyek = len(all_raw)
    sedang_dikerjakan = sum(1 for p in all_raw if p.get('status_progres') == 'Sedang Dikerjakan')
    selesai = sum(1 for p in all_raw if p.get('status_progres') == 'Selesai')
    rencana = sum(1 for p in all_raw if p.get('status_progres') == 'Rencana')
    total_anggaran = sum(p.get('anggaran', 0) for p in all_raw)

    cursor.execute("SELECT DISTINCT tahun_anggaran FROM pembangunan_desa ORDER BY tahun_anggaran DESC")
    tahun_list = [r[0] for r in cursor.fetchall() if r[0]]
    if not tahun_list:
        tahun_list = [2026, 2025]

    cursor.execute("SELECT DISTINCT dusun FROM pembangunan_desa WHERE dusun IS NOT NULL AND dusun != ''")
    dusun_list = [r[0] for r in cursor.fetchall()]
    dusun_defaults = ["Dusun Demung Landung", "Dusun Ranca Sari", "Dusun Margahayu", "Dusun Cihaur"]
    for dd in dusun_defaults:
        if dd not in dusun_list:
            dusun_list.append(dd)

    cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
    profil = dict(cursor.fetchone() or {})
    conn.close()

    return render_template(
        'admin/pembangunan.html',
        items=items,
        total_proyek=total_proyek,
        sedang_dikerjakan=sedang_dikerjakan,
        selesai=selesai,
        rencana=rencana,
        total_anggaran=total_anggaran,
        tahun_list=tahun_list,
        dusun_list=dusun_list,
        status_filter=status_filter,
        dusun_filter=dusun_filter,
        tahun_filter=tahun_filter,
        profil=profil
    )

@app.route('/admin/pembangunan/tambah', methods=['POST'])
@login_required
def admin_tambah_pembangunan():
    nama_kegiatan = request.form.get('nama_kegiatan', '').strip()
    kategori = request.form.get('kategori', 'Infrastruktur Jalan').strip()
    lokasi = request.form.get('lokasi', '').strip()
    dusun = request.form.get('dusun', 'Dusun Demung Landung').strip()
    tahun_anggaran = int(request.form.get('tahun_anggaran') or 2026)
    sumber_dana = request.form.get('sumber_dana', 'Dana Desa (DDS)').strip()
    anggaran = int(request.form.get('anggaran') or 0)
    volume = request.form.get('volume', '').strip()
    pelaksana = request.form.get('pelaksana', 'TPK Desa Papayan').strip()
    progres_persen = int(request.form.get('progres_persen') or 0)
    status_progres = request.form.get('status_progres', 'Sedang Dikerjakan').strip()
    tanggal_mulai = request.form.get('tanggal_mulai', '').strip()
    tanggal_selesai = request.form.get('tanggal_selesai', '').strip()
    manfaat = request.form.get('manfaat', '').strip()
    uraian_singkat = request.form.get('uraian_singkat', '').strip()
    uraian_sebelum = request.form.get('uraian_sebelum', '').strip()
    uraian_proses = request.form.get('uraian_proses', '').strip()
    uraian_akhir = request.form.get('uraian_akhir', '').strip()
    status_tayang = request.form.get('status_tayang', 'Tayang').strip()
    urutan = int(request.form.get('urutan') or 1)

    if not nama_kegiatan or not lokasi:
        flash('Nama kegiatan pembangunan dan lokasi wajib diisi.', 'danger')
        return redirect(url_for('admin_pembangunan'))

    # Upload hingga 6 foto untuk 3 fase
    foto_sebelum_1 = simpan_foto_pembangunan(request, 'foto_sebelum_1', 'static/images/banner1.png')
    foto_sebelum_2 = simpan_foto_pembangunan(request, 'foto_sebelum_2', '')
    foto_proses_1 = simpan_foto_pembangunan(request, 'foto_proses_1', 'static/images/banner2.png')
    foto_proses_2 = simpan_foto_pembangunan(request, 'foto_proses_2', '')
    foto_akhir_1 = simpan_foto_pembangunan(request, 'foto_akhir_1', 'static/images/banner3.png')
    foto_akhir_2 = simpan_foto_pembangunan(request, 'foto_akhir_2', '')

    caption_sebelum_1 = request.form.get('caption_sebelum_1', '').strip() or 'Kondisi fisik lokasi sebelum pelaksanaan pembangunan'
    caption_sebelum_2 = request.form.get('caption_sebelum_2', '').strip() or 'Titik dokumentasi awal pra-konstruksi'
    caption_proses_1 = request.form.get('caption_proses_1', '').strip() or 'Tahapan pengerjaan konstruksi pembangunan'
    caption_proses_2 = request.form.get('caption_proses_2', '').strip() or 'Pelaksanaan pengerjaan fisik bersama tim pelaksana'
    caption_akhir_1 = request.form.get('caption_akhir_1', '').strip() or 'Hasil akhir pasca pembangunan fisik'
    caption_akhir_2 = request.form.get('caption_akhir_2', '').strip() or 'Penyelesaian pekerjaan dan siap dimanfaatkan'

    foto_list = []
    if foto_sebelum_1: foto_list.append({"url": foto_sebelum_1, "fase": "Sebelum", "caption": caption_sebelum_1})
    if foto_sebelum_2: foto_list.append({"url": foto_sebelum_2, "fase": "Sebelum", "caption": caption_sebelum_2})
    if foto_proses_1: foto_list.append({"url": foto_proses_1, "fase": "Proses", "caption": caption_proses_1})
    if foto_proses_2: foto_list.append({"url": foto_proses_2, "fase": "Proses", "caption": caption_proses_2})
    if foto_akhir_1: foto_list.append({"url": foto_akhir_1, "fase": "Akhir", "caption": caption_akhir_1})
    if foto_akhir_2: foto_list.append({"url": foto_akhir_2, "fase": "Akhir", "caption": caption_akhir_2})

    data_foto_json = json.dumps(foto_list)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO pembangunan_desa (
        nama_kegiatan, kategori, lokasi, dusun, tahun_anggaran, sumber_dana,
        anggaran, volume, pelaksana, progres_persen, status_progres,
        tanggal_mulai, tanggal_selesai, manfaat, uraian_singkat,
        uraian_sebelum, uraian_proses, uraian_akhir,
        foto_sebelum_1, foto_sebelum_2, foto_proses_1, foto_proses_2, foto_akhir_1, foto_akhir_2,
        data_foto_json, status_tayang, urutan
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        nama_kegiatan, kategori, lokasi, dusun, tahun_anggaran, sumber_dana,
        anggaran, volume, pelaksana, progres_persen, status_progres,
        tanggal_mulai, tanggal_selesai, manfaat, uraian_singkat,
        uraian_sebelum, uraian_proses, uraian_akhir,
        foto_sebelum_1, foto_sebelum_2, foto_proses_1, foto_proses_2, foto_akhir_1, foto_akhir_2,
        data_foto_json, status_tayang, urutan
    ))
    conn.commit()
    conn.close()

    record_activity_log("TAMBAH_PEMBANGUNAN", f"Menambahkan kegiatan pembangunan: {nama_kegiatan} ({status_progres})", session.get('username'))
    flash(f'Kegiatan pembangunan "{nama_kegiatan}" berhasil ditambahkan.', 'success')
    return redirect(url_for('admin_pembangunan'))

@app.route('/admin/pembangunan/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_pembangunan(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pembangunan_desa WHERE id = ?", (id,))
    cur = cursor.fetchone()
    if not cur:
        conn.close()
        flash('Data pembangunan tidak ditemukan.', 'danger')
        return redirect(url_for('admin_pembangunan'))

    cur_dict = dict(cur)

    nama_kegiatan = request.form.get('nama_kegiatan', '').strip() or cur_dict['nama_kegiatan']
    kategori = request.form.get('kategori', '').strip() or cur_dict['kategori']
    lokasi = request.form.get('lokasi', '').strip() or cur_dict['lokasi']
    dusun = request.form.get('dusun', '').strip() or cur_dict['dusun']
    tahun_anggaran = int(request.form.get('tahun_anggaran') or cur_dict['tahun_anggaran'])
    sumber_dana = request.form.get('sumber_dana', '').strip() or cur_dict['sumber_dana']
    anggaran = int(request.form.get('anggaran') or cur_dict['anggaran'])
    volume = request.form.get('volume', '').strip() or cur_dict.get('volume', '')
    pelaksana = request.form.get('pelaksana', '').strip() or cur_dict.get('pelaksana', '')
    progres_persen = int(request.form.get('progres_persen') or cur_dict.get('progres_persen', 0))
    status_progres = request.form.get('status_progres', '').strip() or cur_dict['status_progres']
    tanggal_mulai = request.form.get('tanggal_mulai', '').strip() or cur_dict.get('tanggal_mulai', '')
    tanggal_selesai = request.form.get('tanggal_selesai', '').strip() or cur_dict.get('tanggal_selesai', '')
    manfaat = request.form.get('manfaat', '').strip() or cur_dict.get('manfaat', '')
    uraian_singkat = request.form.get('uraian_singkat', '').strip() or cur_dict.get('uraian_singkat', '')
    uraian_sebelum = request.form.get('uraian_sebelum', '').strip() or cur_dict.get('uraian_sebelum', '')
    uraian_proses = request.form.get('uraian_proses', '').strip() or cur_dict.get('uraian_proses', '')
    uraian_akhir = request.form.get('uraian_akhir', '').strip() or cur_dict.get('uraian_akhir', '')
    status_tayang = request.form.get('status_tayang', 'Tayang').strip()
    urutan = int(request.form.get('urutan') or cur_dict.get('urutan', 1))

    # Ambil foto baru jika diunggah, jika tidak pakai foto lama
    foto_sebelum_1 = simpan_foto_pembangunan(request, 'foto_sebelum_1', cur_dict.get('foto_sebelum_1', ''))
    foto_sebelum_2 = simpan_foto_pembangunan(request, 'foto_sebelum_2', cur_dict.get('foto_sebelum_2', ''))
    foto_proses_1 = simpan_foto_pembangunan(request, 'foto_proses_1', cur_dict.get('foto_proses_1', ''))
    foto_proses_2 = simpan_foto_pembangunan(request, 'foto_proses_2', cur_dict.get('foto_proses_2', ''))
    foto_akhir_1 = simpan_foto_pembangunan(request, 'foto_akhir_1', cur_dict.get('foto_akhir_1', ''))
    foto_akhir_2 = simpan_foto_pembangunan(request, 'foto_akhir_2', cur_dict.get('foto_akhir_2', ''))

    caption_sebelum_1 = request.form.get('caption_sebelum_1', '').strip() or 'Kondisi fisik lokasi sebelum pelaksanaan pembangunan'
    caption_sebelum_2 = request.form.get('caption_sebelum_2', '').strip() or 'Titik dokumentasi awal pra-konstruksi'
    caption_proses_1 = request.form.get('caption_proses_1', '').strip() or 'Tahapan pengerjaan konstruksi pembangunan'
    caption_proses_2 = request.form.get('caption_proses_2', '').strip() or 'Pelaksanaan pengerjaan fisik bersama tim pelaksana'
    caption_akhir_1 = request.form.get('caption_akhir_1', '').strip() or 'Hasil akhir pasca pembangunan fisik'
    caption_akhir_2 = request.form.get('caption_akhir_2', '').strip() or 'Penyelesaian pekerjaan dan siap dimanfaatkan'

    foto_list = []
    if foto_sebelum_1: foto_list.append({"url": foto_sebelum_1, "fase": "Sebelum", "caption": caption_sebelum_1})
    if foto_sebelum_2: foto_list.append({"url": foto_sebelum_2, "fase": "Sebelum", "caption": caption_sebelum_2})
    if foto_proses_1: foto_list.append({"url": foto_proses_1, "fase": "Proses", "caption": caption_proses_1})
    if foto_proses_2: foto_list.append({"url": foto_proses_2, "fase": "Proses", "caption": caption_proses_2})
    if foto_akhir_1: foto_list.append({"url": foto_akhir_1, "fase": "Akhir", "caption": caption_akhir_1})
    if foto_akhir_2: foto_list.append({"url": foto_akhir_2, "fase": "Akhir", "caption": caption_akhir_2})

    data_foto_json = json.dumps(foto_list)

    cursor.execute('''
    UPDATE pembangunan_desa SET
        nama_kegiatan = ?, kategori = ?, lokasi = ?, dusun = ?, tahun_anggaran = ?, sumber_dana = ?,
        anggaran = ?, volume = ?, pelaksana = ?, progres_persen = ?, status_progres = ?,
        tanggal_mulai = ?, tanggal_selesai = ?, manfaat = ?, uraian_singkat = ?,
        uraian_sebelum = ?, uraian_proses = ?, uraian_akhir = ?,
        foto_sebelum_1 = ?, foto_sebelum_2 = ?, foto_proses_1 = ?, foto_proses_2 = ?, foto_akhir_1 = ?, foto_akhir_2 = ?,
        data_foto_json = ?, status_tayang = ?, urutan = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (
        nama_kegiatan, kategori, lokasi, dusun, tahun_anggaran, sumber_dana,
        anggaran, volume, pelaksana, progres_persen, status_progres,
        tanggal_mulai, tanggal_selesai, manfaat, uraian_singkat,
        uraian_sebelum, uraian_proses, uraian_akhir,
        foto_sebelum_1, foto_sebelum_2, foto_proses_1, foto_proses_2, foto_akhir_1, foto_akhir_2,
        data_foto_json, status_tayang, urutan, id
    ))
    conn.commit()
    conn.close()

    record_activity_log("EDIT_PEMBANGUNAN", f"Mengubah data pembangunan ID {id}: {nama_kegiatan}", session.get('username'))
    flash(f'Pembaruan kegiatan "{nama_kegiatan}" berhasil disimpan.', 'success')
    return redirect(url_for('admin_pembangunan'))

@app.route('/admin/pembangunan/hapus/<int:id>', methods=['POST'])
@login_required
def admin_hapus_pembangunan(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nama_kegiatan FROM pembangunan_desa WHERE id = ?", (id,))
    row = cursor.fetchone()
    nama = row[0] if row else f"ID {id}"

    cursor.execute("DELETE FROM pembangunan_desa WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    record_activity_log("HAPUS_PEMBANGUNAN", f"Menghapus kegiatan pembangunan: {nama}", session.get('username'))
    flash(f'Kegiatan pembangunan "{nama}" berhasil dihapus.', 'info')
    return redirect(url_for('admin_pembangunan'))

@app.route('/admin/pembangunan/toggle-status/<int:id>', methods=['POST'])
@login_required
def admin_toggle_status_pembangunan(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status_tayang, nama_kegiatan FROM pembangunan_desa WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        curr_status = row[0]
        new_status = 'Draf' if curr_status == 'Tayang' else 'Tayang'
        cursor.execute("UPDATE pembangunan_desa SET status_tayang = ? WHERE id = ?", (new_status, id))
        conn.commit()
        record_activity_log("TOGGLE_STATUS_PEMBANGUNAN", f"Mengubah status tayang ID {id} ({row[1]}) menjadi {new_status}", session.get('username'))
        flash(f'Status publikasi "{row[1]}" diubah menjadi {new_status}.', 'success')
    conn.close()
    return redirect(url_for('admin_pembangunan'))

@app.route('/api/pembangunan/<int:id>')
def api_pembangunan_detail(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pembangunan_desa WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({'success': False, 'message': 'Data tidak ditemukan'}), 404

    d = dict(row)
    try:
        d['foto_list'] = json.loads(d.get('data_foto_json') or '[]')
    except Exception:
        d['foto_list'] = []

    return jsonify({'success': True, 'data': d})

@app.route('/pembangunan')
def halaman_pembangunan():
    """Halaman Publik Menampilkan Transparansi Progres Pembangunan Desa Papayan"""
    conn = get_db()
    cursor = conn.cursor()

    status_filter = request.args.get('status', 'Semua')
    dusun_filter = request.args.get('dusun', 'Semua')
    tahun_filter = request.args.get('tahun', 'Semua')

    query = "SELECT * FROM pembangunan_desa WHERE status_tayang = 'Tayang'"
    params = []

    if status_filter != 'Semua':
        query += " AND status_progres = ?"
        params.append(status_filter)
    if dusun_filter != 'Semua':
        query += " AND dusun = ?"
        params.append(dusun_filter)
    if tahun_filter != 'Semua':
        try:
            th_val = int(tahun_filter)
            query += " AND tahun_anggaran = ?"
            params.append(th_val)
        except Exception:
            pass

    query += " ORDER BY urutan ASC, id DESC"
    cursor.execute(query, tuple(params))
    items = []
    for r in cursor.fetchall():
        d = dict(r)
        try:
            d['foto_list'] = json.loads(d.get('data_foto_json') or '[]')
        except Exception:
            d['foto_list'] = []
        items.append(d)

    cursor.execute("SELECT * FROM pembangunan_desa WHERE status_tayang = 'Tayang'")
    all_raw = [dict(r) for r in cursor.fetchall()]

    total_proyek = len(all_raw)
    sedang_dikerjakan = sum(1 for p in all_raw if p.get('status_progres') == 'Sedang Dikerjakan')
    selesai = sum(1 for p in all_raw if p.get('status_progres') == 'Selesai')
    rencana = sum(1 for p in all_raw if p.get('status_progres') == 'Rencana')
    total_anggaran = sum(p.get('anggaran', 0) for p in all_raw)

    cursor.execute("SELECT DISTINCT tahun_anggaran FROM pembangunan_desa WHERE status_tayang = 'Tayang' ORDER BY tahun_anggaran DESC")
    tahun_list = [r[0] for r in cursor.fetchall() if r[0]]
    if not tahun_list:
        tahun_list = [2026, 2025]

    cursor.execute("SELECT DISTINCT dusun FROM pembangunan_desa WHERE status_tayang = 'Tayang' AND dusun IS NOT NULL AND dusun != ''")
    dusun_list = [r[0] for r in cursor.fetchall()]
    dusun_defaults = ["Dusun Demung Landung", "Dusun Ranca Sari", "Dusun Margahayu", "Dusun Cihaur"]
    for dd in dusun_defaults:
        if dd not in dusun_list:
            dusun_list.append(dd)

    cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
    profil = dict(cursor.fetchone() or {})
    conn.close()

    return render_template(
        'pembangunan.html',
        items=items,
        total_proyek=total_proyek,
        sedang_dikerjakan=sedang_dikerjakan,
        selesai=selesai,
        rencana=rencana,
        total_anggaran=total_anggaran,
        tahun_list=tahun_list,
        dusun_list=dusun_list,
        status_filter=status_filter,
        dusun_filter=dusun_filter,
        tahun_filter=tahun_filter,
        profil=profil
    )

# ==========================================
# ADMIN RUNNING TEXT (PENGUMUMAN BERJALAN)
# ==========================================

@app.route('/admin/running-text')
@login_required
def admin_running_text():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM running_texts ORDER BY urutan ASC, id ASC")
    items = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
    profil = dict(cursor.fetchone() or {})
    conn.close()
    tab = request.args.get('tab', 'running-text')
    return render_template('admin/running_text.html', items=items, profil=profil, active_tab=tab)

@app.route('/admin/running-text/tambah', methods=['POST'])
@login_required
def admin_running_text_tambah():
    teks = request.form.get('teks', '').strip()
    urutan = request.form.get('urutan', '1').strip()
    is_active = 1 if request.form.get('is_active') == '1' else 0
    try:
        urutan = int(urutan)
    except ValueError:
        urutan = 1

    if not teks:
        flash('Isi teks pengumuman berjalan tidak boleh kosong.', 'danger')
        return redirect(url_for('admin_running_text'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO running_texts (teks, urutan, is_active) VALUES (?, ?, ?)",
        (teks, urutan, is_active)
    )
    conn.commit()
    conn.close()

    record_activity_log(
        action='TAMBAH_RUNNING_TEXT',
        details=f'Menambahkan teks berjalan baru: "{teks[:50]}..." (Urutan: {urutan}, Status: {"Aktif" if is_active else "Nonaktif"})',
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    flash('Teks berjalan berhasil ditambahkan!', 'success')
    return redirect(url_for('admin_running_text'))

@app.route('/admin/running-text/<int:id>/edit', methods=['POST'])
@login_required
def admin_running_text_edit(id):
    teks = request.form.get('teks', '').strip()
    urutan = request.form.get('urutan', '1').strip()
    is_active = 1 if request.form.get('is_active') == '1' else 0
    try:
        urutan = int(urutan)
    except ValueError:
        urutan = 1

    if not teks:
        flash('Isi teks pengumuman berjalan tidak boleh kosong.', 'danger')
        return redirect(url_for('admin_running_text'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE running_texts SET teks = ?, urutan = ?, is_active = ? WHERE id = ?",
        (teks, urutan, is_active, id)
    )
    conn.commit()
    conn.close()

    record_activity_log(
        action='EDIT_RUNNING_TEXT',
        details=f'Mengedit teks berjalan ID {id}: "{teks[:50]}..."',
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    flash('Teks berjalan berhasil diperbarui!', 'success')
    return redirect(url_for('admin_running_text'))

@app.route('/admin/running-text/<int:id>/hapus', methods=['POST'])
@login_required
def admin_running_text_hapus(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT teks FROM running_texts WHERE id = ?", (id,))
    item = cursor.fetchone()
    teks_lama = item[0] if item else ''
    cursor.execute("DELETE FROM running_texts WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    record_activity_log(
        action='HAPUS_RUNNING_TEXT',
        details=f'Menghapus teks berjalan ID {id}: "{teks_lama[:50]}..."',
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    flash('Teks berjalan berhasil dihapus.', 'info')
    return redirect(url_for('admin_running_text'))

@app.route('/admin/running-text/<int:id>/toggle', methods=['POST'])
@login_required
def admin_running_text_toggle(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE running_texts SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?", (id,))
    conn.commit()
    cursor.execute("SELECT is_active, teks FROM running_texts WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    status_str = 'Diaktifkan' if (row and row[0] == 1) else 'Dinonaktifkan'
    flash(f'Status teks berjalan berhasil {status_str.lower()}.', 'success')
    return redirect(url_for('admin_running_text'))

@app.route('/admin/running-text/reorder', methods=['POST'])
@login_required
def admin_reorder_running_text():
    data = request.get_json(silent=True) or request.form
    order_ids = data.get('order', [])
    if not order_ids or not isinstance(order_ids, list):
        return jsonify({'status': 'error', 'message': 'Data urutan tidak valid'}), 400

    conn = get_db()
    cursor = conn.cursor()
    for index, item_id in enumerate(order_ids):
        try:
            cursor.execute("UPDATE running_texts SET urutan = ? WHERE id = ?", (index + 1, int(item_id)))
        except (ValueError, TypeError):
            continue
    conn.commit()
    conn.close()

    record_activity_log(
        action='REORDER_RUNNING_TEXT',
        details=f'Mengubah urutan running text melalui drag and drop ({len(order_ids)} item)',
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    return jsonify({'status': 'success', 'message': 'Urutan running text berhasil disimpan!'})

@app.route('/admin/footer/update', methods=['POST'])
@login_required
def admin_update_footer():
    alamat = request.form.get('alamat', '').strip()
    telepon = request.form.get('telepon', '').strip()
    email = request.form.get('email', '').strip()
    jam_pelayanan = request.form.get('jam_pelayanan', '').strip()
    provinsi = request.form.get('provinsi', '').strip() or 'Jawa Barat'
    kabupaten = request.form.get('kabupaten', '').strip() or 'Tasikmalaya'
    kecamatan = request.form.get('kecamatan', '').strip() or 'Jatiwaras'
    kode_wilayah = request.form.get('kode_wilayah', '').strip()
    kode_pos = request.form.get('kode_pos', '').strip()
    tagline_website = request.form.get('tagline_website', '').strip()
    subtagline_website = request.form.get('subtagline_website', '').strip()
    teks_footer_deskripsi = request.form.get('teks_footer_deskripsi', '').strip()
    teks_footer_copyright = request.form.get('teks_footer_copyright', '').strip()
    teks_footer_portal = request.form.get('teks_footer_portal', '').strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE profil_desa SET
        alamat = ?,
        telepon = ?,
        email = ?,
        jam_pelayanan = ?,
        provinsi = ?,
        kabupaten = ?,
        kecamatan = ?,
        kode_wilayah = ?,
        kode_pos = ?,
        tagline_website = ?,
        subtagline_website = ?,
        teks_footer_deskripsi = ?,
        teks_footer_copyright = ?,
        teks_footer_portal = ?
    WHERE id = 1
    ''', (alamat, telepon, email, jam_pelayanan, provinsi, kabupaten, kecamatan, kode_wilayah, kode_pos, tagline_website, subtagline_website, teks_footer_deskripsi, teks_footer_copyright, teks_footer_portal))
    conn.commit()
    conn.close()

    record_activity_log(
        action='UPDATE_FOOTER_INFO',
        details='Memperbarui informasi kontak, alamat, dan teks footer desa',
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    flash('Informasi dan pengaturan Footer Desa berhasil disimpan!', 'success')
    return redirect(url_for('admin_running_text', tab='footer'))

# ==========================================
# 12. MANAJEMEN POP-UP PENGUMUMAN & BANNER WEB
# ==========================================

@app.route('/admin/popup')
@login_required
def admin_popup():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM popup_informasi ORDER BY urutan ASC, id DESC")
    popup_list = [dict(row) for row in cursor.fetchall()]

    # Hitung status dinamis berdasarkan rentang waktu tayang
    for p in popup_list:
        p['status_info'] = hitung_status_waktu_popup(p)

    # Statistik Pop-up Akurat
    total_popup = len(popup_list)
    total_tayang = sum(1 for p in popup_list if p['status_info']['status_waktu'] == 'Tayang')
    total_terjadwal = sum(1 for p in popup_list if p['status_info']['status_waktu'] == 'Terjadwal')
    total_kedaluwarsa = sum(1 for p in popup_list if p['status_info']['status_waktu'] == 'Kedaluwarsa')
    total_draf = sum(1 for p in popup_list if p['status_info']['status_waktu'] == 'Draf')

    # Pop-up yang sedang aktif tayang saat ini
    active_popup = next((p for p in popup_list if p['status_info']['is_aktif']), None)

    conn.close()
    return render_template(
        'admin/popup.html',
        popup_list=popup_list,
        total_popup=total_popup,
        total_tayang=total_tayang,
        total_terjadwal=total_terjadwal,
        total_kedaluwarsa=total_kedaluwarsa,
        total_draf=total_draf,
        active_popup=active_popup
    )

@app.route('/admin/popup/tambah', methods=['POST'])
@login_required
def admin_popup_tambah():
    judul = request.form.get('judul', '').strip()
    subjudul = request.form.get('subjudul', '').strip()
    kategori = request.form.get('kategori', 'Pengumuman Penting').strip() or 'Pengumuman Penting'
    isi = request.form.get('isi', '').strip()
    link_url = request.form.get('link_url', '').strip()
    link_teks = request.form.get('link_teks', 'Lihat Selengkapnya').strip() or 'Lihat Selengkapnya'
    tombol_sekunder_teks = request.form.get('tombol_sekunder_teks', 'Tutup').strip() or 'Tutup'
    status = request.form.get('status', 'Tayang').strip()
    tampil_sekali = 1 if request.form.get('tampil_sekali') == '1' else 0
    urutan = request.form.get('urutan', type=int) or 1
    tanggal_mulai = request.form.get('tanggal_mulai', '').strip() or None
    tanggal_selesai = request.form.get('tanggal_selesai', '').strip() or None

    if not judul:
        flash('Judul pop-up pengumuman wajib diisi.', 'danger')
        return redirect(url_for('admin_popup'))

    # Upload Gambar / Banner Flyer
    gambar = request.form.get('gambar_url', '').strip()
    if 'gambar_file' in request.files:
        file = request.files['gambar_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                filename = secure_filename(f"popup_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                gambar = f"static/images/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    # Jika admin memilih jadikan tayang tunggal, ubah pop-up lain menjadi tidak tayang
    if status == 'Tayang' and request.form.get('jadikan_tunggal') == '1':
        cursor.execute("UPDATE popup_informasi SET status = 'Tidak Tayang'")

    cursor.execute('''
    INSERT INTO popup_informasi (
        judul, subjudul, kategori, isi, gambar, link_url, link_teks, tombol_sekunder_teks,
        status, tampil_sekali, urutan, tanggal_mulai, tanggal_selesai
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        judul, subjudul, kategori, isi, gambar, link_url, link_teks, tombol_sekunder_teks,
        status, tampil_sekali, urutan, tanggal_mulai, tanggal_selesai
    ))
    conn.commit()
    conn.close()

    record_activity_log(
        action='TAMBAH_POPUP',
        details=f'Menambahkan pop-up informasi baru: "{judul}" (Status: {status})',
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )

    flash('Pop-up banner informasi berhasil ditambahkan!', 'success')
    return redirect(url_for('admin_popup'))

@app.route('/admin/popup/<int:id>/edit', methods=['POST'])
@login_required
def admin_popup_edit(id):
    judul = request.form.get('judul', '').strip()
    subjudul = request.form.get('subjudul', '').strip()
    kategori = request.form.get('kategori', 'Pengumuman Penting').strip() or 'Pengumuman Penting'
    isi = request.form.get('isi', '').strip()
    link_url = request.form.get('link_url', '').strip()
    link_teks = request.form.get('link_teks', 'Lihat Selengkapnya').strip() or 'Lihat Selengkapnya'
    tombol_sekunder_teks = request.form.get('tombol_sekunder_teks', 'Tutup').strip() or 'Tutup'
    status = request.form.get('status', 'Tayang').strip()
    tampil_sekali = 1 if request.form.get('tampil_sekali') == '1' else 0
    urutan = request.form.get('urutan', type=int) or 1
    tanggal_mulai = request.form.get('tanggal_mulai', '').strip() or None
    tanggal_selesai = request.form.get('tanggal_selesai', '').strip() or None

    if not judul:
        flash('Judul pop-up pengumuman wajib diisi.', 'danger')
        return redirect(url_for('admin_popup'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT gambar FROM popup_informasi WHERE id = ?", (id,))
    row_old = cursor.fetchone()
    gambar = row_old['gambar'] if row_old else ''

    # Cek jika ada input gambar_url baru
    gambar_url_input = request.form.get('gambar_url', '').strip()
    if gambar_url_input:
        gambar = gambar_url_input

    # Cek jika ada upload file gambar baru
    if 'gambar_file' in request.files:
        file = request.files['gambar_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                filename = secure_filename(f"popup_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                gambar = f"static/images/uploads/{filename}"

    if status == 'Tayang' and request.form.get('jadikan_tunggal') == '1':
        cursor.execute("UPDATE popup_informasi SET status = 'Tidak Tayang' WHERE id != ?", (id,))

    cursor.execute('''
    UPDATE popup_informasi SET
        judul = ?, subjudul = ?, kategori = ?, isi = ?, gambar = ?,
        link_url = ?, link_teks = ?, tombol_sekunder_teks = ?,
        status = ?, tampil_sekali = ?, urutan = ?,
        tanggal_mulai = ?, tanggal_selesai = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (
        judul, subjudul, kategori, isi, gambar, link_url, link_teks, tombol_sekunder_teks,
        status, tampil_sekali, urutan, tanggal_mulai, tanggal_selesai, id
    ))
    conn.commit()
    conn.close()

    record_activity_log(
        action='EDIT_POPUP',
        details=f'Memperbarui pop-up informasi ID {id}: "{judul}" (Status: {status})',
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )

    flash('Pop-up pengumuman informasi berhasil diperbarui!', 'success')
    return redirect(url_for('admin_popup'))

@app.route('/admin/popup/<int:id>/toggle-status', methods=['POST'])
@login_required
def admin_popup_toggle_status(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status, judul FROM popup_informasi WHERE id = ?", (id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        flash('Data pop-up tidak ditemukan.', 'danger')
        return redirect(url_for('admin_popup'))

    current_status = row['status']
    new_status = 'Tidak Tayang' if current_status == 'Tayang' else 'Tayang'

    cursor.execute("UPDATE popup_informasi SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, id))
    conn.commit()
    conn.close()

    pesan_status = 'ditayangkan di halaman depan website' if new_status == 'Tayang' else 'dinonaktifkan (dijadikan draf)'
    flash(f'Pop-up "{row["judul"]}" berhasil {pesan_status}!', 'success')
    return redirect(url_for('admin_popup'))

@app.route('/admin/popup/<int:id>/hapus', methods=['POST'])
@login_required
def admin_popup_hapus(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT judul, gambar FROM popup_informasi WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        if row['gambar'] and row['gambar'].startswith('static/images/uploads/'):
            try:
                full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), row['gambar'].replace('/', os.sep))
                if os.path.exists(full_path):
                    os.remove(full_path)
            except Exception:
                pass
        cursor.execute("DELETE FROM popup_informasi WHERE id = ?", (id,))
        conn.commit()
        record_activity_log(
            action='HAPUS_POPUP',
            details=f'Menghapus pop-up ID {id}: "{row["judul"]}"',
            username=session.get('username'),
            user_id=session.get('user_id'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        flash(f'Pop-up "{row["judul"]}" berhasil dihapus.', 'info')
    conn.close()
    return redirect(url_for('admin_popup'))

# ==========================================
# PUBLIC PUBLIKASI & PERPUSTAKAAN DIGITAL
# ==========================================

@app.route('/publikasi')
def publikasi():
    conn = get_db()
    cursor = conn.cursor()

    # Profil
    cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
    profil = dict(cursor.fetchone() or {})

    # Kategori
    cursor.execute("SELECT * FROM kategori_publikasi ORDER BY urutan ASC, nama ASC")
    kategori_list = [dict(r) for r in cursor.fetchall()]

    kat_filter = request.args.get('kategori', '').strip()
    q = request.args.get('q', '').strip()

    sql = "SELECT * FROM buku_publikasi WHERE status = 'Tayang'"
    params = []

    if kat_filter:
        sql += " AND kategori = ?"
        params.append(kat_filter)

    if q:
        sql += " AND (judul LIKE ? OR sinopsis LIKE ? OR penulis LIKE ? OR tahun LIKE ?)"
        wildcard = f"%{q}%"
        params.extend([wildcard, wildcard, wildcard, wildcard])

    sql += " ORDER BY is_featured DESC, id DESC"
    cursor.execute(sql, tuple(params))
    buku_list = [dict(r) for r in cursor.fetchall()]

    # Featured Book (buku unggulan utama)
    cursor.execute("SELECT * FROM buku_publikasi WHERE status = 'Tayang' AND is_featured = 1 ORDER BY id DESC LIMIT 1")
    featured_row = cursor.fetchone()
    if not featured_row and buku_list:
        featured_row = buku_list[0]
    featured_buku = dict(featured_row) if featured_row else None

    # Total unduhan dan baca online
    cursor.execute("SELECT SUM(jumlah_unduh), SUM(jumlah_baca) FROM buku_publikasi WHERE status = 'Tayang'")
    totals = cursor.fetchone()
    total_unduh = totals[0] or 0
    total_baca = totals[1] or 0

    conn.close()

    return render_template(
        'publikasi.html',
        profil=profil,
        kategori_list=kategori_list,
        buku_list=buku_list,
        featured_buku=featured_buku,
        selected_kategori=kat_filter,
        search_query=q,
        total_unduh=total_unduh,
        total_baca=total_baca
    )

@app.route('/publikasi/unduh/<int:id>')
def unduh_publikasi(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM buku_publikasi WHERE id = ?", (id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        flash('Dokumen publikasi tidak ditemukan.', 'warning')
        return redirect(url_for('publikasi'))

    # Update counter jumlah unduh
    cursor.execute("UPDATE buku_publikasi SET jumlah_unduh = COALESCE(jumlah_unduh, 0) + 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    buku = dict(row)
    pdf_rel_path = buku['file_pdf']
    if pdf_rel_path.startswith('/'):
        pdf_rel_path = pdf_rel_path[1:]

    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), pdf_rel_path.replace('/', os.sep))
    if not os.path.exists(full_path):
        # Fallback to sample
        full_path = os.path.join(app.config['DOCS_FOLDER'], 'buku_profil_desa_kersik_2026.pdf')

    safe_title = secure_filename(buku['judul']) or 'publikasi_desa'
    return send_file(
        full_path,
        as_attachment=True,
        download_name=f"{safe_title}.pdf",
        mimetype='application/pdf'
    )

@app.route('/api/publikasi/<int:id>/baca', methods=['POST'])
@app.route('/api/publikasi/<int:id>/counter', methods=['POST'])
def api_publikasi_baca(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE buku_publikasi SET jumlah_baca = COALESCE(jumlah_baca, 0) + 1 WHERE id = ?", (id,))
    conn.commit()
    cursor.execute("SELECT jumlah_baca, jumlah_unduh FROM buku_publikasi WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    return jsonify({
        'success': True,
        'jumlah_baca': row['jumlah_baca'],
        'jumlah_unduh': row['jumlah_unduh'],
        'total_akses': (row['jumlah_baca'] or 0) + (row['jumlah_unduh'] or 0)
    })

# --- 6. MANAJEMEN APARATUR DESA (SOTK) ---
@app.route('/admin/aparatur')
@login_required
def admin_aparatur():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM perangkat_desa ORDER BY urutan ASC")
    aparatur_list = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM jabatan_struktural ORDER BY urutan ASC, nama_jabatan ASC")
    jabatan_list = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
    row_profil = cursor.fetchone()
    profil = dict(row_profil) if row_profil else {}

    # Ambil data Sejarah Desa
    cursor.execute("SELECT * FROM sejarah_desa ORDER BY urutan ASC, id ASC")
    sejarah_list = [dict(row) for row in cursor.fetchall()]

    # Ambil data Kepala Desa dari Masa ke Masa (Mulai dari yang menjabat sekarang ke yang lampau)
    cursor.execute("""
        SELECT * FROM kades_masa_ke_masa 
        ORDER BY CASE WHEN status_jabatan = 'Menjabat' THEN 0 ELSE 1 END,
                 tahun_mulai DESC, urutan ASC, id DESC
    """)
    kades_riwayat_list = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template(
        'admin/aparatur.html',
        aparatur_list=aparatur_list,
        jabatan_list=jabatan_list,
        profil=profil,
        sejarah_list=sejarah_list,
        kades_riwayat_list=kades_riwayat_list
    )

@app.route('/admin/aparatur/bagan/upload', methods=['POST'])
@login_required
def admin_upload_bagan_aparatur():
    jenis = request.form.get('jenis_bagan', 'all')
    keterangan_desa = request.form.get('keterangan_bagan_desa')
    keterangan_bpd = request.form.get('keterangan_bagan_bpd')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT bagan_struktur_desa, bagan_struktur_bpd FROM profil_desa WHERE id = 1")
    row = cursor.fetchone()
    new_bagan_desa = row['bagan_struktur_desa'] if row else None
    new_bagan_bpd = row['bagan_struktur_bpd'] if row else None

    # 1. Upload Bagan Struktur Organisasi Pemerintah Desa
    if 'bagan_desa_file' in request.files:
        f_desa = request.files['bagan_desa_file']
        if f_desa and f_desa.filename != '':
            ext = os.path.splitext(f_desa.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp', '.svg']:
                filename = secure_filename(f"bagan_pemdes_{int(time.time())}_{random.randint(100,999)}{ext}")
                f_desa.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_bagan_desa = f"static/images/uploads/{filename}"

    # 2. Upload Bagan Struktur Organisasi BPD
    if 'bagan_bpd_file' in request.files:
        f_bpd = request.files['bagan_bpd_file']
        if f_bpd and f_bpd.filename != '':
            ext = os.path.splitext(f_bpd.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp', '.svg']:
                filename = secure_filename(f"bagan_bpd_{int(time.time())}_{random.randint(100,999)}{ext}")
                f_bpd.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_bagan_bpd = f"static/images/uploads/{filename}"

    # Dukungan URL eksternal / path langsung jika diinput
    bagan_desa_url = (request.form.get('bagan_desa_url') or '').strip()
    if bagan_desa_url:
        new_bagan_desa = bagan_desa_url

    bagan_bpd_url = (request.form.get('bagan_bpd_url') or '').strip()
    if bagan_bpd_url:
        new_bagan_bpd = bagan_bpd_url

    cursor.execute('''
        UPDATE profil_desa 
        SET bagan_struktur_desa = ?, 
            bagan_struktur_bpd = ?,
            keterangan_bagan_desa = COALESCE(?, keterangan_bagan_desa),
            keterangan_bagan_bpd = COALESCE(?, keterangan_bagan_bpd)
        WHERE id = 1
    ''', (new_bagan_desa, new_bagan_bpd, keterangan_desa, keterangan_bpd))
    conn.commit()
    conn.close()

    try:
        record_activity_log(
            'UPLOAD_BAGAN_SOTK',
            f"Memperbarui berkas bagan struktur organisasi Pemerintah Desa & BPD"
        )
    except Exception:
        pass

    flash('Bagan Struktur Organisasi Pemerintah Desa dan BPD berhasil disimpan!', 'success')
    return redirect(url_for('admin_aparatur'))

@app.route('/admin/aparatur/bagan/reset/<jenis>', methods=['POST'])
@login_required
def admin_reset_bagan_aparatur(jenis):
    conn = get_db()
    cursor = conn.cursor()
    if jenis == 'desa':
        cursor.execute("UPDATE profil_desa SET bagan_struktur_desa = NULL WHERE id = 1")
        msg = "Bagan Struktur Organisasi Pemerintah Desa berhasil direset ke diagram sistem default."
    elif jenis == 'bpd':
        cursor.execute("UPDATE profil_desa SET bagan_struktur_bpd = NULL WHERE id = 1")
        msg = "Bagan Struktur Organisasi BPD berhasil direset ke diagram sistem default."
    else:
        cursor.execute("UPDATE profil_desa SET bagan_struktur_desa = NULL, bagan_struktur_bpd = NULL WHERE id = 1")
        msg = "Semua Bagan Struktur Organisasi berhasil direset ke diagram sistem default."
    conn.commit()
    conn.close()

    try:
        record_activity_log('RESET_BAGAN_SOTK', f"Mereset bagan struktur {jenis} ke diagram default")
    except Exception:
        pass

    flash(msg, 'info')
    return redirect(url_for('admin_aparatur'))


@app.route('/admin/aparatur/jabatan/list', methods=['GET'])
@login_required
def admin_list_jabatan():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT j.id, j.nama_jabatan, j.urutan, COUNT(p.id) as total_dipakai
    FROM jabatan_struktural j
    LEFT JOIN perangkat_desa p ON LOWER(p.jabatan) = LOWER(j.nama_jabatan)
    GROUP BY j.id, j.nama_jabatan
    ORDER BY j.urutan ASC, j.nama_jabatan ASC
    ''')
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({'status': 'success', 'data': rows})

@app.route('/admin/aparatur/jabatan/tambah', methods=['POST'])
@login_required
def admin_tambah_jabatan():
    nama_jabatan = ''
    if request.is_json:
        data = request.get_json() or {}
        nama_jabatan = data.get('nama_jabatan', '').strip()
    else:
        nama_jabatan = request.form.get('nama_jabatan', '').strip()

    if not nama_jabatan:
        return jsonify({'status': 'error', 'message': 'Nama jabatan tidak boleh kosong'}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO jabatan_struktural (nama_jabatan, urutan) VALUES (?, 99)", (nama_jabatan,))
        conn.commit()
        cursor.execute("SELECT id, nama_jabatan FROM jabatan_struktural WHERE LOWER(nama_jabatan) = LOWER(?)", (nama_jabatan,))
        row = cursor.fetchone()
        conn.close()
        return jsonify({
            'status': 'success',
            'id': row['id'] if row else None,
            'nama_jabatan': row['nama_jabatan'] if row else nama_jabatan,
            'message': f'Jabatan "{nama_jabatan}" berhasil ditambahkan!'
        })
    except Exception as e:
        conn.close()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin/aparatur/jabatan/<int:id>/edit', methods=['POST'])
@login_required
def admin_edit_jabatan(id):
    data = request.get_json() if request.is_json else request.form
    nama_baru = (data.get('nama_jabatan') or '').strip()
    if not nama_baru:
        return jsonify({'status': 'error', 'message': 'Nama jabatan tidak boleh kosong'}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nama_jabatan FROM jabatan_struktural WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Jabatan tidak ditemukan'}), 404

        old_name = row['nama_jabatan']
        cursor.execute("UPDATE jabatan_struktural SET nama_jabatan = ? WHERE id = ?", (nama_baru, id))
        # Update jabatan in perangkat_desa if matching
        cursor.execute("UPDATE perangkat_desa SET jabatan = ? WHERE LOWER(jabatan) = LOWER(?)", (nama_baru, old_name))
        conn.commit()
        conn.close()
        return jsonify({
            'status': 'success',
            'id': id,
            'nama_jabatan': nama_baru,
            'nama_lama': old_name,
            'message': f'Jabatan "{old_name}" berhasil diubah menjadi "{nama_baru}".'
        })
    except Exception as e:
        conn.close()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin/aparatur/jabatan/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_jabatan(id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nama_jabatan FROM jabatan_struktural WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Jabatan tidak ditemukan'}), 404

        nama = row['nama_jabatan']
        cursor.execute("DELETE FROM jabatan_struktural WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return jsonify({
            'status': 'success',
            'id': id,
            'nama_jabatan': nama,
            'message': f'Jabatan "{nama}" berhasil dihapus dari daftar pilihan.'
        })
    except Exception as e:
        conn.close()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin/aparatur/jabatan/reorder', methods=['POST'])
@login_required
def admin_reorder_jabatan():
    data = request.get_json() if request.is_json else request.form
    order_ids = data.get('order', [])
    if not order_ids or not isinstance(order_ids, list):
        return jsonify({'status': 'error', 'message': 'Data urutan tidak valid'}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        for idx, j_id in enumerate(order_ids, start=1):
            cursor.execute("UPDATE jabatan_struktural SET urutan = ? WHERE id = ?", (idx, int(j_id)))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Urutan jabatan berhasil disimpan!'})
    except Exception as e:
        conn.close()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin/aparatur/tambah', methods=['POST'])
@login_required
def admin_tambah_aparatur():
    nama = request.form.get('nama')
    jabatan = request.form.get('jabatan')
    periode = request.form.get('periode') or '2021 - 2027'
    kontak = request.form.get('kontak')
    sambutan = request.form.get('sambutan_singkat')
    urutan = int(request.form.get('urutan') or 99)

    foto = request.form.get('foto') or 'static/images/kades.jpg'
    if 'foto_file' in request.files:
        file = request.files['foto_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                filename = secure_filename(f"aparatur_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                foto = f"static/images/uploads/{filename}"

    # Auto-save jabatan into jabatan_struktural if new
    if jabatan:
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO jabatan_struktural (nama_jabatan, urutan) VALUES (?, 99)", (jabatan.strip(),))
            conn.commit()
            conn.close()
        except Exception:
            pass

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO perangkat_desa (nama, jabatan, periode, foto, kontak, sambutan_singkat, urutan)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nama, jabatan, periode, foto, kontak, sambutan, urutan))
    conn.commit()
    conn.close()

    flash('Aparatur desa berhasil ditambahkan.', 'success')
    return redirect(url_for('admin_aparatur'))

@app.route('/admin/aparatur/<int:id>/edit', methods=['POST'])
@login_required
def admin_edit_aparatur(id):
    nama = request.form.get('nama')
    jabatan = request.form.get('jabatan')
    periode = request.form.get('periode') or '2021 - 2027'
    kontak = request.form.get('kontak')
    sambutan = request.form.get('sambutan_singkat')
    urutan = int(request.form.get('urutan') or 0)

    # Ambil foto lama atau fallback
    foto = request.form.get('foto_lama') or request.form.get('foto')
    if 'foto_file' in request.files:
        file = request.files['foto_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                filename = secure_filename(f"aparatur_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                foto = f"static/images/uploads/{filename}"

    # Auto-save jabatan into jabatan_struktural if new
    if jabatan:
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO jabatan_struktural (nama_jabatan, urutan) VALUES (?, 99)", (jabatan.strip(),))
            conn.commit()
            conn.close()
        except Exception:
            pass

    conn = get_db()
    cursor = conn.cursor()
    if not foto:
        cursor.execute("SELECT foto FROM perangkat_desa WHERE id = ?", (id,))
        row = cursor.fetchone()
        foto = row['foto'] if row and row['foto'] else 'static/images/kades.jpg'

    cursor.execute('''
    UPDATE perangkat_desa SET nama=?, jabatan=?, periode=?, foto=?, kontak=?, sambutan_singkat=?, urutan=?
    WHERE id=?
    ''', (nama, jabatan, periode, foto, kontak, sambutan, urutan, id))

    # Jika yang di-edit adalah Kepala Desa, sinkronkan ke profil_desa
    if jabatan and ('kepala desa' in jabatan.lower() or 'kuwu' in jabatan.lower() or 'pembekal' in jabatan.lower()):
        cursor.execute('''
        UPDATE profil_desa SET nama_kades=?, foto_kades=?, periode_kades=? WHERE id=1
        ''', (nama, foto, periode))

    conn.commit()
    conn.close()

    flash('Data aparatur desa berhasil diperbarui.', 'success')
    return redirect(url_for('admin_aparatur'))

@app.route('/admin/aparatur/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_aparatur(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM perangkat_desa WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Aparatur desa berhasil dihapus.', 'info')
    return redirect(url_for('admin_aparatur'))


# ========================================================
# MANAJEMEN SEJARAH DESA (CRUD & TAYANG / DRAF)
# ========================================================
@app.route('/admin/aparatur/sejarah/tambah', methods=['POST'])
@login_required
def admin_tambah_sejarah():
    judul = (request.form.get('judul') or 'Sejarah Desa').strip()
    periode_era = (request.form.get('periode_era') or '').strip()
    konten = (request.form.get('konten') or '').strip()
    urutan = int(request.form.get('urutan') or 1)
    status = request.form.get('status') or 'Tayang'

    foto = (request.form.get('foto') or '').strip() or 'static/images/banner1.png'
    if 'foto_file' in request.files:
        file = request.files['foto_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                filename = secure_filename(f"sejarah_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                foto = f"static/images/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO sejarah_desa (judul, periode_era, konten, foto, urutan, status)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (judul, periode_era, konten, foto, urutan, status))
    conn.commit()
    conn.close()

    try:
        record_activity_log('TAMBAH_SEJARAH', f"Menambahkan bab/sejarah desa: {judul}")
    except Exception:
        pass

    flash(f'Bab Sejarah "{judul}" berhasil disimpan.', 'success')
    return redirect(url_for('admin_aparatur') + '#tab-sejarah')

@app.route('/admin/aparatur/sejarah/<int:id>/edit', methods=['POST'])
@login_required
def admin_edit_sejarah(id):
    judul = (request.form.get('judul') or 'Sejarah Desa').strip()
    periode_era = (request.form.get('periode_era') or '').strip()
    konten = (request.form.get('konten') or '').strip()
    urutan = int(request.form.get('urutan') or 1)
    status = request.form.get('status') or 'Tayang'

    foto = request.form.get('foto_lama') or request.form.get('foto')
    if 'foto_file' in request.files:
        file = request.files['foto_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                filename = secure_filename(f"sejarah_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                foto = f"static/images/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    if not foto:
        cursor.execute("SELECT foto FROM sejarah_desa WHERE id = ?", (id,))
        row = cursor.fetchone()
        foto = row['foto'] if row and row['foto'] else 'static/images/banner1.png'

    cursor.execute('''
    UPDATE sejarah_desa 
    SET judul = ?, periode_era = ?, konten = ?, foto = ?, urutan = ?, status = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (judul, periode_era, konten, foto, urutan, status, id))
    conn.commit()
    conn.close()

    try:
        record_activity_log('EDIT_SEJARAH', f"Memperbarui bab sejarah: {judul}")
    except Exception:
        pass

    flash('Data Sejarah Desa berhasil diperbarui.', 'success')
    return redirect(url_for('admin_aparatur') + '#tab-sejarah')

@app.route('/admin/aparatur/sejarah/<int:id>/toggle-status', methods=['POST'])
@login_required
def admin_toggle_status_sejarah(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status, judul FROM sejarah_desa WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        curr = row['status']
        new_status = 'Draf' if curr == 'Tayang' else 'Tayang'
        cursor.execute("UPDATE sejarah_desa SET status = ? WHERE id = ?", (new_status, id))
        conn.commit()
        flash(f'Status "{row["judul"]}" berhasil diubah menjadi {new_status}.', 'success')
    conn.close()
    return redirect(url_for('admin_aparatur') + '#tab-sejarah')

@app.route('/admin/aparatur/sejarah/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_sejarah(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sejarah_desa WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    try:
        record_activity_log('HAPUS_SEJARAH', f"Menghapus data sejarah ID #{id}")
    except Exception:
        pass
    flash('Data Sejarah Desa berhasil dihapus.', 'info')
    return redirect(url_for('admin_aparatur') + '#tab-sejarah')


# ========================================================
# MANAJEMEN KEPALA DESA DARI MASA KE MASA
# ========================================================
@app.route('/admin/aparatur/kades-riwayat/tambah', methods=['POST'])
@login_required
def admin_tambah_kades_riwayat():
    nama = (request.form.get('nama') or '').strip()
    periode = (request.form.get('periode') or '').strip()
    tahun_mulai = int(request.form.get('tahun_mulai') or 2021)
    tahun_selesai_val = request.form.get('tahun_selesai')
    tahun_selesai = int(tahun_selesai_val) if tahun_selesai_val and tahun_selesai_val.strip().isdigit() else None
    status_jabatan = request.form.get('status_jabatan') or 'Lampau'
    keterangan = (request.form.get('keterangan') or '').strip()
    urutan = int(request.form.get('urutan') or 1)
    status = request.form.get('status') or 'Tayang'

    foto = (request.form.get('foto') or '').strip() or 'static/images/kades.jpg'
    if 'foto_file' in request.files:
        file = request.files['foto_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                filename = secure_filename(f"kades_riwayat_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                foto = f"static/images/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO kades_masa_ke_masa (nama, periode, tahun_mulai, tahun_selesai, status_jabatan, foto, keterangan, urutan, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nama, periode, tahun_mulai, tahun_selesai, status_jabatan, foto, keterangan, urutan, status))
    conn.commit()
    conn.close()

    try:
        record_activity_log('TAMBAH_KADES_RIWAYAT', f"Menambahkan riwayat Kepala Desa: {nama} ({periode})")
    except Exception:
        pass

    flash(f'Kepala Desa "{nama}" ({periode}) berhasil ditambahkan.', 'success')
    return redirect(url_for('admin_aparatur') + '#tab-kades')

@app.route('/admin/aparatur/kades-riwayat/<int:id>/edit', methods=['POST'])
@login_required
def admin_edit_kades_riwayat(id):
    nama = (request.form.get('nama') or '').strip()
    periode = (request.form.get('periode') or '').strip()
    tahun_mulai = int(request.form.get('tahun_mulai') or 2021)
    tahun_selesai_val = request.form.get('tahun_selesai')
    tahun_selesai = int(tahun_selesai_val) if tahun_selesai_val and tahun_selesai_val.strip().isdigit() else None
    status_jabatan = request.form.get('status_jabatan') or 'Lampau'
    keterangan = (request.form.get('keterangan') or '').strip()
    urutan = int(request.form.get('urutan') or 1)
    status = request.form.get('status') or 'Tayang'

    foto = request.form.get('foto_lama') or request.form.get('foto')
    if 'foto_file' in request.files:
        file = request.files['foto_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                filename = secure_filename(f"kades_riwayat_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                foto = f"static/images/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()
    if not foto:
        cursor.execute("SELECT foto FROM kades_masa_ke_masa WHERE id = ?", (id,))
        row = cursor.fetchone()
        foto = row['foto'] if row and row['foto'] else 'static/images/kades.jpg'

    cursor.execute('''
    UPDATE kades_masa_ke_masa 
    SET nama = ?, periode = ?, tahun_mulai = ?, tahun_selesai = ?, status_jabatan = ?, foto = ?, keterangan = ?, urutan = ?, status = ?
    WHERE id = ?
    ''', (nama, periode, tahun_mulai, tahun_selesai, status_jabatan, foto, keterangan, urutan, status, id))
    conn.commit()
    conn.close()

    try:
        record_activity_log('EDIT_KADES_RIWAYAT', f"Memperbarui riwayat Kepala Desa: {nama}")
    except Exception:
        pass

    flash(f'Data Kepala Desa "{nama}" berhasil diperbarui.', 'success')
    return redirect(url_for('admin_aparatur') + '#tab-kades')

@app.route('/admin/aparatur/kades-riwayat/<int:id>/toggle-status', methods=['POST'])
@login_required
def admin_toggle_status_kades_riwayat(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status, nama FROM kades_masa_ke_masa WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        curr = row['status']
        new_status = 'Draf' if curr == 'Tayang' else 'Tayang'
        cursor.execute("UPDATE kades_masa_ke_masa SET status = ? WHERE id = ?", (new_status, id))
        conn.commit()
        flash(f'Status Kepala Desa "{row["nama"]}" berhasil diubah menjadi {new_status}.', 'success')
    conn.close()
    return redirect(url_for('admin_aparatur') + '#tab-kades')

@app.route('/admin/aparatur/kades-riwayat/<int:id>/hapus', methods=['POST'])
@login_required
def admin_hapus_kades_riwayat(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kades_masa_ke_masa WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    try:
        record_activity_log('HAPUS_KADES_RIWAYAT', f"Menghapus Kepala Desa Riwayat ID #{id}")
    except Exception:
        pass
    flash('Data riwayat Kepala Desa berhasil dihapus.', 'info')
    return redirect(url_for('admin_aparatur') + '#tab-kades')

# --- 7. KELOLA STATISTIK & APBDES (DINAMIS SERIES & TEMPLATE UPLOAD/DOWNLOAD) ---
@app.route('/admin/statistik', methods=['GET', 'POST'])
@login_required
def admin_statistik():
    conn = get_db()
    cursor = conn.cursor()

    # Dapatkan daftar tahun yang tersedia dari seluruh tabel statistik
    cursor.execute("""
        SELECT DISTINCT tahun FROM statistik_sls 
        UNION 
        SELECT DISTINCT tahun FROM statistik_umur
        UNION 
        SELECT DISTINCT tahun FROM statistik_pendidikan
        UNION 
        SELECT DISTINCT tahun FROM statistik_perkawinan
        UNION 
        SELECT DISTINCT tahun FROM statistik_pencatatan_nikah
        UNION 
        SELECT DISTINCT tahun FROM statistik_agama
        UNION 
        SELECT DISTINCT tahun FROM statistik_bansos
        UNION 
        SELECT DISTINCT tahun FROM statistik_anak
        UNION 
        SELECT DISTINCT tahun FROM statistik_gizi_buruk
        UNION 
        SELECT DISTINCT tahun FROM statistik_stunting
        UNION 
        SELECT DISTINCT tahun FROM statistik 
        ORDER BY tahun DESC
    """)
    tahun_rows = cursor.fetchall()
    tahun_list = [row[0] for row in tahun_rows if row[0]]
    if not tahun_list:
        tahun_list = [2026]

    selected_tahun = request.args.get('tahun', type=int)
    if selected_tahun and selected_tahun >= 2000 and selected_tahun <= 2100:
        if selected_tahun not in tahun_list:
            tahun_list.append(selected_tahun)
            tahun_list.sort(reverse=True)
    else:
        selected_tahun = tahun_list[0]

    if request.method == 'POST':
        form_tahun = int(request.form.get('tahun') or selected_tahun)

        # Update APBDes
        apbdes_tahun = int(request.form.get('apbdes_tahun') or form_tahun)
        pendapatan = int(request.form.get('apbdes_pendapatan') or 0)
        belanja = int(request.form.get('apbdes_belanja') or 0)
        pembiayaan = int(request.form.get('apbdes_pembiayaan') or 0)

        cursor.execute('''
            UPDATE apbdes 
            SET tahun=?, pendapatan_total=?, belanja_total=?, pembiayaan_netto=?
            WHERE id = 1
        ''', (apbdes_tahun, pendapatan, belanja, pembiayaan))

        conn.commit()
        tab_kembali = request.form.get('tab', 'apbdes')
        flash('Data transparansi APBDes berhasil diperbarui.', 'success')
        conn.close()
        return redirect(url_for('admin_statistik', tahun=form_tahun, tab=tab_kembali))

    # Ambil data statistik untuk tahun terpilih
    cursor.execute("SELECT * FROM statistik WHERE tahun = ? ORDER BY id ASC LIMIT 1", (selected_tahun,))
    stat_row = cursor.fetchone()
    if not stat_row:
        cursor.execute("SELECT * FROM statistik WHERE id = 1")
        stat_row = cursor.fetchone()
    stat = dict(stat_row or {})

    # Ambil data APBDes
    cursor.execute("SELECT * FROM apbdes WHERE id = 1")
    apbdes = dict(cursor.fetchone() or {})

    # Ambil daftar data SLS (RT/RW) untuk tahun terpilih
    cursor.execute("SELECT * FROM statistik_sls WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (selected_tahun,))
    sls_list = [dict(row) for row in cursor.fetchall()]

    # Hitung ringkasan total SLS
    total_sls_laki = sum(s.get('laki_laki', 0) for s in sls_list)
    total_sls_perempuan = sum(s.get('perempuan', 0) for s in sls_list)
    total_sls_total = sum(s.get('total', 0) for s in sls_list)
    total_sls_keluarga = sum(s.get('keluarga', 0) for s in sls_list)
    total_sls_count = len(sls_list)

    if total_sls_total == 0 and (total_sls_laki + total_sls_perempuan) > 0:
        total_sls_total = total_sls_laki + total_sls_perempuan

    sex_ratio = round((total_sls_laki / total_sls_perempuan * 100), 1) if total_sls_perempuan > 0 else 0
    persen_laki = round((total_sls_laki / total_sls_total * 100), 1) if total_sls_total > 0 else 50.0
    persen_perempuan = round((total_sls_perempuan / total_sls_total * 100), 1) if total_sls_total > 0 else 50.0

    sls_summary = {
        'total_laki': total_sls_laki,
        'total_perempuan': total_sls_perempuan,
        'total_jiwa': total_sls_total,
        'total_keluarga': total_sls_keluarga,
        'count_sls': total_sls_count,
        'sex_ratio': sex_ratio,
        'persen_laki': persen_laki,
        'persen_perempuan': persen_perempuan
    }

    # Ambil daftar data Kelompok Umur (Piramida Penduduk) untuk tahun terpilih
    cursor.execute("SELECT * FROM statistik_umur WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (selected_tahun,))
    umur_list = [dict(row) for row in cursor.fetchall()]

    # Hitung ringkasan kelompok umur (Demographic Cohorts)
    tot_u_laki = sum(u.get('laki_laki', 0) for u in umur_list)
    tot_u_perempuan = sum(u.get('perempuan', 0) for u in umur_list)
    tot_u_total = sum(u.get('total', 0) for u in umur_list)

    # 1. Usia Muda (0-14 th): 0-4, 5-9, 10-14
    muda_l = sum(u.get('laki_laki', 0) for u in umur_list if any(k in u.get('kelompok_umur', '') for k in ['0 - 4', '5 - 9', '10 - 14']))
    muda_p = sum(u.get('perempuan', 0) for u in umur_list if any(k in u.get('kelompok_umur', '') for k in ['0 - 4', '5 - 9', '10 - 14']))
    total_muda = muda_l + muda_p

    # 2. Usia Lansia (65+ th): 65-69, 70-74, 75+
    tua_l = sum(u.get('laki_laki', 0) for u in umur_list if any(k in u.get('kelompok_umur', '') for k in ['65 - 69', '70 - 74', '75+']))
    tua_p = sum(u.get('perempuan', 0) for u in umur_list if any(k in u.get('kelompok_umur', '') for k in ['65 - 69', '70 - 74', '75+']))
    total_tua = tua_l + tua_p

    # 3. Usia Produktif (15-64 th): total - muda - tua
    total_produktif = max(0, tot_u_total - total_muda - total_tua)
    produktif_l = max(0, tot_u_laki - muda_l - tua_l)
    produktif_p = max(0, tot_u_perempuan - muda_p - tua_p)

    dep_ratio = round(((total_muda + total_tua) / total_produktif * 100), 1) if total_produktif > 0 else 0
    persen_produktif = round((total_produktif / tot_u_total * 100), 1) if tot_u_total > 0 else 0
    persen_muda = round((total_muda / tot_u_total * 100), 1) if tot_u_total > 0 else 0
    persen_tua = round((total_tua / tot_u_total * 100), 1) if tot_u_total > 0 else 0

    umur_summary = {
        'total_laki': tot_u_laki,
        'total_perempuan': tot_u_perempuan,
        'total_jiwa': tot_u_total,
        'total_muda': total_muda,
        'persen_muda': persen_muda,
        'total_produktif': total_produktif,
        'persen_produktif': persen_produktif,
        'total_tua': total_tua,
        'persen_tua': persen_tua,
        'dependency_ratio': dep_ratio,
        'count_kategori': len(umur_list)
    }

    # Ambil daftar data Pendidikan Penduduk per SLS untuk tahun terpilih
    cursor.execute("SELECT * FROM statistik_pendidikan WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (selected_tahun,))
    pendidikan_list = [dict(row) for row in cursor.fetchall()]

    # Hitung ringkasan statistik pendidikan
    pend_col_totals = {}
    for col_key, _ in PENDIDIKAN_COLUMNS:
        pend_col_totals[col_key] = sum(p.get(col_key, 0) for p in pendidikan_list)

    total_pendidikan_jiwa = sum(p.get('jumlah', 0) for p in pendidikan_list)
    if total_pendidikan_jiwa == 0 and pendidikan_list:
        total_pendidikan_jiwa = sum(sum(p.get(c[0], 0) for c in PENDIDIKAN_COLUMNS) for p in pendidikan_list)

    tot_tidak_sd = pend_col_totals.get('tidak_sekolah', 0)
    tot_sd = sum(pend_col_totals.get(c, 0) for c in ['sd', 'mi', 'paket_a', 'sdlb', 'spm_ula'])
    tot_smp = sum(pend_col_totals.get(c, 0) for c in ['smp', 'mts', 'smp_lb', 'paket_b', 'spm_wustha'])
    tot_sma = sum(pend_col_totals.get(c, 0) for c in ['sma', 'smk', 'ma', 'mak', 'sma_lb', 'paket_c', 'spm_ulya'])
    tot_pt = sum(pend_col_totals.get(c, 0) for c in ['diploma', 's1', 'profesi', 's2', 's3'])

    pendidikan_summary = {
        'col_totals': pend_col_totals,
        'total_jiwa': total_pendidikan_jiwa,
        'tot_tidak_sd': tot_tidak_sd,
        'tot_sd': tot_sd,
        'tot_smp': tot_smp,
        'tot_sma': tot_sma,
        'tot_pt': tot_pt,
        'persen_tidak_sd': round((tot_tidak_sd / total_pendidikan_jiwa * 100), 1) if total_pendidikan_jiwa > 0 else 0,
        'persen_sd': round((tot_sd / total_pendidikan_jiwa * 100), 1) if total_pendidikan_jiwa > 0 else 0,
        'persen_smp': round((tot_smp / total_pendidikan_jiwa * 100), 1) if total_pendidikan_jiwa > 0 else 0,
        'persen_sma': round((tot_sma / total_pendidikan_jiwa * 100), 1) if total_pendidikan_jiwa > 0 else 0,
        'persen_pt': round((tot_pt / total_pendidikan_jiwa * 100), 1) if total_pendidikan_jiwa > 0 else 0,
    }

    # Ambil daftar data Status Perkawinan per SLS untuk tahun terpilih
    cursor.execute("SELECT * FROM statistik_perkawinan WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (selected_tahun,))
    perkawinan_list = [dict(row) for row in cursor.fetchall()]

    tot_bk = sum(p.get('belum_kawin', 0) for p in perkawinan_list)
    tot_k = sum(p.get('kawin', 0) for p in perkawinan_list)
    tot_ch = sum(p.get('cerai_hidup', 0) for p in perkawinan_list)
    tot_cm = sum(p.get('cerai_mati', 0) for p in perkawinan_list)
    tot_perk = sum(p.get('total', 0) for p in perkawinan_list)
    if tot_perk == 0 and (tot_bk + tot_k + tot_ch + tot_cm) > 0:
        tot_perk = tot_bk + tot_k + tot_ch + tot_cm

    perkawinan_summary = {
        'total_belum_kawin': tot_bk,
        'total_kawin': tot_k,
        'total_cerai_hidup': tot_ch,
        'total_cerai_mati': tot_cm,
        'total_jiwa': tot_perk,
        'persen_belum_kawin': round((tot_bk / tot_perk * 100), 1) if tot_perk > 0 else 0,
        'persen_kawin': round((tot_k / tot_perk * 100), 1) if tot_perk > 0 else 0,
        'persen_cerai_hidup': round((tot_ch / tot_perk * 100), 1) if tot_perk > 0 else 0,
        'persen_cerai_mati': round((tot_cm / tot_perk * 100), 1) if tot_perk > 0 else 0,
    }

    # Ambil daftar data Pencatatan Perkawinan per SLS untuk tahun terpilih
    cursor.execute("SELECT * FROM statistik_pencatatan_nikah WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (selected_tahun,))
    pencatatan_nikah_list = [dict(row) for row in cursor.fetchall()]

    tot_kt = sum(n.get('kawin_tercatat', 0) for n in pencatatan_nikah_list)
    tot_kbt = sum(n.get('kawin_belum_tercatat', 0) for n in pencatatan_nikah_list)
    tot_ktt = sum(n.get('kawin_tidak_tercatat', 0) for n in pencatatan_nikah_list)
    tot_penc = sum(n.get('total', 0) for n in pencatatan_nikah_list)
    if tot_penc == 0 and (tot_kt + tot_kbt + tot_ktt) > 0:
        tot_penc = tot_kt + tot_kbt + tot_ktt

    pencatatan_nikah_summary = {
        'total_kawin_tercatat': tot_kt,
        'total_kawin_belum_tercatat': tot_kbt,
        'total_kawin_tidak_tercatat': tot_ktt,
        'total_jiwa': tot_penc,
        'persen_tercatat': round((tot_kt / tot_penc * 100), 1) if tot_penc > 0 else 0,
        'persen_belum_tercatat': round((tot_kbt / tot_penc * 100), 1) if tot_penc > 0 else 0,
        'persen_tidak_tercatat': round((tot_ktt / tot_penc * 100), 1) if tot_penc > 0 else 0,
    }

    # Ambil daftar data Agama per SLS untuk tahun terpilih
    cursor.execute("SELECT * FROM statistik_agama WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (selected_tahun,))
    agama_list = [dict(row) for row in cursor.fetchall()]

    tot_isl = sum(a.get('islam', 0) for a in agama_list)
    tot_krs = sum(a.get('kristen', 0) for a in agama_list)
    tot_kat = sum(a.get('katholik', 0) for a in agama_list)
    tot_bud = sum(a.get('budha', 0) for a in agama_list)
    tot_hin = sum(a.get('hindu', 0) for a in agama_list)
    tot_khg = sum(a.get('konghucu', 0) for a in agama_list)
    tot_kep = sum(a.get('kepercayaan_lainnya', 0) for a in agama_list)
    tot_agm = sum(a.get('total', 0) for a in agama_list)
    if tot_agm == 0 and (tot_isl + tot_krs + tot_kat + tot_bud + tot_hin + tot_khg + tot_kep) > 0:
        tot_agm = tot_isl + tot_krs + tot_kat + tot_bud + tot_hin + tot_khg + tot_kep

    agama_summary = {
        'total_islam': tot_isl,
        'total_kristen': tot_krs,
        'total_katholik': tot_kat,
        'total_budha': tot_bud,
        'total_hindu': tot_hin,
        'total_konghucu': tot_khg,
        'total_kepercayaan_lainnya': tot_kep,
        'total_jiwa': tot_agm,
        'persen_islam': round((tot_isl / tot_agm * 100), 1) if tot_agm > 0 else 0,
        'persen_kristen': round((tot_krs / tot_agm * 100), 1) if tot_agm > 0 else 0,
        'persen_katholik': round((tot_kat / tot_agm * 100), 1) if tot_agm > 0 else 0,
        'persen_budha': round((tot_bud / tot_agm * 100), 1) if tot_agm > 0 else 0,
        'persen_hindu': round((tot_hin / tot_agm * 100), 1) if tot_agm > 0 else 0,
        'persen_konghucu': round((tot_khg / tot_agm * 100), 1) if tot_agm > 0 else 0,
        'persen_kepercayaan_lainnya': round((tot_kep / tot_agm * 100), 1) if tot_agm > 0 else 0,
    }

    # Ambil daftar data Bantuan Sosial per SLS untuk tahun terpilih
    cursor.execute("SELECT * FROM statistik_bansos WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (selected_tahun,))
    bansos_list = [dict(row) for row in cursor.fetchall()]

    tot_pkh = sum(b.get('pkh', 0) for b in bansos_list)
    tot_bpnt = sum(b.get('bpnt', 0) for b in bansos_list)
    tot_bos = sum(b.get('bos', 0) for b in bansos_list)
    tot_bap = sum(b.get('bapanas', 0) for b in bansos_list)
    tot_stun = sum(b.get('stunting', 0) for b in bansos_list)
    tot_pbi = sum(b.get('pbi_jkn', 0) for b in bansos_list)
    tot_blt = sum(b.get('blt', 0) for b in bansos_list)
    tot_bldd = sum(b.get('blt_dd', 0) for b in bansos_list)
    tot_lain = sum(b.get('lainnya', 0) for b in bansos_list)
    tot_bns_all = sum(b.get('total', 0) for b in bansos_list)
    if tot_bns_all == 0 and (tot_pkh + tot_bpnt + tot_bos + tot_bap + tot_stun + tot_pbi + tot_blt + tot_bldd + tot_lain) > 0:
        tot_bns_all = tot_pkh + tot_bpnt + tot_bos + tot_bap + tot_stun + tot_pbi + tot_blt + tot_bldd + tot_lain

    bansos_summary = {
        'total_pkh': tot_pkh,
        'total_bpnt': tot_bpnt,
        'total_bos': tot_bos,
        'total_bapanas': tot_bap,
        'total_stunting': tot_stun,
        'total_pbi_jkn': tot_pbi,
        'total_blt': tot_blt,
        'total_blt_dd': tot_bldd,
        'total_lainnya': tot_lain,
        'total_semua': tot_bns_all,
        'persen_pkh': round((tot_pkh / tot_bns_all * 100), 1) if tot_bns_all > 0 else 0,
        'persen_bpnt': round((tot_bpnt / tot_bns_all * 100), 1) if tot_bns_all > 0 else 0,
        'persen_pbi_jkn': round((tot_pbi / tot_bns_all * 100), 1) if tot_bns_all > 0 else 0,
        'persen_blt_dd': round((tot_bldd / tot_bns_all * 100), 1) if tot_bns_all > 0 else 0,
    }

    # Ambil data Status Keberadaan Orang Tua Anak (Yatim / Piatu)
    cursor.execute("SELECT * FROM statistik_anak WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (selected_tahun,))
    anak_list = [dict(row) for row in cursor.fetchall()]
    tot_anak_yatim = sum(a.get('anak_yatim', 0) for a in anak_list)
    tot_anak_piatu = sum(a.get('anak_piatu', 0) for a in anak_list)
    tot_yatim_piatu = sum(a.get('yatim_piatu', 0) for a in anak_list)
    tot_orang_tua_lengkap = sum(a.get('orang_tua_lengkap', 0) for a in anak_list)
    tot_anak_all = sum(a.get('total_anak', 0) for a in anak_list)
    if tot_anak_all == 0 and (tot_anak_yatim + tot_anak_piatu + tot_yatim_piatu + tot_orang_tua_lengkap) > 0:
        tot_anak_all = tot_anak_yatim + tot_anak_piatu + tot_yatim_piatu + tot_orang_tua_lengkap

    anak_summary = {
        'total_yatim': tot_anak_yatim,
        'total_piatu': tot_anak_piatu,
        'total_yatim_piatu': tot_yatim_piatu,
        'total_lengkap': tot_orang_tua_lengkap,
        'total_semua': tot_anak_all,
        'persen_yatim': round((tot_anak_yatim / tot_anak_all * 100), 1) if tot_anak_all > 0 else 0,
        'persen_piatu': round((tot_anak_piatu / tot_anak_all * 100), 1) if tot_anak_all > 0 else 0,
        'persen_yatim_piatu': round((tot_yatim_piatu / tot_anak_all * 100), 1) if tot_anak_all > 0 else 0,
        'persen_lengkap': round((tot_orang_tua_lengkap / tot_anak_all * 100), 1) if tot_anak_all > 0 else 0,
    }

    # Ambil data Anak Gizi Buruk
    cursor.execute("SELECT * FROM statistik_gizi_buruk WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (selected_tahun,))
    gizi_buruk_list = [dict(row) for row in cursor.fetchall()]
    tot_gizi_buruk = sum(g.get('anak_gizi_buruk', 0) for g in gizi_buruk_list)
    tot_balita_gz = sum(g.get('jumlah_anak_balita', 0) for g in gizi_buruk_list)
    persen_gz = round(tot_gizi_buruk / tot_balita_gz * 100, 1) if tot_balita_gz > 0 else 0
    gizi_buruk_summary = {
        'total_gizi_buruk': tot_gizi_buruk,
        'total_balita': tot_balita_gz,
        'persen_desa': persen_gz,
        'total_sls_terdampak': sum(1 for g in gizi_buruk_list if g.get('anak_gizi_buruk', 0) > 0)
    }

    # Ambil data Anak Stunting
    cursor.execute("SELECT * FROM statistik_stunting WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (selected_tahun,))
    stunting_list = [dict(row) for row in cursor.fetchall()]
    tot_stunting = sum(s.get('anak_stunting', 0) for s in stunting_list)
    tot_balita_st = sum(s.get('jumlah_anak_balita', 0) for s in stunting_list)
    persen_st = round(tot_stunting / tot_balita_st * 100, 1) if tot_balita_st > 0 else 0
    stunting_summary = {
        'total_stunting': tot_stunting,
        'total_balita': tot_balita_st,
        'persen_desa': persen_st,
        'total_sls_terdampak': sum(1 for s in stunting_list if s.get('anak_stunting', 0) > 0)
    }

    # Ambil data series pertahun (rekapitulasi makro)
    cursor.execute("SELECT id, tahun, total_penduduk, laki_laki, perempuan, kepala_keluarga FROM statistik ORDER BY tahun ASC")
    statistik_series = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template(
        'admin/statistik.html',
        stat=stat,
        apbdes=apbdes,
        sls_list=sls_list,
        sls_summary=sls_summary,
        umur_list=umur_list,
        umur_summary=umur_summary,
        pendidikan_list=pendidikan_list,
        pendidikan_summary=pendidikan_summary,
        pendidikan_columns=PENDIDIKAN_COLUMNS,
        perkawinan_list=perkawinan_list,
        perkawinan_summary=perkawinan_summary,
        pencatatan_nikah_list=pencatatan_nikah_list,
        pencatatan_nikah_summary=pencatatan_nikah_summary,
        agama_list=agama_list,
        agama_summary=agama_summary,
        agama_columns=AGAMA_COLUMNS,
        bansos_list=bansos_list,
        bansos_summary=bansos_summary,
        bansos_columns=BANSOS_COLUMNS,
        anak_list=anak_list,
        anak_summary=anak_summary,
        anak_columns=ANAK_COLUMNS,
        gizi_buruk_list=gizi_buruk_list,
        gizi_buruk_summary=gizi_buruk_summary,
        gizi_buruk_columns=GIZI_BURUK_COLUMNS,
        stunting_list=stunting_list,
        stunting_summary=stunting_summary,
        stunting_columns=STUNTING_COLUMNS,
        tahun_list=tahun_list,
        selected_tahun=selected_tahun,
        statistik_series=statistik_series
    )


@app.route('/admin/statistik/template')
@login_required
def admin_statistik_template():
    """Unduh template upload data statistik SLS (.xlsx atau .csv)"""
    file_format = request.args.get('format', 'xlsx').lower()
    template_type = request.args.get('type', 'contoh').lower() # 'contoh' atau 'kosong'
    include_sample = (template_type != 'kosong')

    if file_format == 'csv':
        buf = generate_template_csv(include_sample=include_sample)
        filename = f"Template_Statistik_Kependudukan_SLS_Desa_{'Sample' if include_sample else 'Kosong'}.csv"
        return send_file(
            buf,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    else:
        buf = generate_template_excel(include_sample=include_sample)
        filename = f"Template_Statistik_Kependudukan_SLS_Desa_{'Sample' if include_sample else 'Kosong'}.xlsx"
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )


@app.route('/admin/statistik/export')
@login_required
def admin_statistik_export():
    """Ekspor data statistik SLS tahun berjalan ke file Excel (.xlsx) atau CSV"""
    tahun = request.args.get('tahun', type=int) or 2026
    file_format = request.args.get('format', 'xlsx').lower()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM statistik_sls WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (tahun,))
    sls_rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if file_format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["No.", "Nama SLS", "Laki - Laki", "Perempuan", "Total", "Keluarga"])
        for r in sls_rows:
            writer.writerow([
                r.get('no_urut', ''),
                r.get('nama_sls', ''),
                r.get('laki_laki', 0),
                r.get('perempuan', 0),
                r.get('total', 0),
                r.get('keluarga', 0)
            ])
        if sls_rows:
            tot_l = sum(r.get('laki_laki', 0) for r in sls_rows)
            tot_p = sum(r.get('perempuan', 0) for r in sls_rows)
            tot_j = sum(r.get('total', 0) for r in sls_rows)
            tot_k = sum(r.get('keluarga', 0) for r in sls_rows)
            writer.writerow(["TOTAL", "", tot_l, tot_p, tot_j, tot_k])
        
        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8-sig'))
        mem.seek(0)
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"Data_Statistik_Kependudukan_SLS_{tahun}.csv"
        )
    else:
        buf = export_sls_excel(sls_rows, tahun)
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"Data_Statistik_Kependudukan_SLS_{tahun}.xlsx"
        )


@app.route('/admin/statistik/upload', methods=['POST'])
@login_required
def admin_statistik_upload():
    """Memproses unggahan file template Excel / CSV statistik SLS tahunan"""
    if 'file_statistik' not in request.files:
        flash('Tidak ada file yang dipilih untuk diunggah.', 'danger')
        return redirect(url_for('admin_statistik'))

    file = request.files['file_statistik']
    if not file or file.filename == '':
        flash('Harap pilih file Excel (.xlsx) atau CSV (.csv).', 'warning')
        return redirect(url_for('admin_statistik'))

    tahun = int(request.form.get('tahun') or 2026)
    mode = request.form.get('mode', 'replace') # 'replace' atau 'append'
    sync_agregat = request.form.get('sync_agregat', '1') in ['1', 'on', 'true', True]

    parsed_data, error_msg = parse_uploaded_sls_file(file)
    if error_msg:
        flash(f'Gagal memproses file: {error_msg}', 'danger')
        return redirect(url_for('admin_statistik', tahun=tahun))

    conn = get_db()
    cursor = conn.cursor()

    if mode == 'replace':
        cursor.execute("DELETE FROM statistik_sls WHERE tahun = ?", (tahun,))

    for item in parsed_data:
        cursor.execute('''
            INSERT INTO statistik_sls (tahun, no_urut, nama_sls, laki_laki, perempuan, total, keluarga)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            tahun,
            item.get('no_urut'),
            item.get('nama_sls'),
            item.get('laki_laki', 0),
            item.get('perempuan', 0),
            item.get('total', 0),
            item.get('keluarga', 0)
        ))

    conn.commit()

    if sync_agregat:
        count_sls, sum_laki, sum_perempuan, sum_total, sum_kk = sync_aggregate_statistics(conn, tahun)
        flash(
            f'Berhasil mengimpor {len(parsed_data)} data SLS untuk Tahun {tahun}! '
            f'Total {sum_total:,} jiwa ({sum_laki:,} Laki-laki, {sum_perempuan:,} Perempuan, {sum_kk:,} KK) '
            f'otomatis disinkronkan ke infografis kependudukan desa.',
            'success'
        )
    else:
        flash(f'Berhasil mengimpor {len(parsed_data)} data SLS untuk Tahun {tahun}.', 'success')

    conn.close()
    return redirect(url_for('admin_statistik', tahun=tahun, tab='sls'))


@app.route('/admin/statistik/sls/tambah', methods=['POST'])
@login_required
def admin_statistik_sls_tambah():
    """Menambahkan satu baris data SLS secara manual"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()
    laki = int(request.form.get('laki_laki') or 0)
    perempuan = int(request.form.get('perempuan') or 0)
    total = int(request.form.get('total') or (laki + perempuan))
    keluarga = int(request.form.get('keluarga') or 0)

    if not nama_sls:
        flash('Nama SLS / Wilayah RT-RW wajib diisi.', 'danger')
        return redirect(url_for('admin_statistik', tahun=tahun, tab='sls'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO statistik_sls (tahun, no_urut, nama_sls, laki_laki, perempuan, total, keluarga)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (tahun, no_urut, nama_sls, laki, perempuan, total, keluarga))
    conn.commit()

    sync_aggregate_statistics(conn, tahun)
    conn.close()

    flash(f'Data SLS "{nama_sls}" berhasil ditambahkan dan total kependudukan telah disinkronkan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='sls'))


@app.route('/admin/statistik/sls/<int:id>/edit', methods=['POST'])
@login_required
def admin_statistik_sls_edit(id):
    """Mengubah data SLS"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()
    laki = int(request.form.get('laki_laki') or 0)
    perempuan = int(request.form.get('perempuan') or 0)
    total = int(request.form.get('total') or (laki + perempuan))
    keluarga = int(request.form.get('keluarga') or 0)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE statistik_sls 
        SET no_urut = ?, nama_sls = ?, laki_laki = ?, perempuan = ?, total = ?, keluarga = ?
        WHERE id = ?
    ''', (no_urut, nama_sls, laki, perempuan, total, keluarga, id))
    conn.commit()

    sync_aggregate_statistics(conn, tahun)
    conn.close()

    flash(f'Perubahan data SLS "{nama_sls}" berhasil disimpan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='sls'))


@app.route('/admin/statistik/sls/<int:id>/hapus', methods=['POST'])
@login_required
def admin_statistik_sls_hapus(id):
    """Menghapus satu data SLS"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tahun, nama_sls FROM statistik_sls WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        tahun, nama_sls = row
        cursor.execute("DELETE FROM statistik_sls WHERE id = ?", (id,))
        conn.commit()
        sync_aggregate_statistics(conn, tahun)
        flash(f'Data SLS "{nama_sls}" berhasil dihapus.', 'info')
    else:
        tahun = 2026

    conn.close()
    return redirect(url_for('admin_statistik', tahun=tahun, tab='sls'))


@app.route('/admin/statistik/sls/<int:tahun>/reset', methods=['POST'])
@login_required
def admin_statistik_sls_reset(tahun):
    """Mereset/mengosongkan seluruh data SLS pada tahun tertentu"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM statistik_sls WHERE tahun = ?", (tahun,))
    conn.commit()
    sync_aggregate_statistics(conn, tahun)
    conn.close()

    flash(f'Seluruh data SLS untuk Tahun {tahun} telah berhasil dikosongkan.', 'warning')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='sls'))


@app.route('/admin/statistik/tahun-baru', methods=['POST'])
@login_required
def admin_statistik_tahun_baru():
    """Membuat periode tahun series baru untuk data statistik desa, piramida penduduk & SLS"""
    tahun = request.form.get('tahun', type=int)
    opsi = request.form.get('opsi', 'duplikasi') # 'duplikasi' atau 'kosong'
    tab = request.form.get('tab', 'umur')

    if not tahun or tahun < 2000 or tahun > 2100:
        flash('Silakan masukkan tahun yang valid (antara 2000 s/d 2100).', 'danger')
        return redirect(url_for('admin_statistik', tab=tab))

    conn = get_db()
    cursor = conn.cursor()

    # Periksa apakah tahun ini sudah terdata di salah satu tabel
    cursor.execute("SELECT COUNT(*) FROM statistik_umur WHERE tahun = ?", (tahun,))
    count_u = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM statistik_sls WHERE tahun = ?", (tahun,))
    count_s = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM statistik_pendidikan WHERE tahun = ?", (tahun,))
    count_p = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM statistik_perkawinan WHERE tahun = ?", (tahun,))
    count_perk = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM statistik_pencatatan_nikah WHERE tahun = ?", (tahun,))
    count_penc = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM statistik_agama WHERE tahun = ?", (tahun,))
    count_agm = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM statistik_bansos WHERE tahun = ?", (tahun,))
    count_bns = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM statistik_anak WHERE tahun = ?", (tahun,))
    count_anak = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM statistik_gizi_buruk WHERE tahun = ?", (tahun,))
    count_gizi = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM statistik_stunting WHERE tahun = ?", (tahun,))
    count_stunt = cursor.fetchone()[0]

    if count_u > 0 or count_s > 0 or count_p > 0 or count_perk > 0 or count_penc > 0 or count_agm > 0 or count_bns > 0 or count_anak > 0 or count_gizi > 0 or count_stunt > 0:
        conn.close()
        flash(f'Tahun {tahun} sudah ada di dalam sistem. Data untuk tahun {tahun} kini ditampilkan.', 'info')
        return redirect(url_for('admin_statistik', tahun=tahun, tab=tab))

    if opsi == 'duplikasi':
        # Cari tahun sumber terdekat (tahun terbaru yang ada datanya)
        cursor.execute("SELECT DISTINCT tahun FROM statistik_umur ORDER BY tahun DESC LIMIT 1")
        row_src_u = cursor.fetchone()
        src_tahun_u = row_src_u[0] if row_src_u else 2026

        cursor.execute("SELECT DISTINCT tahun FROM statistik_sls ORDER BY tahun DESC LIMIT 1")
        row_src_s = cursor.fetchone()
        src_tahun_s = row_src_s[0] if row_src_s else 2026

        cursor.execute("SELECT DISTINCT tahun FROM statistik_pendidikan ORDER BY tahun DESC LIMIT 1")
        row_src_p = cursor.fetchone()
        src_tahun_p = row_src_p[0] if row_src_p else 2026

        cursor.execute("SELECT DISTINCT tahun FROM statistik_perkawinan ORDER BY tahun DESC LIMIT 1")
        row_src_perk = cursor.fetchone()
        src_tahun_perk = row_src_perk[0] if row_src_perk else 2026

        cursor.execute("SELECT DISTINCT tahun FROM statistik_pencatatan_nikah ORDER BY tahun DESC LIMIT 1")
        row_src_penc = cursor.fetchone()
        src_tahun_penc = row_src_penc[0] if row_src_penc else 2026

        cursor.execute("SELECT DISTINCT tahun FROM statistik_agama ORDER BY tahun DESC LIMIT 1")
        row_src_agm = cursor.fetchone()
        src_tahun_agm = row_src_agm[0] if row_src_agm else 2026

        cursor.execute("SELECT DISTINCT tahun FROM statistik_bansos ORDER BY tahun DESC LIMIT 1")
        row_src_bns = cursor.fetchone()
        src_tahun_bns = row_src_bns[0] if row_src_bns else 2026

        cursor.execute("SELECT DISTINCT tahun FROM statistik_anak ORDER BY tahun DESC LIMIT 1")
        row_src_anak = cursor.fetchone()
        src_tahun_anak = row_src_anak[0] if row_src_anak else 2026

        cursor.execute("SELECT DISTINCT tahun FROM statistik_gizi_buruk ORDER BY tahun DESC LIMIT 1")
        row_src_gizi = cursor.fetchone()
        src_tahun_gizi = row_src_gizi[0] if row_src_gizi else 2026

        cursor.execute("SELECT DISTINCT tahun FROM statistik_stunting ORDER BY tahun DESC LIMIT 1")
        row_src_stunt = cursor.fetchone()
        src_tahun_stunt = row_src_stunt[0] if row_src_stunt else 2026

        # Salin struktur 16 kelompok umur (nilai awal 0)
        cursor.execute("SELECT no_urut, kelompok_umur FROM statistik_umur WHERE tahun = ? ORDER BY no_urut ASC", (src_tahun_u,))
        umur_src = cursor.fetchall()
        for u in umur_src:
            cursor.execute('''
                INSERT INTO statistik_umur (tahun, no_urut, kelompok_umur, laki_laki, perempuan, total)
                VALUES (?, ?, ?, 0, 0, 0)
            ''', (tahun, u[0], u[1]))

        # Salin struktur 26 SLS RT/RW (nilai awal 0)
        cursor.execute("SELECT no_urut, nama_sls FROM statistik_sls WHERE tahun = ? ORDER BY no_urut ASC", (src_tahun_s,))
        sls_src = cursor.fetchall()
        for s in sls_src:
            cursor.execute('''
                INSERT INTO statistik_sls (tahun, no_urut, nama_sls, laki_laki, perempuan, total, keluarga)
                VALUES (?, ?, ?, 0, 0, 0, 0)
            ''', (tahun, s[0], s[1]))

        # Salin struktur 26 SLS Pendidikan (nilai awal 0)
        cursor.execute("SELECT no_urut, nama_sls FROM statistik_pendidikan WHERE tahun = ? ORDER BY no_urut ASC", (src_tahun_p,))
        pen_src = cursor.fetchall()
        for p in pen_src:
            cursor.execute('''
                INSERT INTO statistik_pendidikan (
                    tahun, no_urut, nama_sls, tidak_sekolah, sd, mi, paket_a, sdlb, spm_ula,
                    smp, mts, smp_lb, paket_b, spm_wustha, sma, smk, ma, mak, sma_lb, paket_c,
                    spm_ulya, diploma, s1, profesi, s2, s3, jumlah
                )
                VALUES (?, ?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            ''', (tahun, p[0], p[1]))

        # Salin struktur 26 SLS Status Perkawinan (nilai awal 0)
        cursor.execute("SELECT no_urut, nama_sls FROM statistik_perkawinan WHERE tahun = ? ORDER BY no_urut ASC", (src_tahun_perk,))
        perk_src = cursor.fetchall()
        for pk in perk_src:
            cursor.execute('''
                INSERT INTO statistik_perkawinan (
                    tahun, no_urut, nama_sls, belum_kawin, kawin, cerai_hidup, cerai_mati, total
                )
                VALUES (?, ?, ?, 0, 0, 0, 0, 0)
            ''', (tahun, pk[0], pk[1]))

        # Salin struktur 26 SLS Pencatatan Perkawinan (nilai awal 0)
        cursor.execute("SELECT no_urut, nama_sls FROM statistik_pencatatan_nikah WHERE tahun = ? ORDER BY no_urut ASC", (src_tahun_penc,))
        penc_src = cursor.fetchall()
        for pn in penc_src:
            cursor.execute('''
                INSERT INTO statistik_pencatatan_nikah (
                    tahun, no_urut, nama_sls, kawin_tercatat, kawin_belum_tercatat, kawin_tidak_tercatat, total
                )
                VALUES (?, ?, ?, 0, 0, 0, 0)
            ''', (tahun, pn[0], pn[1]))

        # Salin struktur 26 SLS Agama dan Kepercayaan (nilai awal 0)
        cursor.execute("SELECT no_urut, nama_sls FROM statistik_agama WHERE tahun = ? ORDER BY no_urut ASC", (src_tahun_agm,))
        agm_src = cursor.fetchall()
        for ag in agm_src:
            cursor.execute('''
                INSERT INTO statistik_agama (
                    tahun, no_urut, nama_sls, islam, kristen, katholik, budha, hindu, konghucu, kepercayaan_lainnya, total
                )
                VALUES (?, ?, ?, 0, 0, 0, 0, 0, 0, 0, 0)
            ''', (tahun, ag[0], ag[1]))

        # Salin struktur 26 SLS Bantuan Sosial (nilai awal 0)
        cursor.execute("SELECT no_urut, nama_sls FROM statistik_bansos WHERE tahun = ? ORDER BY no_urut ASC", (src_tahun_bns,))
        bns_src = cursor.fetchall()
        for bs in bns_src:
            cursor.execute('''
                INSERT INTO statistik_bansos (
                    tahun, no_urut, nama_sls, pkh, bpnt, bos, bapanas, stunting, pbi_jkn, blt, blt_dd, lainnya, total
                )
                VALUES (?, ?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            ''', (tahun, bs[0], bs[1]))

        # Salin struktur 26 SLS Status Anak Yatim/Piatu (nilai awal 0)
        cursor.execute("SELECT no_urut, nama_sls FROM statistik_anak WHERE tahun = ? ORDER BY no_urut ASC", (src_tahun_anak,))
        anak_src = cursor.fetchall()
        for ak in anak_src:
            cursor.execute('''
                INSERT INTO statistik_anak (
                    tahun, no_urut, nama_sls, anak_yatim, anak_piatu, yatim_piatu, orang_tua_lengkap, total_anak
                )
                VALUES (?, ?, ?, 0, 0, 0, 0, 0)
            ''', (tahun, ak[0], ak[1]))

        # Salin struktur 26 SLS Gizi Buruk (nilai awal 0)
        cursor.execute("SELECT no_urut, nama_sls FROM statistik_gizi_buruk WHERE tahun = ? ORDER BY no_urut ASC", (src_tahun_gizi,))
        gizi_src = cursor.fetchall()
        for gz in gizi_src:
            cursor.execute('''
                INSERT INTO statistik_gizi_buruk (
                    tahun, no_urut, nama_sls, anak_gizi_buruk, jumlah_anak_balita, persentase
                )
                VALUES (?, ?, ?, 0, 0, 0.0)
            ''', (tahun, gz[0], gz[1]))

        # Salin struktur 26 SLS Stunting (nilai awal 0)
        cursor.execute("SELECT no_urut, nama_sls FROM statistik_stunting WHERE tahun = ? ORDER BY no_urut ASC", (src_tahun_stunt,))
        stunt_src = cursor.fetchall()
        for st in stunt_src:
            cursor.execute('''
                INSERT INTO statistik_stunting (
                    tahun, no_urut, nama_sls, anak_stunting, jumlah_anak_balita, persentase
                )
                VALUES (?, ?, ?, 0, 0, 0.0)
            ''', (tahun, st[0], st[1]))

        # Inisialisasi statistik kependudukan untuk tahun baru
        cursor.execute('''
            INSERT INTO statistik (tahun, total_penduduk, laki_laki, perempuan, kepala_keluarga, penduduk_sementara, mutasi_penduduk)
            VALUES (?, 0, 0, 0, 0, 0, 0)
        ''', (tahun,))

        conn.commit()
        conn.close()
        flash(
            f'Seri Tahun Baru {tahun} berhasil dibuat! Struktur 16 Kelompok Umur, 26 SLS RT/RW, Data Pendidikan, Status Perkawinan, Pencatatan Nikah, Agama, Bantuan Sosial, serta Status Anak Yatim/Gizi Buruk/Stunting telah disiapkan (nilai di-reset ke 0). '
            f'Anda dapat langsung mengisi angka di tabel atau mengunduh template Excel tahun {tahun}.',
            'success'
        )
    else:
        # Opsi Kosong
        cursor.execute('''
            INSERT INTO statistik (tahun, total_penduduk, laki_laki, perempuan, kepala_keluarga, penduduk_sementara, mutasi_penduduk)
            VALUES (?, 0, 0, 0, 0, 0, 0)
        ''', (tahun,))
        conn.commit()
        conn.close()
        flash(f'Seri Tahun Baru {tahun} siap digunakan dalam keadaan kosong. Silakan unggah file template Excel / CSV atau tambahkan data.', 'success')

    return redirect(url_for('admin_statistik', tahun=tahun, tab=tab))


# --- 7a. ROUTE DATA SERIES TAHUNAN KEPENDUDUKAN (REKAPITULASI MAKRO) ---

@app.route('/api/statistik/series')
def api_statistik_series():
    """Endpoint API publik untuk data series kependudukan tahunan"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, tahun, total_penduduk, laki_laki, perempuan, kepala_keluarga FROM statistik ORDER BY tahun ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({'success': True, 'series': rows})


@app.route('/admin/statistik/series/tambah', methods=['POST'])
@login_required
def admin_statistik_series_tambah():
    """Tambah baris data series tahun baru secara langsung"""
    tahun = request.form.get('tahun', type=int)
    tot = int(request.form.get('total_penduduk') or 0)
    laki = int(request.form.get('laki_laki') or 0)
    perempuan = int(request.form.get('perempuan') or 0)
    kk = int(request.form.get('kepala_keluarga') or 0)
    if tot == 0 and (laki + perempuan) > 0:
        tot = laki + perempuan

    if not tahun or tahun < 2000 or tahun > 2100:
        flash('Silakan masukkan tahun yang valid.', 'danger')
        return redirect(url_for('admin_statistik', tab='series'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM statistik WHERE tahun = ?", (tahun,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("""
            UPDATE statistik SET total_penduduk=?, laki_laki=?, perempuan=?, kepala_keluarga=? WHERE id=?
        """, (tot, laki, perempuan, kk, existing[0]))
    else:
        cursor.execute("""
            INSERT INTO statistik (tahun, total_penduduk, laki_laki, perempuan, kepala_keluarga, penduduk_sementara, mutasi_penduduk)
            VALUES (?, ?, ?, ?, ?, 0, 0)
        """, (tahun, tot, laki, perempuan, kk))
    conn.commit()
    conn.close()
    flash(f'Data series tahun {tahun} berhasil disimpan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='series'))


@app.route('/admin/statistik/series/<int:id>/edit', methods=['POST'])
@login_required
def admin_statistik_series_edit(id):
    """Edit data series tahunan"""
    tahun = request.form.get('tahun', type=int)
    tot = int(request.form.get('total_penduduk') or 0)
    laki = int(request.form.get('laki_laki') or 0)
    perempuan = int(request.form.get('perempuan') or 0)
    kk = int(request.form.get('kepala_keluarga') or 0)
    if tot == 0 and (laki + perempuan) > 0:
        tot = laki + perempuan

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE statistik SET tahun=?, total_penduduk=?, laki_laki=?, perempuan=?, kepala_keluarga=? WHERE id=?
    """, (tahun, tot, laki, perempuan, kk, id))
    conn.commit()
    conn.close()
    flash(f'Data series kependudukan tahun {tahun} berhasil diperbarui.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='series'))


@app.route('/admin/statistik/series/<int:id>/hapus', methods=['POST'])
@login_required
def admin_statistik_series_hapus(id):
    """Hapus data series tahunan"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tahun FROM statistik WHERE id=?", (id,))
    row = cursor.fetchone()
    th = row[0] if row else ''
    cursor.execute("DELETE FROM statistik WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash(f'Data series tahun {th} telah dihapus.', 'warning')
    return redirect(url_for('admin_statistik', tab='series'))


@app.route('/admin/statistik/series/<int:tahun>/sync', methods=['POST'])
@login_required
def admin_statistik_series_sync(tahun):
    """Sinkronkan data series makro dari akumulasi tabel SLS tahun bersangkutan"""
    conn = get_db()
    sync_aggregate_statistics(conn, tahun)
    conn.close()
    flash(f'Data series tahun {tahun} berhasil dihitung dan disinkronkan otomatis dari data SLS.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='series'))


# --- 7b. ROUTE DATA KELOMPOK UMUR & PIRAMIDA PENDUDUK ---

@app.route('/admin/statistik/umur/template')
@login_required
def admin_statistik_umur_template():
    """Unduh template upload data kelompok umur piramida penduduk (.xlsx atau .csv)"""
    file_format = request.args.get('format', 'xlsx').lower()
    template_type = request.args.get('type', 'contoh').lower()
    include_sample = (template_type != 'kosong')

    if file_format == 'csv':
        buf = generate_template_umur_csv(include_sample=include_sample)
        filename = f"Template_Kelompok_Umur_Piramida_Desa_{'Sample' if include_sample else 'Kosong'}.csv"
        return send_file(
            buf,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    else:
        buf = generate_template_umur_excel(include_sample=include_sample)
        filename = f"Template_Kelompok_Umur_Piramida_Desa_{'Sample' if include_sample else 'Kosong'}.xlsx"
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )


@app.route('/admin/statistik/umur/export')
@login_required
def admin_statistik_umur_export():
    """Ekspor data kelompok umur tahun berjalan ke file Excel (.xlsx) atau CSV"""
    tahun = request.args.get('tahun', type=int) or 2026
    file_format = request.args.get('format', 'xlsx').lower()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM statistik_umur WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (tahun,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if file_format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["No.", "Kelompok Umur", "Laki-laki", "Perempuan", "Total"])
        for r in rows:
            writer.writerow([
                r.get('no_urut', ''),
                r.get('kelompok_umur', ''),
                r.get('laki_laki', 0),
                r.get('perempuan', 0),
                r.get('total', 0)
            ])
        if rows:
            tot_l = sum(r.get('laki_laki', 0) for r in rows)
            tot_p = sum(r.get('perempuan', 0) for r in rows)
            tot_j = sum(r.get('total', 0) for r in rows)
            writer.writerow(["TOTAL", "", tot_l, tot_p, tot_j])

        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8-sig'))
        mem.seek(0)
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"Data_Kelompok_Umur_{tahun}.csv"
        )
    else:
        buf = export_umur_excel(rows, tahun)
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"Data_Kelompok_Umur_{tahun}.xlsx"
        )


@app.route('/admin/statistik/umur/upload', methods=['POST'])
@login_required
def admin_statistik_umur_upload():
    """Memproses unggahan file Excel/CSV data kelompok umur untuk piramida penduduk"""
    if 'file_umur' not in request.files:
        flash('Tidak ada file kelompok umur yang dipilih.', 'danger')
        return redirect(url_for('admin_statistik', tab='umur'))

    file = request.files['file_umur']
    if not file or file.filename == '':
        flash('Harap pilih file Excel (.xlsx) atau CSV (.csv).', 'warning')
        return redirect(url_for('admin_statistik', tab='umur'))

    tahun = int(request.form.get('tahun') or 2026)
    mode = request.form.get('mode', 'replace')

    parsed_data, error_msg = parse_uploaded_umur_file(file)
    if error_msg:
        flash(f'Gagal memproses file kelompok umur: {error_msg}', 'danger')
        return redirect(url_for('admin_statistik', tahun=tahun, tab='umur'))

    conn = get_db()
    cursor = conn.cursor()

    if mode == 'replace':
        cursor.execute("DELETE FROM statistik_umur WHERE tahun = ?", (tahun,))

    for item in parsed_data:
        cursor.execute('''
            INSERT INTO statistik_umur (tahun, no_urut, kelompok_umur, laki_laki, perempuan, total)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            tahun,
            item.get('no_urut'),
            item.get('kelompok_umur'),
            item.get('laki_laki', 0),
            item.get('perempuan', 0),
            item.get('total', 0)
        ))

    conn.commit()

    count_rows, sum_l, sum_p, sum_tot = sync_aggregate_umur(conn, tahun)
    conn.close()

    flash(
        f'Berhasil mengimpor {len(parsed_data)} kategori kelompok umur untuk Tahun {tahun}! '
        f'Piramida penduduk ({sum_tot:,} jiwa: {sum_l:,} Laki-laki, {sum_p:,} Perempuan) otomatis diperbarui.',
        'success'
    )
    return redirect(url_for('admin_statistik', tahun=tahun, tab='umur'))


@app.route('/admin/statistik/umur/tambah', methods=['POST'])
@login_required
def admin_statistik_umur_tambah():
    """Menambahkan satu baris kategori kelompok umur"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    kelompok_umur = request.form.get('kelompok_umur', '').strip()
    laki = int(request.form.get('laki_laki') or 0)
    perempuan = int(request.form.get('perempuan') or 0)
    total = int(request.form.get('total') or (laki + perempuan))

    if not kelompok_umur:
        flash('Rentang kelompok umur wajib diisi.', 'danger')
        return redirect(url_for('admin_statistik', tahun=tahun, tab='umur'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO statistik_umur (tahun, no_urut, kelompok_umur, laki_laki, perempuan, total)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (tahun, no_urut, kelompok_umur, laki, perempuan, total))
    conn.commit()

    sync_aggregate_umur(conn, tahun)
    conn.close()

    flash(f'Kelompok umur "{kelompok_umur}" berhasil ditambahkan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='umur'))


@app.route('/admin/statistik/umur/<int:id>/edit', methods=['POST'])
@login_required
def admin_statistik_umur_edit(id):
    """Mengubah data kelompok umur"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    kelompok_umur = request.form.get('kelompok_umur', '').strip()
    laki = int(request.form.get('laki_laki') or 0)
    perempuan = int(request.form.get('perempuan') or 0)
    total = int(request.form.get('total') or (laki + perempuan))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE statistik_umur
        SET no_urut = ?, kelompok_umur = ?, laki_laki = ?, perempuan = ?, total = ?
        WHERE id = ?
    ''', (no_urut, kelompok_umur, laki, perempuan, total, id))
    conn.commit()

    sync_aggregate_umur(conn, tahun)
    conn.close()

    flash(f'Perubahan kelompok umur "{kelompok_umur}" berhasil disimpan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='umur'))


@app.route('/admin/statistik/umur/<int:id>/hapus', methods=['POST'])
@login_required
def admin_statistik_umur_hapus(id):
    """Menghapus satu data kelompok umur"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tahun, kelompok_umur FROM statistik_umur WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        tahun, kelompok_umur = row
        cursor.execute("DELETE FROM statistik_umur WHERE id = ?", (id,))
        conn.commit()
        sync_aggregate_umur(conn, tahun)
        flash(f'Kelompok umur "{kelompok_umur}" berhasil dihapus.', 'info')
    else:
        tahun = 2026

    conn.close()
    return redirect(url_for('admin_statistik', tahun=tahun, tab='umur'))


@app.route('/admin/statistik/umur/<int:tahun>/reset', methods=['POST'])
@login_required
def admin_statistik_umur_reset(tahun):
    """Mereset/mengosongkan data kelompok umur tahun tertentu"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM statistik_umur WHERE tahun = ?", (tahun,))
    conn.commit()
    sync_aggregate_umur(conn, tahun)
    conn.close()

    flash(f'Seluruh data kelompok umur untuk Tahun {tahun} berhasil dikosongkan.', 'warning')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='umur'))


# --- 7c. ROUTE DATA TINGKAT PENDIDIKAN PENDUDUK PER SLS (RT/RW) ---

@app.route('/admin/statistik/pendidikan/template')
@login_required
def admin_statistik_pendidikan_template():
    """Unduh template upload data tingkat pendidikan per SLS (.xlsx atau .csv)"""
    file_format = request.args.get('format', 'xlsx').lower()
    template_type = request.args.get('type', 'contoh').lower()
    include_sample = (template_type != 'kosong')

    if file_format == 'csv':
        buf = generate_template_pendidikan_csv(include_sample=include_sample)
        filename = f"Template_Pendidikan_Penduduk_SLS_Desa_{'Sample' if include_sample else 'Kosong'}.csv"
        return send_file(
            buf,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    else:
        buf = generate_template_pendidikan_excel(include_sample=include_sample)
        filename = f"Template_Pendidikan_Penduduk_SLS_Desa_{'Sample' if include_sample else 'Kosong'}.xlsx"
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )


@app.route('/admin/statistik/pendidikan/export')
@login_required
def admin_statistik_pendidikan_export():
    """Ekspor data tingkat pendidikan per SLS tahun tertentu ke file Excel (.xlsx) atau CSV"""
    tahun = request.args.get('tahun', type=int) or 2026
    file_format = request.args.get('format', 'xlsx').lower()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM statistik_pendidikan WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (tahun,))
    pen_rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if file_format == 'csv':
        import io, csv
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        headers = ["No.", "Nama SLS"] + [col[1] for col in PENDIDIKAN_COLUMNS] + ["Jumlah"]
        writer.writerow(headers)
        for r in pen_rows:
            vals = [r.get(c[0], 0) for c in PENDIDIKAN_COLUMNS]
            writer.writerow([r.get('no_urut', ''), r.get('nama_sls', '')] + vals + [r.get('jumlah', sum(vals))])
        if pen_rows:
            tot_cells = ["Total", ""]
            for c in PENDIDIKAN_COLUMNS:
                tot_cells.append(sum(r.get(c[0], 0) for r in pen_rows))
            tot_cells.append(sum(r.get('jumlah', 0) for r in pen_rows))
            writer.writerow(tot_cells)

        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8-sig'))
        mem.seek(0)
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"Data_Pendidikan_Penduduk_SLS_{tahun}.csv"
        )
    else:
        buf = export_pendidikan_excel(pen_rows, tahun)
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"Data_Pendidikan_Penduduk_SLS_{tahun}.xlsx"
        )


@app.route('/admin/statistik/pendidikan/upload', methods=['POST'])
@login_required
def admin_statistik_pendidikan_upload():
    """Memproses unggahan file Excel/CSV data tingkat pendidikan penduduk per SLS"""
    if 'file_pendidikan' not in request.files:
        flash('Tidak ada file yang dipilih untuk diunggah.', 'danger')
        return redirect(url_for('admin_statistik', tab='pendidikan'))

    file = request.files['file_pendidikan']
    if not file or file.filename == '':
        flash('Harap pilih file Excel (.xlsx) atau CSV (.csv).', 'warning')
        return redirect(url_for('admin_statistik', tab='pendidikan'))

    tahun = int(request.form.get('tahun') or 2026)
    mode = request.form.get('mode', 'replace')

    parsed_data, error_msg = parse_uploaded_pendidikan_file(file)
    if error_msg:
        flash(f'Gagal memproses file: {error_msg}', 'danger')
        return redirect(url_for('admin_statistik', tahun=tahun, tab='pendidikan'))

    conn = get_db()
    cursor = conn.cursor()

    if mode == 'replace':
        cursor.execute("DELETE FROM statistik_pendidikan WHERE tahun = ?", (tahun,))

    for item in parsed_data:
        cursor.execute('''
            INSERT INTO statistik_pendidikan (
                tahun, no_urut, nama_sls, tidak_sekolah, sd, mi, paket_a, sdlb, spm_ula,
                smp, mts, smp_lb, paket_b, spm_wustha, sma, smk, ma, mak, sma_lb, paket_c,
                spm_ulya, diploma, s1, profesi, s2, s3, jumlah
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tahun,
            item.get('no_urut'),
            item.get('nama_sls'),
            item.get('tidak_sekolah', 0),
            item.get('sd', 0),
            item.get('mi', 0),
            item.get('paket_a', 0),
            item.get('sdlb', 0),
            item.get('spm_ula', 0),
            item.get('smp', 0),
            item.get('mts', 0),
            item.get('smp_lb', 0),
            item.get('paket_b', 0),
            item.get('spm_wustha', 0),
            item.get('sma', 0),
            item.get('smk', 0),
            item.get('ma', 0),
            item.get('mak', 0),
            item.get('sma_lb', 0),
            item.get('paket_c', 0),
            item.get('spm_ulya', 0),
            item.get('diploma', 0),
            item.get('s1', 0),
            item.get('profesi', 0),
            item.get('s2', 0),
            item.get('s3', 0),
            item.get('jumlah', 0)
        ))

    conn.commit()
    conn.close()

    total_jiwa = sum(it.get('jumlah', 0) for it in parsed_data)
    flash(
        f'Berhasil mengimpor data pendidikan untuk {len(parsed_data)} SLS pada Tahun {tahun}! '
        f'Total {total_jiwa:,} jiwa terdata.',
        'success'
    )
    return redirect(url_for('admin_statistik', tahun=tahun, tab='pendidikan'))


@app.route('/admin/statistik/pendidikan/tambah', methods=['POST'])
@login_required
def admin_statistik_pendidikan_tambah():
    """Menambahkan satu baris data pendidikan per SLS secara manual"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()

    if not nama_sls:
        flash('Nama SLS / Wilayah RT-RW wajib diisi.', 'danger')
        return redirect(url_for('admin_statistik', tahun=tahun, tab='pendidikan'))

    cols_vals = {}
    row_sum = 0
    for col_key, _ in PENDIDIKAN_COLUMNS:
        v = int(request.form.get(col_key) or 0)
        cols_vals[col_key] = max(0, v)
        row_sum += max(0, v)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO statistik_pendidikan (
            tahun, no_urut, nama_sls, tidak_sekolah, sd, mi, paket_a, sdlb, spm_ula,
            smp, mts, smp_lb, paket_b, spm_wustha, sma, smk, ma, mak, sma_lb, paket_c,
            spm_ulya, diploma, s1, profesi, s2, s3, jumlah
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        tahun, no_urut, nama_sls,
        cols_vals['tidak_sekolah'], cols_vals['sd'], cols_vals['mi'], cols_vals['paket_a'], cols_vals['sdlb'], cols_vals['spm_ula'],
        cols_vals['smp'], cols_vals['mts'], cols_vals['smp_lb'], cols_vals['paket_b'], cols_vals['spm_wustha'],
        cols_vals['sma'], cols_vals['smk'], cols_vals['ma'], cols_vals['mak'], cols_vals['sma_lb'], cols_vals['paket_c'],
        cols_vals['spm_ulya'], cols_vals['diploma'], cols_vals['s1'], cols_vals['profesi'], cols_vals['s2'], cols_vals['s3'],
        row_sum
    ))
    conn.commit()
    conn.close()

    flash(f'Data pendidikan SLS "{nama_sls}" berhasil ditambahkan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='pendidikan'))


@app.route('/admin/statistik/pendidikan/<int:id>/edit', methods=['POST'])
@login_required
def admin_statistik_pendidikan_edit(id):
    """Mengubah satu baris data pendidikan per SLS"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()

    cols_vals = {}
    row_sum = 0
    for col_key, _ in PENDIDIKAN_COLUMNS:
        v = int(request.form.get(col_key) or 0)
        cols_vals[col_key] = max(0, v)
        row_sum += max(0, v)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE statistik_pendidikan
        SET no_urut = ?, nama_sls = ?,
            tidak_sekolah = ?, sd = ?, mi = ?, paket_a = ?, sdlb = ?, spm_ula = ?,
            smp = ?, mts = ?, smp_lb = ?, paket_b = ?, spm_wustha = ?,
            sma = ?, smk = ?, ma = ?, mak = ?, sma_lb = ?, paket_c = ?,
            spm_ulya = ?, diploma = ?, s1 = ?, profesi = ?, s2 = ?, s3 = ?,
            jumlah = ?
        WHERE id = ?
    ''', (
        no_urut, nama_sls,
        cols_vals['tidak_sekolah'], cols_vals['sd'], cols_vals['mi'], cols_vals['paket_a'], cols_vals['sdlb'], cols_vals['spm_ula'],
        cols_vals['smp'], cols_vals['mts'], cols_vals['smp_lb'], cols_vals['paket_b'], cols_vals['spm_wustha'],
        cols_vals['sma'], cols_vals['smk'], cols_vals['ma'], cols_vals['mak'], cols_vals['sma_lb'], cols_vals['paket_c'],
        cols_vals['spm_ulya'], cols_vals['diploma'], cols_vals['s1'], cols_vals['profesi'], cols_vals['s2'], cols_vals['s3'],
        row_sum, id
    ))
    conn.commit()
    conn.close()

    flash(f'Perubahan data pendidikan SLS "{nama_sls}" berhasil disimpan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='pendidikan'))


@app.route('/admin/statistik/pendidikan/<int:id>/hapus', methods=['POST'])
@login_required
def admin_statistik_pendidikan_hapus(id):
    """Menghapus satu data pendidikan SLS"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tahun, nama_sls FROM statistik_pendidikan WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        tahun, nama_sls = row
        cursor.execute("DELETE FROM statistik_pendidikan WHERE id = ?", (id,))
        conn.commit()
        flash(f'Data pendidikan SLS "{nama_sls}" berhasil dihapus.', 'info')
    else:
        tahun = 2026

    conn.close()
    return redirect(url_for('admin_statistik', tahun=tahun, tab='pendidikan'))


@app.route('/admin/statistik/pendidikan/<int:tahun>/reset', methods=['POST'])
@login_required
def admin_statistik_pendidikan_reset(tahun):
    """Mereset seluruh data pendidikan pada tahun tertentu"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM statistik_pendidikan WHERE tahun = ?", (tahun,))
    conn.commit()
    conn.close()

    flash(f'Seluruh data tingkat pendidikan untuk Tahun {tahun} berhasil dikosongkan.', 'warning')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='pendidikan'))


# --- 7d. ROUTE DATA STATUS PERKAWINAN PER SLS (RT/RW) ---

@app.route('/admin/statistik/perkawinan/template')
@login_required
def admin_statistik_perkawinan_template():
    """Unduh template upload data status perkawinan per SLS (.xlsx atau .csv)"""
    file_format = request.args.get('format', 'xlsx').lower()
    template_type = request.args.get('type', 'contoh').lower()
    include_sample = (template_type != 'kosong')

    if file_format == 'csv':
        buf = generate_template_perkawinan_csv(include_sample=include_sample)
        filename = f"Template_Status_Perkawinan_SLS_Desa_{'Sample' if include_sample else 'Kosong'}.csv"
        return send_file(
            buf,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    else:
        buf = generate_template_perkawinan_excel(include_sample=include_sample)
        filename = f"Template_Status_Perkawinan_SLS_Desa_{'Sample' if include_sample else 'Kosong'}.xlsx"
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )


@app.route('/admin/statistik/perkawinan/export')
@login_required
def admin_statistik_perkawinan_export():
    """Ekspor data status perkawinan per SLS tahun tertentu ke file Excel (.xlsx) atau CSV"""
    tahun = request.args.get('tahun', type=int) or 2026
    file_format = request.args.get('format', 'xlsx').lower()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM statistik_perkawinan WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (tahun,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if file_format == 'csv':
        buf = export_perkawinan_csv(rows, tahun)
        return send_file(
            buf,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"Data_Status_Perkawinan_SLS_{tahun}.csv"
        )
    else:
        buf = export_perkawinan_excel(rows, tahun)
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"Data_Status_Perkawinan_SLS_{tahun}.xlsx"
        )


@app.route('/admin/statistik/perkawinan/upload', methods=['POST'])
@login_required
def admin_statistik_perkawinan_upload():
    """Memproses unggahan file Excel/CSV data status perkawinan per SLS"""
    if 'file_perkawinan' not in request.files:
        flash('Tidak ada file yang dipilih untuk diunggah.', 'danger')
        return redirect(url_for('admin_statistik', tab='perkawinan'))

    file = request.files['file_perkawinan']
    if not file or file.filename == '':
        flash('Harap pilih file Excel (.xlsx) atau CSV (.csv).', 'warning')
        return redirect(url_for('admin_statistik', tab='perkawinan'))

    tahun = int(request.form.get('tahun') or 2026)
    mode = request.form.get('mode', 'replace')

    parsed_data, error_msg = parse_uploaded_perkawinan_file(file)
    if error_msg:
        flash(f'Gagal memproses file: {error_msg}', 'danger')
        return redirect(url_for('admin_statistik', tahun=tahun, tab='perkawinan'))

    conn = get_db()
    cursor = conn.cursor()

    if mode == 'replace':
        cursor.execute("DELETE FROM statistik_perkawinan WHERE tahun = ?", (tahun,))

    for item in parsed_data:
        cursor.execute('''
            INSERT INTO statistik_perkawinan (
                tahun, no_urut, nama_sls, belum_kawin, kawin, cerai_hidup, cerai_mati, total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tahun,
            item.get('no_urut'),
            item.get('nama_sls'),
            item.get('belum_kawin', 0),
            item.get('kawin', 0),
            item.get('cerai_hidup', 0),
            item.get('cerai_mati', 0),
            item.get('total', 0)
        ))

    conn.commit()
    conn.close()

    total_jiwa = sum(it.get('total', 0) for it in parsed_data)
    flash(
        f'Berhasil mengimpor data status perkawinan untuk {len(parsed_data)} SLS pada Tahun {tahun}! '
        f'Total tercatat: {total_jiwa:,} jiwa.',
        'success'
    )
    return redirect(url_for('admin_statistik', tahun=tahun, tab='perkawinan'))


@app.route('/admin/statistik/perkawinan/tambah', methods=['POST'])
@login_required
def admin_statistik_perkawinan_tambah():
    """Menambahkan baris data status perkawinan SLS baru secara manual"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()
    belum_kawin = max(0, int(request.form.get('belum_kawin') or 0))
    kawin = max(0, int(request.form.get('kawin') or 0))
    cerai_hidup = max(0, int(request.form.get('cerai_hidup') or 0))
    cerai_mati = max(0, int(request.form.get('cerai_mati') or 0))
    total = belum_kawin + kawin + cerai_hidup + cerai_mati

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO statistik_perkawinan (
            tahun, no_urut, nama_sls, belum_kawin, kawin, cerai_hidup, cerai_mati, total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tahun, no_urut, nama_sls, belum_kawin, kawin, cerai_hidup, cerai_mati, total))
    conn.commit()
    conn.close()

    flash(f'Data status perkawinan SLS "{nama_sls}" berhasil ditambahkan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='perkawinan'))


@app.route('/admin/statistik/perkawinan/<int:id>/edit', methods=['POST'])
@login_required
def admin_statistik_perkawinan_edit(id):
    """Mengubah satu baris data status perkawinan per SLS"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()
    belum_kawin = max(0, int(request.form.get('belum_kawin') or 0))
    kawin = max(0, int(request.form.get('kawin') or 0))
    cerai_hidup = max(0, int(request.form.get('cerai_hidup') or 0))
    cerai_mati = max(0, int(request.form.get('cerai_mati') or 0))
    total = belum_kawin + kawin + cerai_hidup + cerai_mati

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE statistik_perkawinan SET
            no_urut=?, nama_sls=?, belum_kawin=?, kawin=?, cerai_hidup=?, cerai_mati=?, total=?
        WHERE id=?
    ''', (no_urut, nama_sls, belum_kawin, kawin, cerai_hidup, cerai_mati, total, id))
    conn.commit()
    conn.close()

    flash(f'Perubahan data status perkawinan SLS "{nama_sls}" berhasil disimpan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='perkawinan'))


@app.route('/admin/statistik/perkawinan/<int:id>/hapus', methods=['POST'])
@login_required
def admin_statistik_perkawinan_hapus(id):
    """Menghapus satu baris data status perkawinan SLS"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tahun, nama_sls FROM statistik_perkawinan WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        tahun, nama_sls = row
        cursor.execute("DELETE FROM statistik_perkawinan WHERE id = ?", (id,))
        conn.commit()
        flash(f'Data status perkawinan SLS "{nama_sls}" berhasil dihapus.', 'info')
    else:
        tahun = 2026

    conn.close()
    return redirect(url_for('admin_statistik', tahun=tahun, tab='perkawinan'))


@app.route('/admin/statistik/perkawinan/<int:tahun>/reset', methods=['POST'])
@login_required
def admin_statistik_perkawinan_reset(tahun):
    """Mereset seluruh data status perkawinan pada tahun tertentu"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM statistik_perkawinan WHERE tahun = ?", (tahun,))
    conn.commit()
    conn.close()

    flash(f'Seluruh data status perkawinan untuk Tahun {tahun} berhasil dikosongkan.', 'warning')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='perkawinan'))


# --- 7e. ROUTE DATA STATUS PENCATATAN PERKAWINAN PER SLS (RT/RW) ---

@app.route('/admin/statistik/pencatatan-nikah/template')
@login_required
def admin_statistik_pencatatan_nikah_template():
    """Unduh template upload data pencatatan perkawinan per SLS (.xlsx atau .csv)"""
    file_format = request.args.get('format', 'xlsx').lower()
    template_type = request.args.get('type', 'contoh').lower()
    include_sample = (template_type != 'kosong')

    if file_format == 'csv':
        buf = generate_template_pencatatan_nikah_csv(include_sample=include_sample)
        filename = f"Template_Pencatatan_Perkawinan_SLS_Desa_{'Sample' if include_sample else 'Kosong'}.csv"
        return send_file(
            buf,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    else:
        buf = generate_template_pencatatan_nikah_excel(include_sample=include_sample)
        filename = f"Template_Pencatatan_Perkawinan_SLS_Desa_{'Sample' if include_sample else 'Kosong'}.xlsx"
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )


@app.route('/admin/statistik/pencatatan-nikah/export')
@login_required
def admin_statistik_pencatatan_nikah_export():
    """Ekspor data status pencatatan perkawinan per SLS tahun tertentu ke file Excel (.xlsx) atau CSV"""
    tahun = request.args.get('tahun', type=int) or 2026
    file_format = request.args.get('format', 'xlsx').lower()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM statistik_pencatatan_nikah WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (tahun,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if file_format == 'csv':
        buf = export_pencatatan_nikah_csv(rows, tahun)
        return send_file(
            buf,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"Data_Pencatatan_Perkawinan_SLS_{tahun}.csv"
        )
    else:
        buf = export_pencatatan_nikah_excel(rows, tahun)
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"Data_Pencatatan_Perkawinan_SLS_{tahun}.xlsx"
        )


@app.route('/admin/statistik/pencatatan-nikah/upload', methods=['POST'])
@login_required
def admin_statistik_pencatatan_nikah_upload():
    """Memproses unggahan file Excel/CSV data pencatatan perkawinan per SLS"""
    if 'file_pencatatan' not in request.files:
        flash('Tidak ada file yang dipilih untuk diunggah.', 'danger')
        return redirect(url_for('admin_statistik', tab='perkawinan'))

    file = request.files['file_pencatatan']
    if not file or file.filename == '':
        flash('Harap pilih file Excel (.xlsx) atau CSV (.csv).', 'warning')
        return redirect(url_for('admin_statistik', tab='perkawinan'))

    tahun = int(request.form.get('tahun') or 2026)
    mode = request.form.get('mode', 'replace')

    parsed_data, error_msg = parse_uploaded_pencatatan_nikah_file(file)
    if error_msg:
        flash(f'Gagal memproses file: {error_msg}', 'danger')
        return redirect(url_for('admin_statistik', tahun=tahun, tab='perkawinan'))

    conn = get_db()
    cursor = conn.cursor()

    if mode == 'replace':
        cursor.execute("DELETE FROM statistik_pencatatan_nikah WHERE tahun = ?", (tahun,))

    for item in parsed_data:
        cursor.execute('''
            INSERT INTO statistik_pencatatan_nikah (
                tahun, no_urut, nama_sls, kawin_tercatat, kawin_belum_tercatat, kawin_tidak_tercatat, total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            tahun,
            item.get('no_urut'),
            item.get('nama_sls'),
            item.get('kawin_tercatat', 0),
            item.get('kawin_belum_tercatat', 0),
            item.get('kawin_tidak_tercatat', 0),
            item.get('total', 0)
        ))

    conn.commit()
    conn.close()

    total_jiwa = sum(it.get('total', 0) for it in parsed_data)
    flash(
        f'Berhasil mengimpor data status pencatatan perkawinan untuk {len(parsed_data)} SLS pada Tahun {tahun}! '
        f'Total tercatat: {total_jiwa:,} jiwa.',
        'success'
    )
    return redirect(url_for('admin_statistik', tahun=tahun, tab='perkawinan'))


@app.route('/admin/statistik/pencatatan-nikah/tambah', methods=['POST'])
@login_required
def admin_statistik_pencatatan_nikah_tambah():
    """Menambahkan baris data status pencatatan perkawinan SLS baru secara manual"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()
    kawin_tercatat = max(0, int(request.form.get('kawin_tercatat') or 0))
    kawin_belum_tercatat = max(0, int(request.form.get('kawin_belum_tercatat') or 0))
    kawin_tidak_tercatat = max(0, int(request.form.get('kawin_tidak_tercatat') or 0))
    total = kawin_tercatat + kawin_belum_tercatat + kawin_tidak_tercatat

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO statistik_pencatatan_nikah (
            tahun, no_urut, nama_sls, kawin_tercatat, kawin_belum_tercatat, kawin_tidak_tercatat, total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (tahun, no_urut, nama_sls, kawin_tercatat, kawin_belum_tercatat, kawin_tidak_tercatat, total))
    conn.commit()
    conn.close()

    flash(f'Data pencatatan perkawinan SLS "{nama_sls}" berhasil ditambahkan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='perkawinan'))


@app.route('/admin/statistik/pencatatan-nikah/<int:id>/edit', methods=['POST'])
@login_required
def admin_statistik_pencatatan_nikah_edit(id):
    """Mengubah satu baris data status pencatatan perkawinan per SLS"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()
    kawin_tercatat = max(0, int(request.form.get('kawin_tercatat') or 0))
    kawin_belum_tercatat = max(0, int(request.form.get('kawin_belum_tercatat') or 0))
    kawin_tidak_tercatat = max(0, int(request.form.get('kawin_tidak_tercatat') or 0))
    total = kawin_tercatat + kawin_belum_tercatat + kawin_tidak_tercatat

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE statistik_pencatatan_nikah SET
            no_urut=?, nama_sls=?, kawin_tercatat=?, kawin_belum_tercatat=?, kawin_tidak_tercatat=?, total=?
        WHERE id=?
    ''', (no_urut, nama_sls, kawin_tercatat, kawin_belum_tercatat, kawin_tidak_tercatat, total, id))
    conn.commit()
    conn.close()

    flash(f'Perubahan data pencatatan perkawinan SLS "{nama_sls}" berhasil disimpan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='perkawinan'))


@app.route('/admin/statistik/pencatatan-nikah/<int:id>/hapus', methods=['POST'])
@login_required
def admin_statistik_pencatatan_nikah_hapus(id):
    """Menghapus satu baris data status pencatatan perkawinan SLS"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tahun, nama_sls FROM statistik_pencatatan_nikah WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        tahun, nama_sls = row
        cursor.execute("DELETE FROM statistik_pencatatan_nikah WHERE id = ?", (id,))
        conn.commit()
        flash(f'Data pencatatan perkawinan SLS "{nama_sls}" berhasil dihapus.', 'info')
    else:
        tahun = 2026

    conn.close()
    return redirect(url_for('admin_statistik', tahun=tahun, tab='perkawinan'))


@app.route('/admin/statistik/pencatatan-nikah/<int:tahun>/reset', methods=['POST'])
@login_required
def admin_statistik_pencatatan_nikah_reset(tahun):
    """Mereset seluruh data status pencatatan perkawinan pada tahun tertentu"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM statistik_pencatatan_nikah WHERE tahun = ?", (tahun,))
    conn.commit()
    conn.close()

    flash(f'Seluruh data status pencatatan perkawinan untuk Tahun {tahun} berhasil dikosongkan.', 'warning')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='perkawinan'))


# --- 7f. ROUTE DATA AGAMA DAN KEPERCAYAAN PER SLS (RT/RW) ---

@app.route('/admin/statistik/agama/template')
@login_required
def admin_statistik_agama_template():
    """Unduh template upload data agama dan kepercayaan per SLS (.xlsx atau .csv)"""
    file_format = request.args.get('format', 'xlsx').lower()
    template_type = request.args.get('type', 'contoh').lower()
    include_sample = (template_type != 'kosong')

    if file_format == 'csv':
        buf = generate_template_agama_csv(include_sample=include_sample)
        filename = f"Template_Agama_Kepercayaan_SLS_Desa_{'Sample' if include_sample else 'Kosong'}.csv"
        return send_file(
            buf,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    else:
        buf = generate_template_agama_excel(include_sample=include_sample)
        filename = f"Template_Agama_Kepercayaan_SLS_Desa_{'Sample' if include_sample else 'Kosong'}.xlsx"
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )


@app.route('/admin/statistik/agama/export')
@login_required
def admin_statistik_agama_export():
    """Ekspor data agama dan kepercayaan per SLS tahun tertentu ke file Excel (.xlsx) atau CSV"""
    tahun = request.args.get('tahun', type=int) or 2026
    file_format = request.args.get('format', 'xlsx').lower()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM statistik_agama WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (tahun,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if file_format == 'csv':
        buf = export_agama_csv(rows, tahun)
        return send_file(
            buf,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"Data_Agama_Kepercayaan_SLS_{tahun}.csv"
        )
    else:
        buf = export_agama_excel(rows, tahun)
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"Data_Agama_Kepercayaan_SLS_{tahun}.xlsx"
        )


@app.route('/admin/statistik/agama/upload', methods=['POST'])
@login_required
def admin_statistik_agama_upload():
    """Memproses unggahan file Excel/CSV data agama dan kepercayaan per SLS"""
    if 'file_agama' not in request.files:
        flash('Tidak ada file yang dipilih untuk diunggah.', 'danger')
        return redirect(url_for('admin_statistik', tab='agama'))

    file = request.files['file_agama']
    if not file or file.filename == '':
        flash('Harap pilih file Excel (.xlsx) atau CSV (.csv).', 'warning')
        return redirect(url_for('admin_statistik', tab='agama'))

    tahun = int(request.form.get('tahun') or 2026)
    mode = request.form.get('mode', 'replace')

    parsed_data, error_msg = parse_uploaded_agama_file(file)
    if error_msg:
        flash(f'Gagal memproses file: {error_msg}', 'danger')
        return redirect(url_for('admin_statistik', tahun=tahun, tab='agama'))

    conn = get_db()
    cursor = conn.cursor()

    if mode == 'replace':
        cursor.execute("DELETE FROM statistik_agama WHERE tahun = ?", (tahun,))

    for item in parsed_data:
        cursor.execute('''
            INSERT INTO statistik_agama (
                tahun, no_urut, nama_sls, islam, kristen, katholik, budha, hindu, konghucu, kepercayaan_lainnya, total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tahun,
            item.get('no_urut'),
            item.get('nama_sls'),
            item.get('islam', 0),
            item.get('kristen', 0),
            item.get('katholik', 0),
            item.get('budha', 0),
            item.get('hindu', 0),
            item.get('konghucu', 0),
            item.get('kepercayaan_lainnya', 0),
            item.get('total', 0)
        ))

    conn.commit()
    conn.close()

    total_jiwa = sum(it.get('total', 0) for it in parsed_data)
    flash(
        f'Berhasil mengimpor data agama dan kepercayaan untuk {len(parsed_data)} SLS pada Tahun {tahun}! '
        f'Total tercatat: {total_jiwa:,} jiwa.',
        'success'
    )
    return redirect(url_for('admin_statistik', tahun=tahun, tab='agama'))


@app.route('/admin/statistik/agama/tambah', methods=['POST'])
@login_required
def admin_statistik_agama_tambah():
    """Menambahkan baris data agama SLS baru secara manual"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()
    islam = max(0, int(request.form.get('islam') or 0))
    kristen = max(0, int(request.form.get('kristen') or 0))
    katholik = max(0, int(request.form.get('katholik') or 0))
    budha = max(0, int(request.form.get('budha') or 0))
    hindu = max(0, int(request.form.get('hindu') or 0))
    konghucu = max(0, int(request.form.get('konghucu') or 0))
    kepercayaan_lainnya = max(0, int(request.form.get('kepercayaan_lainnya') or 0))
    total = islam + kristen + katholik + budha + hindu + konghucu + kepercayaan_lainnya

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO statistik_agama (
            tahun, no_urut, nama_sls, islam, kristen, katholik, budha, hindu, konghucu, kepercayaan_lainnya, total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tahun, no_urut, nama_sls, islam, kristen, katholik, budha, hindu, konghucu, kepercayaan_lainnya, total))
    conn.commit()
    conn.close()

    flash(f'Data agama SLS "{nama_sls}" berhasil ditambahkan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='agama'))


@app.route('/admin/statistik/agama/<int:id>/edit', methods=['POST'])
@login_required
def admin_statistik_agama_edit(id):
    """Mengubah satu baris data agama per SLS"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()
    islam = max(0, int(request.form.get('islam') or 0))
    kristen = max(0, int(request.form.get('kristen') or 0))
    katholik = max(0, int(request.form.get('katholik') or 0))
    budha = max(0, int(request.form.get('budha') or 0))
    hindu = max(0, int(request.form.get('hindu') or 0))
    konghucu = max(0, int(request.form.get('konghucu') or 0))
    kepercayaan_lainnya = max(0, int(request.form.get('kepercayaan_lainnya') or 0))
    total = islam + kristen + katholik + budha + hindu + konghucu + kepercayaan_lainnya

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE statistik_agama SET
            no_urut=?, nama_sls=?, islam=?, kristen=?, katholik=?, budha=?, hindu=?, konghucu=?, kepercayaan_lainnya=?, total=?
        WHERE id=?
    ''', (no_urut, nama_sls, islam, kristen, katholik, budha, hindu, konghucu, kepercayaan_lainnya, total, id))
    conn.commit()
    conn.close()

    flash(f'Perubahan data agama SLS "{nama_sls}" berhasil disimpan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='agama'))


@app.route('/admin/statistik/agama/<int:id>/hapus', methods=['POST'])
@login_required
def admin_statistik_agama_hapus(id):
    """Menghapus satu baris data agama SLS"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tahun, nama_sls FROM statistik_agama WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        tahun, nama_sls = row
        cursor.execute("DELETE FROM statistik_agama WHERE id = ?", (id,))
        conn.commit()
        flash(f'Data agama SLS "{nama_sls}" berhasil dihapus.', 'info')
    else:
        tahun = 2026

    conn.close()
    return redirect(url_for('admin_statistik', tahun=tahun, tab='agama'))


@app.route('/admin/statistik/agama/<int:tahun>/reset', methods=['POST'])
@login_required
def admin_statistik_agama_reset(tahun):
    """Mereset seluruh data agama pada tahun tertentu"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM statistik_agama WHERE tahun = ?", (tahun,))
    conn.commit()
    conn.close()

    flash(f'Seluruh data agama dan kepercayaan untuk Tahun {tahun} berhasil dikosongkan.', 'warning')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='agama'))


# --- 7g. ROUTE DATA BANTUAN SOSIAL (BANSOS) PER SLS (RT/RW) ---

@app.route('/admin/statistik/bansos/template')
@login_required
def admin_statistik_bansos_template():
    """Unduh template upload data bantuan sosial per SLS (.xlsx atau .csv)"""
    file_format = request.args.get('format', 'xlsx').lower()
    template_type = request.args.get('type', 'contoh').lower()
    include_sample = (template_type != 'kosong')

    if file_format == 'csv':
        buf = generate_template_bansos_csv(include_sample=include_sample)
        filename = f"Template_Bantuan_Sosial_SLS_Desa_{'Sample' if include_sample else 'Kosong'}.csv"
        return send_file(
            buf,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    else:
        buf = generate_template_bansos_excel(include_sample=include_sample)
        filename = f"Template_Bantuan_Sosial_SLS_Desa_{'Sample' if include_sample else 'Kosong'}.xlsx"
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )


@app.route('/admin/statistik/bansos/export')
@login_required
def admin_statistik_bansos_export():
    """Ekspor data bantuan sosial per SLS tahun tertentu ke file Excel (.xlsx) atau CSV"""
    tahun = request.args.get('tahun', type=int) or 2026
    file_format = request.args.get('format', 'xlsx').lower()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM statistik_bansos WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (tahun,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if file_format == 'csv':
        buf = export_bansos_csv(rows, tahun)
        return send_file(
            buf,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"Data_Bantuan_Sosial_SLS_{tahun}.csv"
        )
    else:
        buf = export_bansos_excel(rows, tahun)
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"Data_Bantuan_Sosial_SLS_{tahun}.xlsx"
        )


@app.route('/admin/statistik/bansos/upload', methods=['POST'])
@login_required
def admin_statistik_bansos_upload():
    """Memproses unggahan file Excel/CSV data bantuan sosial per SLS"""
    if 'file_bansos' not in request.files:
        flash('Tidak ada file yang dipilih untuk diunggah.', 'danger')
        return redirect(url_for('admin_statistik', tab='bansos'))

    file = request.files['file_bansos']
    if not file or file.filename == '':
        flash('Harap pilih file Excel (.xlsx) atau CSV (.csv).', 'warning')
        return redirect(url_for('admin_statistik', tab='bansos'))

    tahun = int(request.form.get('tahun') or 2026)
    mode = request.form.get('mode', 'replace')

    parsed_data, error_msg = parse_uploaded_bansos_file(file)
    if error_msg:
        flash(f'Gagal memproses file: {error_msg}', 'danger')
        return redirect(url_for('admin_statistik', tahun=tahun, tab='bansos'))

    conn = get_db()
    cursor = conn.cursor()

    if mode == 'replace':
        cursor.execute("DELETE FROM statistik_bansos WHERE tahun = ?", (tahun,))

    for item in parsed_data:
        cursor.execute('''
            INSERT INTO statistik_bansos (
                tahun, no_urut, nama_sls, pkh, bpnt, bos, bapanas, stunting, pbi_jkn, blt, blt_dd, lainnya, total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tahun,
            item.get('no_urut'),
            item.get('nama_sls'),
            item.get('pkh', 0),
            item.get('bpnt', 0),
            item.get('bos', 0),
            item.get('bapanas', 0),
            item.get('stunting', 0),
            item.get('pbi_jkn', 0),
            item.get('blt', 0),
            item.get('blt_dd', 0),
            item.get('lainnya', 0),
            item.get('total', 0)
        ))

    conn.commit()
    conn.close()

    total_kpm = sum(it.get('total', 0) for it in parsed_data)
    flash(
        f'Berhasil mengimpor data bantuan sosial untuk {len(parsed_data)} SLS pada Tahun {tahun}! '
        f'Total alokasi bantuan tercatat: {total_kpm:,} penerima.',
        'success'
    )
    return redirect(url_for('admin_statistik', tahun=tahun, tab='bansos'))


@app.route('/admin/statistik/bansos/tambah', methods=['POST'])
@login_required
def admin_statistik_bansos_tambah():
    """Menambahkan baris data bantuan sosial SLS baru secara manual"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()
    pkh = max(0, int(request.form.get('pkh') or 0))
    bpnt = max(0, int(request.form.get('bpnt') or 0))
    bos = max(0, int(request.form.get('bos') or 0))
    bapanas = max(0, int(request.form.get('bapanas') or 0))
    stunting = max(0, int(request.form.get('stunting') or 0))
    pbi_jkn = max(0, int(request.form.get('pbi_jkn') or 0))
    blt = max(0, int(request.form.get('blt') or 0))
    blt_dd = max(0, int(request.form.get('blt_dd') or 0))
    lainnya = max(0, int(request.form.get('lainnya') or 0))
    total = pkh + bpnt + bos + bapanas + stunting + pbi_jkn + blt + blt_dd + lainnya

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO statistik_bansos (
            tahun, no_urut, nama_sls, pkh, bpnt, bos, bapanas, stunting, pbi_jkn, blt, blt_dd, lainnya, total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tahun, no_urut, nama_sls, pkh, bpnt, bos, bapanas, stunting, pbi_jkn, blt, blt_dd, lainnya, total))
    conn.commit()
    conn.close()

    flash(f'Data bantuan sosial SLS "{nama_sls}" berhasil ditambahkan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='bansos'))


@app.route('/admin/statistik/bansos/<int:id>/edit', methods=['POST'])
@login_required
def admin_statistik_bansos_edit(id):
    """Mengubah satu baris data bantuan sosial per SLS"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()
    pkh = max(0, int(request.form.get('pkh') or 0))
    bpnt = max(0, int(request.form.get('bpnt') or 0))
    bos = max(0, int(request.form.get('bos') or 0))
    bapanas = max(0, int(request.form.get('bapanas') or 0))
    stunting = max(0, int(request.form.get('stunting') or 0))
    pbi_jkn = max(0, int(request.form.get('pbi_jkn') or 0))
    blt = max(0, int(request.form.get('blt') or 0))
    blt_dd = max(0, int(request.form.get('blt_dd') or 0))
    lainnya = max(0, int(request.form.get('lainnya') or 0))
    total = pkh + bpnt + bos + bapanas + stunting + pbi_jkn + blt + blt_dd + lainnya

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE statistik_bansos SET
            no_urut=?, nama_sls=?, pkh=?, bpnt=?, bos=?, bapanas=?, stunting=?, pbi_jkn=?, blt=?, blt_dd=?, lainnya=?, total=?
        WHERE id=?
    ''', (no_urut, nama_sls, pkh, bpnt, bos, bapanas, stunting, pbi_jkn, blt, blt_dd, lainnya, total, id))
    conn.commit()
    conn.close()

    flash(f'Perubahan data bantuan sosial SLS "{nama_sls}" berhasil disimpan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='bansos'))


@app.route('/admin/statistik/bansos/<int:id>/hapus', methods=['POST'])
@login_required
def admin_statistik_bansos_hapus(id):
    """Menghapus satu baris data bantuan sosial SLS"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tahun, nama_sls FROM statistik_bansos WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        tahun, nama_sls = row
        cursor.execute("DELETE FROM statistik_bansos WHERE id = ?", (id,))
        conn.commit()
        flash(f'Data bantuan sosial SLS "{nama_sls}" berhasil dihapus.', 'info')
    else:
        tahun = 2026

    conn.close()
    return redirect(url_for('admin_statistik', tahun=tahun, tab='bansos'))


@app.route('/admin/statistik/bansos/<int:tahun>/reset', methods=['POST'])
@login_required
def admin_statistik_bansos_reset(tahun):
    """Mereset seluruh data bantuan sosial pada tahun tertentu"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM statistik_bansos WHERE tahun = ?", (tahun,))
    conn.commit()
    conn.close()

    flash(f'Seluruh data bantuan sosial untuk Tahun {tahun} berhasil dikosongkan.', 'warning')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='bansos'))



# --- 7h. ROUTE DATA STATUS KEBERADAAN ORANG TUA ANAK (YATIM / PIATU) PER SLS ---

@app.route('/admin/statistik/anak/template')
@login_required
def admin_statistik_anak_template():
    """Unduh template upload data status keberadaan orang tua anak (.xlsx atau .csv)"""
    file_format = request.args.get('format', 'xlsx').lower()
    template_type = request.args.get('type', 'contoh').lower()
    include_sample = (template_type != 'kosong')

    if file_format == 'csv':
        buf = generate_template_anak_csv(include_sample=include_sample)
        filename = f"template_status_orang_tua_anak_{template_type}.csv"
        mimetype = 'text/csv'
    else:
        buf = generate_template_anak_excel(include_sample=include_sample)
        filename = f"template_status_orang_tua_anak_{template_type}.xlsx"
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype=mimetype
    )


@app.route('/admin/statistik/anak/export')
@login_required
def admin_statistik_anak_export():
    """Ekspor data status keberadaan orang tua anak tahun terpilih (.xlsx atau .csv)"""
    tahun = request.args.get('tahun', type=int) or 2026
    file_format = request.args.get('format', 'xlsx').lower()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM statistik_anak WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (tahun,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if file_format == 'csv':
        buf = export_anak_csv(rows, tahun)
        filename = f"data_status_orang_tua_anak_desa_kersik_{tahun}.csv"
        mimetype = 'text/csv'
    else:
        buf = export_anak_excel(rows, tahun)
        filename = f"data_status_orang_tua_anak_desa_kersik_{tahun}.xlsx"
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype=mimetype
    )


@app.route('/admin/statistik/anak/upload', methods=['POST'])
@login_required
def admin_statistik_anak_upload():
    """Mengunggah file Excel / CSV data status keberadaan orang tua anak per SLS"""
    tahun = request.form.get('tahun', type=int) or 2026

    if 'file_anak' not in request.files:
        flash('Tidak ada berkas yang dipilih.', 'danger')
        return redirect(url_for('admin_statistik', tab='anak', subtab='yatim'))

    file = request.files['file_anak']
    if not file or file.filename == '':
        flash('Silakan pilih berkas Excel (.xlsx) atau CSV (.csv).', 'danger')
        return redirect(url_for('admin_statistik', tab='anak', subtab='yatim'))

    parsed_data, error_msg = parse_uploaded_anak_file(file)
    if error_msg:
        flash(f'Gagal mengimpor data: {error_msg}', 'danger')
        return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='yatim'))

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Hapus data tahun berjalan lalu insert data baru
        cursor.execute("DELETE FROM statistik_anak WHERE tahun = ?", (tahun,))

        for row in parsed_data:
            cursor.execute('''
                INSERT INTO statistik_anak (
                    tahun, no_urut, nama_sls, anak_yatim, anak_piatu, yatim_piatu, orang_tua_lengkap, total_anak
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tahun,
                row['no_urut'],
                row['nama_sls'],
                row.get('anak_yatim', 0),
                row.get('anak_piatu', 0),
                row.get('yatim_piatu', 0),
                row.get('orang_tua_lengkap', 0),
                row.get('total_anak', 0)
            ))

        conn.commit()
        flash(
            f'Berhasil! {len(parsed_data)} baris data status keberadaan orang tua anak tahun {tahun} berhasil diimpor.',
            'success'
        )
    except Exception as e:
        conn.rollback()
        flash(f'Terjadi kesalahan database saat menyimpan: {str(e)}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='yatim'))


@app.route('/admin/statistik/anak/tambah', methods=['POST'])
@login_required
def admin_statistik_anak_tambah():
    """Menambahkan baris data status keberadaan orang tua anak SLS baru secara manual"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()
    anak_yatim = max(0, int(request.form.get('anak_yatim') or 0))
    anak_piatu = max(0, int(request.form.get('anak_piatu') or 0))
    yatim_piatu = max(0, int(request.form.get('yatim_piatu') or 0))
    orang_tua_lengkap = max(0, int(request.form.get('orang_tua_lengkap') or 0))
    total_anak = anak_yatim + anak_piatu + yatim_piatu + orang_tua_lengkap

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO statistik_anak (
            tahun, no_urut, nama_sls, anak_yatim, anak_piatu, yatim_piatu, orang_tua_lengkap, total_anak
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tahun, no_urut, nama_sls, anak_yatim, anak_piatu, yatim_piatu, orang_tua_lengkap, total_anak))
    conn.commit()
    conn.close()

    flash(f'Data status keberadaan orang tua anak SLS "{nama_sls}" berhasil ditambahkan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='yatim'))


@app.route('/admin/statistik/anak/<int:id>/edit', methods=['POST'])
@login_required
def admin_statistik_anak_edit(id):
    """Mengupdate baris data status keberadaan orang tua anak SLS"""
    tahun = int(request.form.get('tahun') or 2026)
    nama_sls = request.form.get('nama_sls', '').strip()
    anak_yatim = max(0, int(request.form.get('anak_yatim') or 0))
    anak_piatu = max(0, int(request.form.get('anak_piatu') or 0))
    yatim_piatu = max(0, int(request.form.get('yatim_piatu') or 0))
    orang_tua_lengkap = max(0, int(request.form.get('orang_tua_lengkap') or 0))
    total_anak = anak_yatim + anak_piatu + yatim_piatu + orang_tua_lengkap

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE statistik_anak SET
            nama_sls = ?,
            anak_yatim = ?,
            anak_piatu = ?,
            yatim_piatu = ?,
            orang_tua_lengkap = ?,
            total_anak = ?
        WHERE id = ?
    ''', (nama_sls, anak_yatim, anak_piatu, yatim_piatu, orang_tua_lengkap, total_anak, id))
    conn.commit()
    conn.close()

    flash(f'Data SLS "{nama_sls}" berhasil diperbarui.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='yatim'))


@app.route('/admin/statistik/anak/<int:id>/hapus', methods=['POST'])
@login_required
def admin_statistik_anak_hapus(id):
    """Menghapus data status orang tua anak SLS tertentu"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tahun, nama_sls FROM statistik_anak WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        tahun, nama_sls = row
        cursor.execute("DELETE FROM statistik_anak WHERE id = ?", (id,))
        conn.commit()
        flash(f'Data status keberadaan orang tua anak SLS "{nama_sls}" berhasil dihapus.', 'info')
    else:
        tahun = 2026

    conn.close()
    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='yatim'))


@app.route('/admin/statistik/anak/<int:tahun>/reset', methods=['POST'])
@login_required
def admin_statistik_anak_reset(tahun):
    """Mereset seluruh data status orang tua anak pada tahun tertentu"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM statistik_anak WHERE tahun = ?", (tahun,))
    conn.commit()
    conn.close()

    flash(f'Seluruh data status keberadaan orang tua anak untuk Tahun {tahun} berhasil dikosongkan.', 'warning')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='yatim'))



# --- 7i. ROUTE DATA ANAK GIZI BURUK PER SLS ---

@app.route('/admin/statistik/gizi-buruk/template')
@login_required
def admin_statistik_gizi_buruk_template():
    """Unduh template upload data anak gizi buruk (.xlsx atau .csv)"""
    file_format = request.args.get('format', 'xlsx').lower()
    template_type = request.args.get('type', 'contoh').lower()
    include_sample = (template_type != 'kosong')

    if file_format == 'csv':
        buf = generate_template_gizi_buruk_csv(include_sample=include_sample)
        filename = f"template_anak_gizi_buruk_{template_type}.csv"
        mimetype = 'text/csv'
    else:
        buf = generate_template_gizi_buruk_excel(include_sample=include_sample)
        filename = f"template_anak_gizi_buruk_{template_type}.xlsx"
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype=mimetype
    )


@app.route('/admin/statistik/gizi-buruk/export')
@login_required
def admin_statistik_gizi_buruk_export():
    """Ekspor data anak gizi buruk tahun terpilih (.xlsx atau .csv)"""
    tahun = request.args.get('tahun', type=int) or 2026
    file_format = request.args.get('format', 'xlsx').lower()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM statistik_gizi_buruk WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (tahun,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if file_format == 'csv':
        buf = export_gizi_buruk_csv(rows, tahun)
        filename = f"data_anak_gizi_buruk_desa_kersik_{tahun}.csv"
        mimetype = 'text/csv'
    else:
        buf = export_gizi_buruk_excel(rows, tahun)
        filename = f"data_anak_gizi_buruk_desa_kersik_{tahun}.xlsx"
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype=mimetype
    )


@app.route('/admin/statistik/gizi-buruk/upload', methods=['POST'])
@login_required
def admin_statistik_gizi_buruk_upload():
    """Mengunggah file Excel / CSV data anak gizi buruk per SLS"""
    tahun = request.form.get('tahun', type=int) or 2026

    if 'file_gizi_buruk' not in request.files:
        flash('Tidak ada berkas yang dipilih.', 'danger')
        return redirect(url_for('admin_statistik', tab='anak', subtab='gizi'))

    file = request.files['file_gizi_buruk']
    if not file or file.filename == '':
        flash('Silakan pilih berkas Excel (.xlsx) atau CSV (.csv).', 'danger')
        return redirect(url_for('admin_statistik', tab='anak', subtab='gizi'))

    parsed_data, error_msg = parse_uploaded_gizi_buruk_file(file)
    if error_msg:
        flash(f'Gagal mengimpor data: {error_msg}', 'danger')
        return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='gizi'))

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM statistik_gizi_buruk WHERE tahun = ?", (tahun,))

        for row in parsed_data:
            cursor.execute('''
                INSERT INTO statistik_gizi_buruk (
                    tahun, no_urut, nama_sls, anak_gizi_buruk, jumlah_anak_balita, persentase
                )
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                tahun,
                row['no_urut'],
                row['nama_sls'],
                row.get('anak_gizi_buruk', 0),
                row.get('jumlah_anak_balita', 0),
                row.get('persentase', 0.0)
            ))

        conn.commit()
        flash(
            f'Berhasil! {len(parsed_data)} baris data anak gizi buruk tahun {tahun} berhasil diimpor.',
            'success'
        )
    except Exception as e:
        conn.rollback()
        flash(f'Terjadi kesalahan database saat menyimpan: {str(e)}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='gizi'))


@app.route('/admin/statistik/gizi-buruk/tambah', methods=['POST'])
@login_required
def admin_statistik_gizi_buruk_tambah():
    """Menambahkan baris data anak gizi buruk SLS baru secara manual"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()
    anak_gizi_buruk = max(0, int(request.form.get('anak_gizi_buruk') or 0))
    jumlah_anak_balita = max(0, int(request.form.get('jumlah_anak_balita') or 0))
    persentase = round((anak_gizi_buruk / jumlah_anak_balita * 100), 2) if jumlah_anak_balita > 0 else 0.0

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO statistik_gizi_buruk (
            tahun, no_urut, nama_sls, anak_gizi_buruk, jumlah_anak_balita, persentase
        )
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (tahun, no_urut, nama_sls, anak_gizi_buruk, jumlah_anak_balita, persentase))
    conn.commit()
    conn.close()

    flash(f'Data anak gizi buruk SLS "{nama_sls}" berhasil ditambahkan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='gizi'))


@app.route('/admin/statistik/gizi-buruk/<int:id>/edit', methods=['POST'])
@login_required
def admin_statistik_gizi_buruk_edit(id):
    """Mengupdate baris data anak gizi buruk SLS"""
    tahun = int(request.form.get('tahun') or 2026)
    nama_sls = request.form.get('nama_sls', '').strip()
    anak_gizi_buruk = max(0, int(request.form.get('anak_gizi_buruk') or 0))
    jumlah_anak_balita = max(0, int(request.form.get('jumlah_anak_balita') or 0))
    persentase = round((anak_gizi_buruk / jumlah_anak_balita * 100), 2) if jumlah_anak_balita > 0 else 0.0

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE statistik_gizi_buruk SET
            nama_sls = ?,
            anak_gizi_buruk = ?,
            jumlah_anak_balita = ?,
            persentase = ?
        WHERE id = ?
    ''', (nama_sls, anak_gizi_buruk, jumlah_anak_balita, persentase, id))
    conn.commit()
    conn.close()

    flash(f'Data anak gizi buruk SLS "{nama_sls}" berhasil diperbarui.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='gizi'))


@app.route('/admin/statistik/gizi-buruk/<int:id>/hapus', methods=['POST'])
@login_required
def admin_statistik_gizi_buruk_hapus(id):
    """Menghapus data anak gizi buruk SLS tertentu"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tahun, nama_sls FROM statistik_gizi_buruk WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        tahun, nama_sls = row
        cursor.execute("DELETE FROM statistik_gizi_buruk WHERE id = ?", (id,))
        conn.commit()
        flash(f'Data anak gizi buruk SLS "{nama_sls}" berhasil dihapus.', 'info')
    else:
        tahun = 2026

    conn.close()
    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='gizi'))


@app.route('/admin/statistik/gizi-buruk/<int:tahun>/reset', methods=['POST'])
@login_required
def admin_statistik_gizi_buruk_reset(tahun):
    """Mereset seluruh data anak gizi buruk pada tahun tertentu"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM statistik_gizi_buruk WHERE tahun = ?", (tahun,))
    conn.commit()
    conn.close()

    flash(f'Seluruh data anak gizi buruk untuk Tahun {tahun} berhasil dikosongkan.', 'warning')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='gizi'))



# --- 7j. ROUTE DATA ANAK STUNTING PER SLS ---

@app.route('/admin/statistik/stunting/template')
@login_required
def admin_statistik_stunting_template():
    """Unduh template upload data anak stunting (.xlsx atau .csv)"""
    file_format = request.args.get('format', 'xlsx').lower()
    template_type = request.args.get('type', 'contoh').lower()
    include_sample = (template_type != 'kosong')

    if file_format == 'csv':
        buf = generate_template_stunting_csv(include_sample=include_sample)
        filename = f"template_anak_stunting_{template_type}.csv"
        mimetype = 'text/csv'
    else:
        buf = generate_template_stunting_excel(include_sample=include_sample)
        filename = f"template_anak_stunting_{template_type}.xlsx"
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype=mimetype
    )


@app.route('/admin/statistik/stunting/export')
@login_required
def admin_statistik_stunting_export():
    """Ekspor data anak stunting tahun terpilih (.xlsx atau .csv)"""
    tahun = request.args.get('tahun', type=int) or 2026
    file_format = request.args.get('format', 'xlsx').lower()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM statistik_stunting WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (tahun,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if file_format == 'csv':
        buf = export_stunting_csv(rows, tahun)
        filename = f"data_anak_stunting_desa_kersik_{tahun}.csv"
        mimetype = 'text/csv'
    else:
        buf = export_stunting_excel(rows, tahun)
        filename = f"data_anak_stunting_desa_kersik_{tahun}.xlsx"
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype=mimetype
    )


@app.route('/admin/statistik/stunting/upload', methods=['POST'])
@login_required
def admin_statistik_stunting_upload():
    """Mengunggah file Excel / CSV data anak stunting per SLS"""
    tahun = request.form.get('tahun', type=int) or 2026

    if 'file_stunting' not in request.files:
        flash('Tidak ada berkas yang dipilih.', 'danger')
        return redirect(url_for('admin_statistik', tab='anak', subtab='stunting'))

    file = request.files['file_stunting']
    if not file or file.filename == '':
        flash('Silakan pilih berkas Excel (.xlsx) atau CSV (.csv).', 'danger')
        return redirect(url_for('admin_statistik', tab='anak', subtab='stunting'))

    parsed_data, error_msg = parse_uploaded_stunting_file(file)
    if error_msg:
        flash(f'Gagal mengimpor data: {error_msg}', 'danger')
        return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='stunting'))

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM statistik_stunting WHERE tahun = ?", (tahun,))

        for row in parsed_data:
            cursor.execute('''
                INSERT INTO statistik_stunting (
                    tahun, no_urut, nama_sls, anak_stunting, jumlah_anak_balita, persentase
                )
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                tahun,
                row['no_urut'],
                row['nama_sls'],
                row.get('anak_stunting', 0),
                row.get('jumlah_anak_balita', 0),
                row.get('persentase', 0.0)
            ))

        conn.commit()
        flash(
            f'Berhasil! {len(parsed_data)} baris data anak stunting tahun {tahun} berhasil diimpor.',
            'success'
        )
    except Exception as e:
        conn.rollback()
        flash(f'Terjadi kesalahan database saat menyimpan: {str(e)}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='stunting'))


@app.route('/admin/statistik/stunting/tambah', methods=['POST'])
@login_required
def admin_statistik_stunting_tambah():
    """Menambahkan baris data anak stunting SLS baru secara manual"""
    tahun = int(request.form.get('tahun') or 2026)
    no_urut = int(request.form.get('no_urut') or 1)
    nama_sls = request.form.get('nama_sls', '').strip()
    anak_stunting = max(0, int(request.form.get('anak_stunting') or 0))
    jumlah_anak_balita = max(0, int(request.form.get('jumlah_anak_balita') or 0))
    persentase = round((anak_stunting / jumlah_anak_balita * 100), 2) if jumlah_anak_balita > 0 else 0.0

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO statistik_stunting (
            tahun, no_urut, nama_sls, anak_stunting, jumlah_anak_balita, persentase
        )
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (tahun, no_urut, nama_sls, anak_stunting, jumlah_anak_balita, persentase))
    conn.commit()
    conn.close()

    flash(f'Data anak stunting SLS "{nama_sls}" berhasil ditambahkan.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='stunting'))


@app.route('/admin/statistik/stunting/<int:id>/edit', methods=['POST'])
@login_required
def admin_statistik_stunting_edit(id):
    """Mengupdate baris data anak stunting SLS"""
    tahun = int(request.form.get('tahun') or 2026)
    nama_sls = request.form.get('nama_sls', '').strip()
    anak_stunting = max(0, int(request.form.get('anak_stunting') or 0))
    jumlah_anak_balita = max(0, int(request.form.get('jumlah_anak_balita') or 0))
    persentase = round((anak_stunting / jumlah_anak_balita * 100), 2) if jumlah_anak_balita > 0 else 0.0

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE statistik_stunting SET
            nama_sls = ?,
            anak_stunting = ?,
            jumlah_anak_balita = ?,
            persentase = ?
        WHERE id = ?
    ''', (nama_sls, anak_stunting, jumlah_anak_balita, persentase, id))
    conn.commit()
    conn.close()

    flash(f'Data anak stunting SLS "{nama_sls}" berhasil diperbarui.', 'success')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='stunting'))


@app.route('/admin/statistik/stunting/<int:id>/hapus', methods=['POST'])
@login_required
def admin_statistik_stunting_hapus(id):
    """Menghapus data anak stunting SLS tertentu"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tahun, nama_sls FROM statistik_stunting WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        tahun, nama_sls = row
        cursor.execute("DELETE FROM statistik_stunting WHERE id = ?", (id,))
        conn.commit()
        flash(f'Data anak stunting SLS "{nama_sls}" berhasil dihapus.', 'info')
    else:
        tahun = 2026

    conn.close()
    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='stunting'))


@app.route('/admin/statistik/stunting/<int:tahun>/reset', methods=['POST'])
@login_required
def admin_statistik_stunting_reset(tahun):
    """Mereset seluruh data anak stunting pada tahun tertentu"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM statistik_stunting WHERE tahun = ?", (tahun,))
    conn.commit()
    conn.close()

    flash(f'Seluruh data anak stunting untuk Tahun {tahun} berhasil dikosongkan.', 'warning')
    return redirect(url_for('admin_statistik', tahun=tahun, tab='anak', subtab='stunting'))



# --- 8. PROFIL DESA (Khusus Super Admin) ---
@app.route('/admin/profil', methods=['GET', 'POST'])
@superadmin_required
def admin_profil():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        nama_desa = request.form.get('nama_desa')
        kecamatan = request.form.get('kecamatan')
        kabupaten = request.form.get('kabupaten')
        alamat = request.form.get('alamat')
        telepon = request.form.get('telepon')
        email = request.form.get('email')
        jam_pelayanan = request.form.get('jam_pelayanan')
        nama_kades = request.form.get('nama_kades')
        sambutan = request.form.get('sambutan_kades')
        visi = request.form.get('visi')
        misi = request.form.get('misi')

        # Foto Kepala Desa handling (upload file or existing)
        foto_kades = request.form.get('foto_kades')
        if 'foto_kades_file' in request.files:
            file = request.files['foto_kades_file']
            if file and file.filename != '':
                ext = os.path.splitext(file.filename)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                    filename = secure_filename(f"kades_{int(time.time())}_{random.randint(100,999)}{ext}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    foto_kades = f"static/images/uploads/{filename}"

        if foto_kades:
            cursor.execute('''
            UPDATE profil_desa SET nama_desa=?, kecamatan=?, kabupaten=?, alamat=?, telepon=?, email=?, jam_pelayanan=?, nama_kades=?, foto_kades=?, sambutan_kades=?, visi=?, misi=?
            WHERE id = 1
            ''', (nama_desa, kecamatan, kabupaten, alamat, telepon, email, jam_pelayanan, nama_kades, foto_kades, sambutan, visi, misi))
            # Sinkronkan otomatis ke tabel perangkat_desa (SOTK)
            cursor.execute('''
            UPDATE perangkat_desa SET nama=?, foto=? WHERE jabatan LIKE '%Kepala Desa%' OR jabatan LIKE '%Kuwu%' OR jabatan LIKE '%Pembekal%'
            ''', (nama_kades, foto_kades))
        else:
            cursor.execute('''
            UPDATE profil_desa SET nama_desa=?, kecamatan=?, kabupaten=?, alamat=?, telepon=?, email=?, jam_pelayanan=?, nama_kades=?, sambutan_kades=?, visi=?, misi=?
            WHERE id = 1
            ''', (nama_desa, kecamatan, kabupaten, alamat, telepon, email, jam_pelayanan, nama_kades, sambutan, visi, misi))
            cursor.execute('''
            UPDATE perangkat_desa SET nama=? WHERE jabatan LIKE '%Kepala Desa%' OR jabatan LIKE '%Kuwu%' OR jabatan LIKE '%Pembekal%'
            ''', (nama_kades,))

        conn.commit()
        flash('Profil dan identitas desa berhasil diperbarui.', 'success')

    cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
    profil = dict(cursor.fetchone() or {})
    conn.close()

    return render_template('admin/profil.html', profil=profil)

# --- 9. BRANDING, LOGO & HERO BANNER (Khusus Super Admin) ---
@app.route('/admin/branding', methods=['GET', 'POST'])
@superadmin_required
def admin_branding():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        judul_website = request.form.get('judul_website')
        nama_desa = request.form.get('nama_desa')
        tagline_website = request.form.get('tagline_website') or ''
        subtagline_website = request.form.get('subtagline_website') or ''
        kecamatan = request.form.get('kecamatan')
        kabupaten = request.form.get('kabupaten')
        
        # Logo handling (upload file or keep text)
        logo_website = request.form.get('logo_website')
        if 'logo_file' in request.files:
            file = request.files['logo_file']
            if file and file.filename != '':
                ext = os.path.splitext(file.filename)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.svg', '.webp']:
                    filename = secure_filename(f"logo_{int(time.time())}{ext}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    logo_website = f"static/images/uploads/{filename}"

        # Favicon handling
        favicon_website = request.form.get('favicon_website')
        if 'favicon_file' in request.files:
            file = request.files['favicon_file']
            if file and file.filename != '':
                ext = os.path.splitext(file.filename)[1].lower()
                if ext in ['.png', '.ico', '.jpg', '.jpeg', '.svg']:
                    filename = secure_filename(f"fav_{int(time.time())}{ext}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    favicon_website = f"static/images/uploads/{filename}"

        # Banner 1
        banner_hero_1 = request.form.get('banner_hero_1')
        if 'banner_file_1' in request.files:
            file = request.files['banner_file_1']
            if file and file.filename != '':
                ext = os.path.splitext(file.filename)[1].lower()
                filename = secure_filename(f"b1_{int(time.time())}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                banner_hero_1 = f"static/images/uploads/{filename}"
        banner_title_1 = request.form.get('banner_title_1')
        banner_desc_1 = request.form.get('banner_desc_1')

        # Banner 2
        banner_hero_2 = request.form.get('banner_hero_2')
        if 'banner_file_2' in request.files:
            file = request.files['banner_file_2']
            if file and file.filename != '':
                ext = os.path.splitext(file.filename)[1].lower()
                filename = secure_filename(f"b2_{int(time.time())}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                banner_hero_2 = f"static/images/uploads/{filename}"
        banner_title_2 = request.form.get('banner_title_2')
        banner_desc_2 = request.form.get('banner_desc_2')

        # Banner 3
        banner_hero_3 = request.form.get('banner_hero_3')
        if 'banner_file_3' in request.files:
            file = request.files['banner_file_3']
            if file and file.filename != '':
                ext = os.path.splitext(file.filename)[1].lower()
                filename = secure_filename(f"b3_{int(time.time())}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                banner_hero_3 = f"static/images/uploads/{filename}"
        banner_title_3 = request.form.get('banner_title_3')
        banner_desc_3 = request.form.get('banner_desc_3')

        cursor.execute('''
        UPDATE profil_desa SET 
            judul_website=?, nama_desa=?, tagline_website=?, subtagline_website=?,
            kecamatan=?, kabupaten=?, logo_website=?, favicon_website=?
        WHERE id = 1
        ''', (
            judul_website, nama_desa, tagline_website, subtagline_website,
            kecamatan, kabupaten, logo_website, favicon_website
        ))
        conn.commit()
        flash('Pengaturan logo & identitas website berhasil diperbarui!', 'success')

    cursor.execute("SELECT * FROM profil_desa WHERE id = 1")
    profil = dict(cursor.fetchone() or {})

    cursor.execute("SELECT * FROM banner_slider ORDER BY urutan ASC, id ASC")
    sliders = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return render_template('admin/branding.html', profil=profil, sliders=sliders)

# --- BANNER SLIDER MANAGEMENT ROUTES (Edit, Hapus, Aktif Tayang) ---
@app.route('/admin/banner-slider/tambah', methods=['POST'])
@superadmin_required
def admin_banner_slider_tambah():
    judul = request.form.get('judul', '').strip()
    deskripsi = request.form.get('deskripsi', '').strip()
    try:
        urutan = int(request.form.get('urutan', 1) or 1)
    except (ValueError, TypeError):
        urutan = 1
    is_active = 1 if request.form.get('is_active') in ['1', 'on', 'true', True] else 0

    gambar = request.form.get('gambar_url', '').strip()
    if 'gambar_file' in request.files:
        file = request.files['gambar_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.svg', '.webp']:
                filename = secure_filename(f"slider_{int(time.time())}_{random.randint(100,999)}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                gambar = f"static/images/uploads/{filename}"

    if not gambar:
        gambar = "static/images/banner1.png"

    if not judul:
        flash('Judul banner slider wajib diisi.', 'danger')
        return redirect(url_for('admin_branding') + '#section-slider')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO banner_slider (judul, deskripsi, gambar, urutan, is_active)
        VALUES (?, ?, ?, ?, ?)
    ''', (judul, deskripsi, gambar, urutan, is_active))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    record_activity_log(
        action='TAMBAH_BANNER_SLIDER',
        details=f'Menambahkan banner slider ID {new_id}: "{judul[:40]}" (Urutan: {urutan}, Status: {"Aktif" if is_active else "Nonaktif"})',
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )

    flash('Banner slider baru berhasil ditambahkan!', 'success')
    return redirect(url_for('admin_branding') + '#section-slider')


@app.route('/admin/banner-slider/<int:id>/edit', methods=['POST'])
@superadmin_required
def admin_banner_slider_edit(id):
    judul = request.form.get('judul', '').strip()
    deskripsi = request.form.get('deskripsi', '').strip()
    try:
        urutan = int(request.form.get('urutan', 1) or 1)
    except (ValueError, TypeError):
        urutan = 1
    is_active = 1 if request.form.get('is_active') in ['1', 'on', 'true', True] else 0

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT gambar, urutan FROM banner_slider WHERE id = ?", (id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        flash('Banner slider tidak ditemukan.', 'danger')
        return redirect(url_for('admin_branding') + '#section-slider')

    gambar = request.form.get('gambar_url', '').strip() or row[0]
    if 'gambar_file' in request.files:
        file = request.files['gambar_file']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.svg', '.webp']:
                filename = secure_filename(f"slider_{id}_{int(time.time())}{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                gambar = f"static/images/uploads/{filename}"

    if not judul:
        conn.close()
        flash('Judul banner slider tidak boleh kosong.', 'danger')
        return redirect(url_for('admin_branding') + '#section-slider')

    cursor.execute('''
        UPDATE banner_slider 
        SET judul = ?, deskripsi = ?, gambar = ?, urutan = ?, is_active = ?
        WHERE id = ?
    ''', (judul, deskripsi, gambar, urutan, is_active, id))
    conn.commit()

    # Sync back to profil_desa if this corresponds to slider 1, 2, or 3
    if urutan == 1:
        cursor.execute("UPDATE profil_desa SET banner_hero_1 = ?, banner_title_1 = ?, banner_desc_1 = ? WHERE id = 1", (gambar, judul, deskripsi))
    elif urutan == 2:
        cursor.execute("UPDATE profil_desa SET banner_hero_2 = ?, banner_title_2 = ?, banner_desc_2 = ? WHERE id = 1", (gambar, judul, deskripsi))
    elif urutan == 3:
        cursor.execute("UPDATE profil_desa SET banner_hero_3 = ?, banner_title_3 = ?, banner_desc_3 = ? WHERE id = 1", (gambar, judul, deskripsi))
    conn.commit()
    conn.close()

    record_activity_log(
        action='EDIT_BANNER_SLIDER',
        details=f'Mengedit banner slider ID {id}: "{judul[:40]}" (Urutan: {urutan}, Status: {"Aktif" if is_active else "Nonaktif"})',
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )

    flash('Banner slider berhasil diperbarui!', 'success')
    return redirect(url_for('admin_branding') + '#section-slider')


@app.route('/admin/banner-slider/<int:id>/toggle', methods=['POST'])
@superadmin_required
def admin_banner_slider_toggle(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE banner_slider SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?", (id,))
    conn.commit()
    cursor.execute("SELECT judul, is_active FROM banner_slider WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        status_str = "diaktifkan (tayang di depan)" if row[1] == 1 else "dinonaktifkan (disembunyikan)"
        flash(f'Banner slider "{row[0][:35]}" berhasil {status_str}.', 'success')
        record_activity_log(
            action='TOGGLE_BANNER_SLIDER',
            details=f'Mengubah status banner slider ID {id} menjadi {"Aktif" if row[1] == 1 else "Nonaktif"}',
            username=session.get('username'),
            user_id=session.get('user_id'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
    return redirect(url_for('admin_branding') + '#section-slider')


@app.route('/admin/banner-slider/<int:id>/hapus', methods=['POST'])
@superadmin_required
def admin_banner_slider_hapus(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT judul FROM banner_slider WHERE id = ?", (id,))
    row = cursor.fetchone()
    judul = row[0] if row else f"ID {id}"
    cursor.execute("DELETE FROM banner_slider WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    record_activity_log(
        action='HAPUS_BANNER_SLIDER',
        details=f'Menghapus banner slider ID {id}: "{judul[:40]}"',
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )

    flash(f'Banner slider "{judul[:35]}" berhasil dihapus.', 'info')
    return redirect(url_for('admin_branding') + '#section-slider')

# ==========================================
# 10. MENU BACKUP & RESTORE DATA (Khusus Super Admin)
# ==========================================

@app.route('/admin/backup')
@superadmin_required
def admin_backup():
    """Halaman Pengelolaan Cadangan & Pemulihan Basis Data"""
    # Ambil daftar file backup di folder backups/
    backup_files = []
    if os.path.exists(app.config['BACKUP_FOLDER']):
        for fname in os.listdir(app.config['BACKUP_FOLDER']):
            fpath = os.path.join(app.config['BACKUP_FOLDER'], fname)
            if os.path.isfile(fpath) and (fname.endswith('.db') or fname.endswith('.zip')):
                stat = os.stat(fpath)
                size_mb = round(stat.st_size / (1024 * 1024), 2)
                size_str = f"{size_mb} MB" if size_mb >= 0.1 else f"{round(stat.st_size / 1024, 1)} KB"
                backup_files.append({
                    'filename': fname,
                    'size': size_str,
                    'created_at': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'is_zip': fname.endswith('.zip')
                })
    
    backup_files.sort(key=lambda x: x['created_at'], reverse=True)

    # Info Database Aktif
    db_size_mb = 0
    if os.path.exists('desa.db'):
        db_size_mb = round(os.path.getsize('desa.db') / (1024 * 1024), 2)

    # Info Direktori Uploads
    uploads_size_mb = 0
    for root, dirs, files in os.walk('static'):
        for f in files:
            fp = os.path.join(root, f)
            if not os.path.islink(fp):
                uploads_size_mb += os.path.getsize(fp)
    uploads_size_mb = round(uploads_size_mb / (1024 * 1024), 2)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    total_tabel = cursor.fetchone()[0] or 0
    conn.close()

    return render_template(
        'admin/backup.html',
        backup_files=backup_files,
        db_size_mb=db_size_mb,
        uploads_size_mb=uploads_size_mb,
        total_tabel=total_tabel
    )

@app.route('/admin/backup/download-db')
@superadmin_required
def admin_backup_download_db():
    """Mengunduh salinan database SQLite secara aman (Instan)"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backup_desa_{timestamp}.db"
    dest_path = os.path.join(app.config['BACKUP_FOLDER'], filename)

    try:
        # Gunakan API SQLite Backup agar salinan konsisten tanpa locking issue
        src = sqlite3.connect('desa.db')
        dst = sqlite3.connect(dest_path)
        with dst:
            src.backup(dst)
        dst.close()
        src.close()

        record_activity_log(
            'BACKUP_DATABASE_DB',
            f"Super Admin mengunduh snapshot database: {filename}",
            username=session.get('username'),
            user_id=session.get('user_id'),
            ip_address=request.headers.get('X-Forwarded-For', request.remote_addr)
        )
        return send_file(dest_path, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f'Gagal mengunduh backup database: {str(e)}', 'danger')
        return redirect(url_for('admin_backup'))

@app.route('/admin/backup/download-zip')
@superadmin_required
def admin_backup_download_zip():
    """Mengunduh paket arsip komplit: Database + Seluruh Berkas Upload Media"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f"backup_komplit_desa_{timestamp}.zip"
    zip_path = os.path.join(app.config['BACKUP_FOLDER'], zip_filename)

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Simpan salinan database aktif
            if os.path.exists('desa.db'):
                zipf.write('desa.db', arcname='desa.db')

            # 2. Simpan folder uploads & media
            for folder_target in [os.path.join('static', 'uploads'), os.path.join('static', 'images', 'uploads'), os.path.join('static', 'docs')]:
                if os.path.exists(folder_target):
                    for root, dirs, files in os.walk(folder_target):
                        for f in files:
                            file_path = os.path.join(root, f)
                            arcname = os.path.relpath(file_path, os.path.dirname(os.path.abspath(__file__)))
                            zipf.write(file_path, arcname=arcname)

        record_activity_log(
            'BACKUP_KOMPLIT_ZIP',
            f"Super Admin mengunduh arsip komplit database & berkas upload: {zip_filename}",
            username=session.get('username'),
            user_id=session.get('user_id'),
            ip_address=request.headers.get('X-Forwarded-For', request.remote_addr)
        )
        return send_file(zip_path, as_attachment=True, download_name=zip_filename)
    except Exception as e:
        flash(f'Gagal membuat arsip komplit: {str(e)}', 'danger')
        return redirect(url_for('admin_backup'))

@app.route('/admin/backup/buat-snapshot', methods=['POST'])
@superadmin_required
def admin_backup_buat_snapshot():
    """Menyimpan snapshot database lokal di server satu-klik"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"snapshot_desa_{timestamp}.db"
    dest_path = os.path.join(app.config['BACKUP_FOLDER'], filename)

    try:
        src = sqlite3.connect('desa.db')
        dst = sqlite3.connect(dest_path)
        with dst:
            src.backup(dst)
        dst.close()
        src.close()

        record_activity_log(
            'CREATE_SNAPSHOT',
            f"Super Admin membuat snapshot lokal: {filename}",
            username=session.get('username'),
            user_id=session.get('user_id'),
            ip_address=request.headers.get('X-Forwarded-For', request.remote_addr)
        )
        flash(f'Snapshot database lokal "{filename}" berhasil dibuat dan tersimpan aman di server!', 'success')
    except Exception as e:
        flash(f'Gagal membuat snapshot database: {str(e)}', 'danger')

    return redirect(url_for('admin_backup'))

@app.route('/admin/backup/restore', methods=['POST'])
@superadmin_required
def admin_backup_restore():
    """Memulihkan basis data dari file cadangan .db dengan verifikasi integritas ketat"""
    if 'backup_file' not in request.files:
        flash('Silakan pilih file database cadangan (.db) untuk dipulihkan.', 'danger')
        return redirect(url_for('admin_backup'))

    file = request.files['backup_file']
    if not file or not file.filename:
        flash('File backup belum dipilih.', 'danger')
        return redirect(url_for('admin_backup'))

    if not file.filename.lower().endswith('.db'):
        flash('Keamanan: Format file ditolak! Hanya file database SQLite (.db) yang diizinkan untuk dipulihkan.', 'danger')
        return redirect(url_for('admin_backup'))

    # 1. Verifikasi Header Biner SQLite3 (Anti-Malicious File)
    header = file.read(16)
    file.seek(0)
    if header != b"SQLite format 3\x00":
        record_activity_log(
            'RESTORE_REJECTED',
            f"Percobaan restore ditolak (File bukan format SQLite3 valid: {file.filename})",
            username=session.get('username'),
            user_id=session.get('user_id'),
            ip_address=request.headers.get('X-Forwarded-For', request.remote_addr)
        )
        flash('Keamanan Ditingkatkan: File yang diunggah bukan database SQLite3 valid atau file mengalami kerusakan integritas.', 'danger')
        return redirect(url_for('admin_backup'))

    temp_path = os.path.join(app.config['BACKUP_FOLDER'], f"temp_restore_{int(time.time())}.db")
    file.save(temp_path)

    # 2. Uji Integritas Database (PRAGMA integrity_check)
    try:
        test_conn = sqlite3.connect(temp_path)
        test_cur = test_conn.cursor()
        test_cur.execute("PRAGMA integrity_check")
        integrity_res = test_cur.fetchone()
        test_conn.close()

        if not integrity_res or integrity_res[0] != 'ok':
            os.remove(temp_path)
            flash('Keamanan: File database gagal uji integritas SQLite (database rusak/corrupt). Pemulihan dibatalkan.', 'danger')
            return redirect(url_for('admin_backup'))
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        flash(f'Gagal memverifikasi database cadangan: {str(e)}', 'danger')
        return redirect(url_for('admin_backup'))

    # 3. Buat Cadangan Pengaman Otomatis (Pre-Restore Safety Backup)
    db_path = 'desa.db'
    safety_backup = os.path.join(app.config['BACKUP_FOLDER'], f"pre_restore_safety_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    try:
        if os.path.exists(db_path):
            shutil.copy2(db_path, safety_backup)

        # 4. Terapkan file cadangan ke database aktif
        shutil.copy2(temp_path, db_path)
        os.remove(temp_path)

        record_activity_log(
            'RESTORE_DATABASE',
            f"Basis data desa berhasil dipulihkan dari file {file.filename}. Cadangan pengaman dibuat di {os.path.basename(safety_backup)}.",
            username=session.get('username'),
            user_id=session.get('user_id'),
            ip_address=request.headers.get('X-Forwarded-For', request.remote_addr)
        )
        flash('Basis data desa berhasil dipulihkan (Restore Sukses)! Cadangan pengaman otomatis telah disimpan di server.', 'success')
    except Exception as e:
        flash(f'Terjadi kendala saat menerapkan pemulihan database: {str(e)}', 'danger')

    return redirect(url_for('admin_backup'))

@app.route('/admin/backup/hapus/<filename>', methods=['POST'])
@superadmin_required
def admin_backup_hapus(filename):
    """Menghapus file cadangan lokal di server"""
    safe_name = secure_filename(filename)
    fpath = os.path.join(app.config['BACKUP_FOLDER'], safe_name)
    if os.path.exists(fpath):
        try:
            os.remove(fpath)
            record_activity_log(
                'DELETE_BACKUP',
                f"Menghapus file cadangan lokal: {safe_name}",
                username=session.get('username'),
                user_id=session.get('user_id'),
                ip_address=request.headers.get('X-Forwarded-For', request.remote_addr)
            )
            flash(f'File cadangan "{safe_name}" berhasil dihapus.', 'info')
        except Exception as e:
            flash(f'Gagal menghapus file cadangan: {str(e)}', 'danger')
    return redirect(url_for('admin_backup'))

# ==========================================
# 11. MANAJEMEN AKUN ADMIN & HAK AKSES (Khusus Super Admin)
# ==========================================

@app.route('/admin/users')
@superadmin_required
def admin_users():
    """Halaman Manajemen Akun Admin & Super Admin"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, nama, role, status, last_login, created_at FROM users ORDER BY id ASC")
    users_list = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return render_template('admin/users.html', users_list=users_list)

@app.route('/admin/users/tambah', methods=['POST'])
@superadmin_required
def admin_users_tambah():
    """Menambah akun admin / operator baru"""
    username = request.form.get('username', '').strip().lower()
    nama = request.form.get('nama', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', 'admin').strip()

    if not (username and nama and password):
        flash('Semua kolom data pengguna wajib diisi.', 'danger')
        return redirect(url_for('admin_users'))

    if len(password) < 6:
        flash('Kata sandi minimal harus 6 karakter demi keamanan akun.', 'warning')
        return redirect(url_for('admin_users'))

    if role not in ['superadmin', 'admin']:
        role = 'admin'

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO users (username, password_hash, nama, role, status)
        VALUES (?, ?, ?, ?, 'aktif')
        ''', (username, generate_password_hash(password), nama, role))
        conn.commit()

        record_activity_log(
            'USER_CREATE',
            f"Super Admin menambahkan akun pengguna baru: {username} ({'Super Admin' if role=='superadmin' else 'Admin Operator'})",
            username=session.get('username'),
            user_id=session.get('user_id'),
            ip_address=request.headers.get('X-Forwarded-For', request.remote_addr)
        )
        flash(f'Akun "{username}" dengan peran {("Super Admin" if role=="superadmin" else "Admin Operator")} berhasil dibuat.', 'success')
    except sqlite3.IntegrityError:
        flash(f'Username "{username}" sudah digunakan akun lain. Silakan pilih username berbeda.', 'warning')
    finally:
        conn.close()

    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:id>/edit', methods=['POST'])
@superadmin_required
def admin_users_edit(id):
    """Mengubah nama, hak akses role, dan status keaktifan akun"""
    nama = request.form.get('nama', '').strip()
    role = request.form.get('role', 'admin').strip()
    status = request.form.get('status', 'aktif').strip()

    if not nama:
        flash('Nama pengguna tidak boleh kosong.', 'danger')
        return redirect(url_for('admin_users'))

    if role not in ['superadmin', 'admin']:
        role = 'admin'
    if status not in ['aktif', 'nonaktif']:
        status = 'aktif'

    # Cegah super admin mendowngrade diri sendiri jika sedang login
    if id == session.get('user_id') and role != 'superadmin':
        flash('Anda tidak dapat mengubah peran Anda sendiri dari Super Admin.', 'warning')
        return redirect(url_for('admin_users'))

    # Cegah menonaktifkan akun sendiri
    if id == session.get('user_id') and status == 'nonaktif':
        flash('Anda tidak dapat menonaktifkan akun Anda sendiri yang sedang aktif digunakan.', 'warning')
        return redirect(url_for('admin_users'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET nama = ?, role = ?, status = ? WHERE id = ?", (nama, role, status, id))
    conn.commit()
    conn.close()

    record_activity_log(
        'USER_EDIT',
        f"Super Admin mengubah data pengguna ID {id}: Role={role}, Status={status}",
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.headers.get('X-Forwarded-For', request.remote_addr)
    )
    flash('Data akun pengguna berhasil diperbarui.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:id>/reset-password', methods=['POST'])
@superadmin_required
def admin_users_reset_password(id):
    """Mereset kata sandi akun pengguna"""
    password_baru = request.form.get('password_baru', '').strip()
    if not password_baru or len(password_baru) < 6:
        flash('Kata sandi baru minimal harus 6 karakter.', 'warning')
        return redirect(url_for('admin_users'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (generate_password_hash(password_baru), id))
    conn.commit()
    cursor.execute("SELECT username FROM users WHERE id = ?", (id,))
    u_row = cursor.fetchone()
    conn.close()

    u_name = u_row['username'] if u_row else f'ID {id}'
    record_activity_log(
        'USER_RESET_PASSWORD',
        f"Super Admin mereset kata sandi untuk akun: {u_name}",
        username=session.get('username'),
        user_id=session.get('user_id'),
        ip_address=request.headers.get('X-Forwarded-For', request.remote_addr)
    )
    flash(f'Kata sandi untuk akun "{u_name}" berhasil direset.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:id>/hapus', methods=['POST'])
@superadmin_required
def admin_users_hapus(id):
    """Menghapus akun admin / operator"""
    if id == session.get('user_id'):
        flash('Anda tidak dapat menghapus akun Anda sendiri.', 'danger')
        return redirect(url_for('admin_users'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users WHERE id = ?", (id,))
    u_row = cursor.fetchone()
    if u_row:
        # Cek jika ini satu-satunya superadmin
        if u_row['role'] == 'superadmin':
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'superadmin'")
            if cursor.fetchone()[0] <= 1:
                conn.close()
                flash('Tidak dapat menghapus satu-satunya akun Super Admin di sistem.', 'danger')
                return redirect(url_for('admin_users'))

        cursor.execute("DELETE FROM users WHERE id = ?", (id,))
        conn.commit()
        record_activity_log(
            'USER_DELETE',
            f"Super Admin menghapus akun: {u_row['username']}",
            username=session.get('username'),
            user_id=session.get('user_id'),
            ip_address=request.headers.get('X-Forwarded-For', request.remote_addr)
        )
        flash(f'Akun "{u_row["username"]}" berhasil dihapus.', 'info')

    conn.close()
    return redirect(url_for('admin_users'))

# ==========================================
# 12. LOG AUDIT & KEAMANAN SISTEM (Khusus Super Admin)
# ==========================================

@app.route('/admin/keamanan')
@superadmin_required
def admin_keamanan():
    """Halaman Monitoring Log Audit Aktivitas & Status Keamanan Siber"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM activity_logs ORDER BY id DESC LIMIT 100")
    logs = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM login_attempts ORDER BY id DESC LIMIT 50")
    attempts = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT COUNT(*) FROM login_attempts WHERE is_success = 0 AND attempted_at >= datetime('now', '-24 hours')")
    failed_24h = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM login_attempts WHERE is_success = 1 AND attempted_at >= datetime('now', '-24 hours')")
    success_24h = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(DISTINCT ip_address) FROM login_attempts WHERE is_success = 0 AND attempted_at >= datetime('now', '-24 hours')")
    suspicious_ips = cursor.fetchone()[0] or 0

    conn.close()

    return render_template(
        'admin/keamanan.html',
        logs=logs,
        attempts=attempts,
        failed_24h=failed_24h,
        success_24h=success_24h,
        suspicious_ips=suspicious_ips
    )

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 8080))
    print("=" * 65)
    print("       PORTAL RESMI WEBSITE DESA - SISTEM AKTIF & TERLINDUNGI")
    print("=" * 65)
    print(f" [FRONTEND PUBLIK]  : http://localhost:{port}")
    print(f"                      http://192.168.2.105:{port} (Akses Jaringan LAN/WiFi)")
    print(f" [BACKEND ADMIN]    : http://localhost:{port}/admin")
    print(f"                      http://192.168.2.105:{port}/admin")
    print(f" [AKUN ADMIN]       : admin / admin123 (Super Admin)")
    print(f"                      operator / operator123 (Staf Pelayanan)")
    print(f" [KEAMANAN SISTEM]  : Aktif (Anti-CSRF, Rate Limiting, HTTP Hardening, CSP)")
    print("=" * 65)
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)

