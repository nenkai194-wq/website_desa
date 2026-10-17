import sqlite3
import json
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'desa.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users / Admin (Super Admin & Admin)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nama TEXT NOT NULL,
        role TEXT DEFAULT 'admin',
        status TEXT DEFAULT 'aktif',
        last_login TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Migration users: pastikan kolom status, last_login, created_at ada
    cursor.execute("PRAGMA table_info(users)")
    cols_users = [col[1] for col in cursor.fetchall()]
    if 'status' not in cols_users:
        cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'aktif'")
    if 'last_login' not in cols_users:
        cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
    if 'created_at' not in cols_users:
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP")
        cursor.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    conn.commit()

    # 1.1 Activity Audit Logs (Log Aktivitas & Audit Keamanan)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        action TEXT NOT NULL,
        details TEXT,
        ip_address TEXT,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 1.2 Login Attempts (Rate Limiting & Anti Brute-Force)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT NOT NULL,
        username TEXT,
        attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_success INTEGER DEFAULT 0
    )
    ''')
    conn.commit()

    # 2. Profil Desa
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS profil_desa (
        id INTEGER PRIMARY KEY,
        judul_website TEXT DEFAULT 'Website Resmi Desa Papayan',
        nama_desa TEXT NOT NULL,
        tagline_website TEXT DEFAULT 'Desa Wisata Pesisir Marang Kayu',
        subtagline_website TEXT DEFAULT 'Penerima Penghargaan Kampung Iklim (Proklim) Utama KLHK RI',
        logo_website TEXT DEFAULT 'static/images/kutaikartanegara.png',
        favicon_website TEXT DEFAULT 'static/images/kutaikartanegara.png',
        kecamatan TEXT NOT NULL,
        kabupaten TEXT NOT NULL,
        provinsi TEXT NOT NULL,
        kode_pos TEXT,
        kode_wilayah TEXT,
        alamat TEXT,
        telepon TEXT,
        email TEXT,
        jam_pelayanan TEXT,
        nama_kades TEXT,
        periode_kades TEXT,
        foto_kades TEXT,
        sambutan_kades TEXT,
        visi TEXT,
        misi TEXT,
        luas_wilayah TEXT,
        koordinat_lat REAL,
        koordinat_lng REAL,
        banner_hero_1 TEXT DEFAULT 'static/images/banner1.png',
        banner_title_1 TEXT DEFAULT 'Selamat Datang di Website Resmi Desa Papayan',
        banner_desc_1 TEXT DEFAULT 'Menjelajahi pesona Pantai Biru Kersik, kelestarian mangrove pesisir, dan kemajuan masyarakat.',
        banner_hero_2 TEXT DEFAULT 'static/images/banner2.png',
        banner_title_2 TEXT DEFAULT 'Penerima Sertifikat Proklim Utama KLHK RI',
        banner_desc_2 TEXT DEFAULT 'Komitmen nyata masyarakat Desa Papayan dalam menjaga kelestarian lingkungan pesisir.',
        banner_hero_3 TEXT DEFAULT 'static/images/pantai_kersik.jpg',
        banner_title_3 TEXT DEFAULT 'Pelayanan Publik Cepat, Transparan dan Akuntabel',
        banner_desc_3 TEXT DEFAULT 'Nikmati kemudahan layanan pengajuan surat online mandiri dan keterbukaan informasi.'
    )
    ''')

    # Migration profil_desa: tambahkan kolom footer dan bagan struktur organisasi jika belum ada
    cursor.execute("PRAGMA table_info(profil_desa)")
    cols_profil = [col[1] for col in cursor.fetchall()]
    if 'teks_footer_deskripsi' not in cols_profil:
        cursor.execute("ALTER TABLE profil_desa ADD COLUMN teks_footer_deskripsi TEXT")
    if 'teks_footer_copyright' not in cols_profil:
        cursor.execute("ALTER TABLE profil_desa ADD COLUMN teks_footer_copyright TEXT")
    if 'teks_footer_portal' not in cols_profil:
        cursor.execute("ALTER TABLE profil_desa ADD COLUMN teks_footer_portal TEXT")
    if 'bagan_struktur_desa' not in cols_profil:
        cursor.execute("ALTER TABLE profil_desa ADD COLUMN bagan_struktur_desa TEXT")
    if 'bagan_struktur_bpd' not in cols_profil:
        cursor.execute("ALTER TABLE profil_desa ADD COLUMN bagan_struktur_bpd TEXT")
    if 'keterangan_bagan_desa' not in cols_profil:
        cursor.execute("ALTER TABLE profil_desa ADD COLUMN keterangan_bagan_desa TEXT")
    if 'keterangan_bagan_bpd' not in cols_profil:
        cursor.execute("ALTER TABLE profil_desa ADD COLUMN keterangan_bagan_bpd TEXT")
    if 'status_maintenance_surat' not in cols_profil:
        cursor.execute("ALTER TABLE profil_desa ADD COLUMN status_maintenance_surat INTEGER DEFAULT 1")
    if 'pesan_maintenance_surat' not in cols_profil:
        cursor.execute("ALTER TABLE profil_desa ADD COLUMN pesan_maintenance_surat TEXT DEFAULT 'Layanan Sedang Maintenace. Mohon maaf atas ketidaknyamananya !!!'")
    conn.commit()

    # 3. Perangkat Desa (SOTK)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS perangkat_desa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        jabatan TEXT NOT NULL,
        periode TEXT DEFAULT '2021 - 2027',
        foto TEXT,
        kontak TEXT,
        sambutan_singkat TEXT,
        urutan INTEGER DEFAULT 0
    )
    ''')

    # Migration: pastikan kolom periode ada di perangkat_desa
    cursor.execute("PRAGMA table_info(perangkat_desa)")
    cols_perangkat = [col[1] for col in cursor.fetchall()]
    if 'periode' not in cols_perangkat:
        cursor.execute("ALTER TABLE perangkat_desa ADD COLUMN periode TEXT")
        cursor.execute("UPDATE perangkat_desa SET periode = ? WHERE periode IS NULL", ('2021 - 2027',))
        conn.commit()

    # 3.1 Jabatan Struktural
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jabatan_struktural (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_jabatan TEXT UNIQUE NOT NULL,
        urutan INTEGER DEFAULT 0
    )
    ''')

    # 4. Berita & Informasi
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS berita (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        judul TEXT NOT NULL,
        kategori TEXT NOT NULL,
        penulis TEXT NOT NULL,
        tanggal TEXT NOT NULL,
        gambar TEXT,
        ringkasan TEXT NOT NULL,
        isi TEXT NOT NULL,
        status TEXT DEFAULT 'Tayang',
        catatan_redaksi TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Migration: pastikan kolom status dan catatan_redaksi ada di berita
    cursor.execute("PRAGMA table_info(berita)")
    cols_berita = [col[1] for col in cursor.fetchall()]
    if 'status' not in cols_berita:
        cursor.execute("ALTER TABLE berita ADD COLUMN status TEXT DEFAULT 'Tayang'")
        cursor.execute("UPDATE berita SET status = 'Tayang' WHERE status IS NULL")
    if 'catatan_redaksi' not in cols_berita:
        cursor.execute("ALTER TABLE berita ADD COLUMN catatan_redaksi TEXT")
    conn.commit()

    # 4.1 Kategori Berita
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kategori_berita (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT UNIQUE NOT NULL,
        urutan INTEGER DEFAULT 0
    )
    ''')

    # 5. Wisata & Potensi
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wisata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        kategori TEXT NOT NULL,
        deskripsi TEXT NOT NULL,
        fasilitas TEXT,
        tiket TEXT,
        lokasi TEXT,
        latitude REAL,
        longitude REAL,
        gambar TEXT,
        urutan INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Disetujui',
        nama_pengaju TEXT,
        kontak_pengaju TEXT,
        catatan_admin TEXT,
        created_at TEXT
    )
    ''')

    # Migration: pastikan kolom latitude, longitude, status, dll ada di wisata
    cursor.execute("PRAGMA table_info(wisata)")
    cols_wisata = [col[1] for col in cursor.fetchall()]
    if 'latitude' not in cols_wisata:
        cursor.execute("ALTER TABLE wisata ADD COLUMN latitude REAL")
    if 'longitude' not in cols_wisata:
        cursor.execute("ALTER TABLE wisata ADD COLUMN longitude REAL")
    if 'status' not in cols_wisata:
        cursor.execute("ALTER TABLE wisata ADD COLUMN status TEXT DEFAULT 'Disetujui'")
        cursor.execute("UPDATE wisata SET status = 'Disetujui' WHERE status IS NULL")
    if 'nama_pengaju' not in cols_wisata:
        cursor.execute("ALTER TABLE wisata ADD COLUMN nama_pengaju TEXT")
    if 'kontak_pengaju' not in cols_wisata:
        cursor.execute("ALTER TABLE wisata ADD COLUMN kontak_pengaju TEXT")
    if 'catatan_admin' not in cols_wisata:
        cursor.execute("ALTER TABLE wisata ADD COLUMN catatan_admin TEXT")
    if 'created_at' not in cols_wisata:
        cursor.execute("ALTER TABLE wisata ADD COLUMN created_at TEXT")
    conn.commit()

    # 6. UMKM & Produk Desa
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS umkm (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        produsen TEXT NOT NULL,
        harga INTEGER NOT NULL,
        satuan TEXT NOT NULL,
        deskripsi TEXT NOT NULL,
        kontak_wa TEXT NOT NULL,
        gambar TEXT,
        gambar2 TEXT,
        gambar3 TEXT,
        rating REAL DEFAULT 4.8,
        terjual INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Disetujui',
        nik_pemilik TEXT,
        catatan_admin TEXT,
        created_at TEXT
    )
    ''')

    # Migration: pastikan kolom gambar2, gambar3, status, nik_pemilik, catatan_admin, created_at ada di umkm
    cursor.execute("PRAGMA table_info(umkm)")
    cols_umkm = [col[1] for col in cursor.fetchall()]
    if 'gambar2' not in cols_umkm:
        cursor.execute("ALTER TABLE umkm ADD COLUMN gambar2 TEXT")
    if 'gambar3' not in cols_umkm:
        cursor.execute("ALTER TABLE umkm ADD COLUMN gambar3 TEXT")
    if 'status' not in cols_umkm:
        cursor.execute("ALTER TABLE umkm ADD COLUMN status TEXT DEFAULT 'Disetujui'")
        cursor.execute("UPDATE umkm SET status = 'Disetujui' WHERE status IS NULL")
    if 'nik_pemilik' not in cols_umkm:
        cursor.execute("ALTER TABLE umkm ADD COLUMN nik_pemilik TEXT")
    if 'catatan_admin' not in cols_umkm:
        cursor.execute("ALTER TABLE umkm ADD COLUMN catatan_admin TEXT")
    if 'created_at' not in cols_umkm:
        cursor.execute("ALTER TABLE umkm ADD COLUMN created_at TEXT")
    conn.commit()

    # 7. Layanan Surat Mandiri
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS layanan_surat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        no_reg TEXT UNIQUE NOT NULL,
        jenis_surat TEXT NOT NULL,
        nik TEXT NOT NULL,
        nama TEXT NOT NULL,
        wa TEXT NOT NULL,
        dusun TEXT NOT NULL,
        rt TEXT NOT NULL,
        keperluan TEXT NOT NULL,
        status TEXT DEFAULT 'Menunggu',
        catatan_admin TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 8. Pengaduan & Aspirasi Warga
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pengaduan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        no_tiket TEXT UNIQUE NOT NULL,
        nama TEXT NOT NULL,
        kontak TEXT NOT NULL,
        kategori TEXT NOT NULL,
        pesan TEXT NOT NULL,
        lampiran TEXT,
        status TEXT DEFAULT 'Belum Ditanggapi',
        tanggapan_admin TEXT,
        uraian_tindak_lanjut TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Migration pengaduan: pastikan lampiran & uraian_tindak_lanjut ada
    cursor.execute("PRAGMA table_info(pengaduan)")
    cols_pengaduan = [col[1] for col in cursor.fetchall()]
    if 'lampiran' not in cols_pengaduan:
        cursor.execute("ALTER TABLE pengaduan ADD COLUMN lampiran TEXT")
    if 'uraian_tindak_lanjut' not in cols_pengaduan:
        cursor.execute("ALTER TABLE pengaduan ADD COLUMN uraian_tindak_lanjut TEXT")
    
    # Standarisasi status aduan: Sudah Diselesaikan, Belum Ditanggapi, Perlu Perlakuan Khusus
    cursor.execute("UPDATE pengaduan SET status = 'Belum Ditanggapi' WHERE status = 'Menunggu' OR status IS NULL")
    cursor.execute("UPDATE pengaduan SET status = 'Sudah Diselesaikan' WHERE status = 'Selesai'")
    cursor.execute("UPDATE pengaduan SET status = 'Perlu Perlakuan Khusus' WHERE status = 'Diproses'")
    cursor.execute("UPDATE pengaduan SET uraian_tindak_lanjut = tanggapan_admin WHERE uraian_tindak_lanjut IS NULL AND tanggapan_admin IS NOT NULL")
    conn.commit()

    # 8.1 Kategori Pengaduan & Aspirasi Warga
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kategori_pengaduan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT UNIQUE NOT NULL,
        keterangan TEXT,
        urutan INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()

    # 9. APBDes Transparansi
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS apbdes (
        id INTEGER PRIMARY KEY,
        tahun INTEGER NOT NULL,
        pendapatan_total INTEGER NOT NULL,
        belanja_total INTEGER NOT NULL,
        pembiayaan_netto INTEGER NOT NULL,
        data_sumber_json TEXT,
        data_belanja_json TEXT
    )
    ''')

    # 10. Statistik Kependudukan
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statistik (
        id INTEGER PRIMARY KEY,
        tahun INTEGER DEFAULT 2026,
        total_penduduk INTEGER NOT NULL,
        laki_laki INTEGER NOT NULL,
        perempuan INTEGER NOT NULL,
        kepala_keluarga INTEGER NOT NULL,
        penduduk_sementara INTEGER NOT NULL,
        mutasi_penduduk INTEGER NOT NULL,
        data_usia_json TEXT,
        data_pekerjaan_json TEXT
    )
    ''')

    # Migration: pastikan kolom tahun ada di statistik
    cursor.execute("PRAGMA table_info(statistik)")
    cols_stat = [col[1] for col in cursor.fetchall()]
    if 'tahun' not in cols_stat:
        cursor.execute("ALTER TABLE statistik ADD COLUMN tahun INTEGER DEFAULT 2026")
        cursor.execute("UPDATE statistik SET tahun = 2026 WHERE tahun IS NULL")
        conn.commit()

    # 10b. Statistik SLS (Satuan Lingkungan Setempat / RT-RW) Per Tahun Series
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statistik_sls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tahun INTEGER NOT NULL,
        no_urut INTEGER,
        nama_sls TEXT NOT NULL,
        laki_laki INTEGER DEFAULT 0,
        perempuan INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        keluarga INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    # Migration: pastikan kolom geo ada di statistik_sls
    cursor.execute("PRAGMA table_info(statistik_sls)")
    cols_sls = [col[1] for col in cursor.fetchall()]
    if 'latitude' not in cols_sls:
        cursor.execute("ALTER TABLE statistik_sls ADD COLUMN latitude REAL")
    if 'longitude' not in cols_sls:
        cursor.execute("ALTER TABLE statistik_sls ADD COLUMN longitude REAL")
    if 'dusun' not in cols_sls:
        cursor.execute("ALTER TABLE statistik_sls ADD COLUMN dusun TEXT")
    if 'nama_lengkap' not in cols_sls:
        cursor.execute("ALTER TABLE statistik_sls ADD COLUMN nama_lengkap TEXT")

    # Migration: pastikan kml_url ada di profil_desa
    cursor.execute("PRAGMA table_info(profil_desa)")
    cols_profil = [col[1] for col in cursor.fetchall()]
    if 'kml_url' not in cols_profil:
        cursor.execute("ALTER TABLE profil_desa ADD COLUMN kml_url TEXT")

    # 10c. Statistik Penduduk Berdasarkan Kelompok Umur Per Tahun Series
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statistik_umur (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tahun INTEGER NOT NULL,
        no_urut INTEGER,
        kelompok_umur TEXT NOT NULL,
        laki_laki INTEGER DEFAULT 0,
        perempuan INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 10d. Statistik Penduduk Berdasarkan Tingkat Pendidikan Per SLS (RT/RW)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statistik_pendidikan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tahun INTEGER NOT NULL,
        no_urut INTEGER,
        nama_sls TEXT NOT NULL,
        tidak_sekolah INTEGER DEFAULT 0,
        sd INTEGER DEFAULT 0,
        mi INTEGER DEFAULT 0,
        paket_a INTEGER DEFAULT 0,
        sdlb INTEGER DEFAULT 0,
        spm_ula INTEGER DEFAULT 0,
        smp INTEGER DEFAULT 0,
        mts INTEGER DEFAULT 0,
        smp_lb INTEGER DEFAULT 0,
        paket_b INTEGER DEFAULT 0,
        spm_wustha INTEGER DEFAULT 0,
        sma INTEGER DEFAULT 0,
        smk INTEGER DEFAULT 0,
        ma INTEGER DEFAULT 0,
        mak INTEGER DEFAULT 0,
        sma_lb INTEGER DEFAULT 0,
        paket_c INTEGER DEFAULT 0,
        spm_ulya INTEGER DEFAULT 0,
        diploma INTEGER DEFAULT 0,
        s1 INTEGER DEFAULT 0,
        profesi INTEGER DEFAULT 0,
        s2 INTEGER DEFAULT 0,
        s3 INTEGER DEFAULT 0,
        jumlah INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 10e. Statistik Penduduk Berdasarkan Status Perkawinan Per SLS (RT/RW)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statistik_perkawinan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tahun INTEGER NOT NULL,
        no_urut INTEGER,
        nama_sls TEXT NOT NULL,
        belum_kawin INTEGER DEFAULT 0,
        kawin INTEGER DEFAULT 0,
        cerai_hidup INTEGER DEFAULT 0,
        cerai_mati INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 10f. Statistik Penduduk Berstatus Kawin Berdasarkan Status Pencatatan Perkawinan Per SLS (RT/RW)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statistik_pencatatan_nikah (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tahun INTEGER NOT NULL,
        no_urut INTEGER,
        nama_sls TEXT NOT NULL,
        kawin_tercatat INTEGER DEFAULT 0,
        kawin_belum_tercatat INTEGER DEFAULT 0,
        kawin_tidak_tercatat INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 10g. Statistik Penduduk Menurut Agama dan Kepercayaannya Per SLS (RT/RW)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statistik_agama (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tahun INTEGER NOT NULL,
        no_urut INTEGER,
        nama_sls TEXT NOT NULL,
        islam INTEGER DEFAULT 0,
        kristen INTEGER DEFAULT 0,
        katholik INTEGER DEFAULT 0,
        budha INTEGER DEFAULT 0,
        hindu INTEGER DEFAULT 0,
        konghucu INTEGER DEFAULT 0,
        kepercayaan_lainnya INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 10h. Statistik Penerima Bantuan Sosial (Bansos) Per SLS (RT/RW)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statistik_bansos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tahun INTEGER NOT NULL,
        no_urut INTEGER,
        nama_sls TEXT NOT NULL,
        pkh INTEGER DEFAULT 0,
        bpnt INTEGER DEFAULT 0,
        bos INTEGER DEFAULT 0,
        bapanas INTEGER DEFAULT 0,
        stunting INTEGER DEFAULT 0,
        pbi_jkn INTEGER DEFAULT 0,
        blt INTEGER DEFAULT 0,
        blt_dd INTEGER DEFAULT 0,
        lainnya INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 10i. Statistik Status Keberadaan Orang Tua Anak (Anak Yatim, Piatu, Yatim Piatu) Per SLS (RT/RW)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statistik_anak (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tahun INTEGER NOT NULL,
        no_urut INTEGER,
        nama_sls TEXT NOT NULL,
        anak_yatim INTEGER DEFAULT 0,
        anak_piatu INTEGER DEFAULT 0,
        yatim_piatu INTEGER DEFAULT 0,
        orang_tua_lengkap INTEGER DEFAULT 0,
        total_anak INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 10j. Statistik Anak Gizi Buruk Per SLS (RT/RW)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statistik_gizi_buruk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tahun INTEGER NOT NULL,
        no_urut INTEGER,
        nama_sls TEXT NOT NULL,
        anak_gizi_buruk INTEGER DEFAULT 0,
        jumlah_anak_balita INTEGER DEFAULT 0,
        persentase REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Migration gizi buruk
    cursor.execute("PRAGMA table_info(statistik_gizi_buruk)")
    cols_gz = [c[1] for c in cursor.fetchall()]
    if 'jumlah_anak_balita' not in cols_gz:
        cursor.execute("ALTER TABLE statistik_gizi_buruk ADD COLUMN jumlah_anak_balita INTEGER DEFAULT 0")
    if 'persentase' not in cols_gz:
        cursor.execute("ALTER TABLE statistik_gizi_buruk ADD COLUMN persentase REAL DEFAULT 0.0")

    # 10k. Statistik Anak Stunting Per SLS (RT/RW)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statistik_stunting (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tahun INTEGER NOT NULL,
        no_urut INTEGER,
        nama_sls TEXT NOT NULL,
        anak_stunting INTEGER DEFAULT 0,
        jumlah_anak_balita INTEGER DEFAULT 0,
        persentase REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Migration stunting
    cursor.execute("PRAGMA table_info(statistik_stunting)")
    cols_st = [c[1] for c in cursor.fetchall()]
    if 'jumlah_anak_balita' not in cols_st:
        cursor.execute("ALTER TABLE statistik_stunting ADD COLUMN jumlah_anak_balita INTEGER DEFAULT 0")
    if 'persentase' not in cols_st:
        cursor.execute("ALTER TABLE statistik_stunting ADD COLUMN persentase REAL DEFAULT 0.0")


    # 11. Buku Publikasi Desa
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS buku_publikasi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        judul TEXT NOT NULL,
        kategori TEXT NOT NULL,
        penulis TEXT DEFAULT 'Pemerintah Desa',
        tahun TEXT DEFAULT '2026',
        edisi TEXT DEFAULT 'Edisi Tahunan',
        jumlah_halaman INTEGER DEFAULT 0,
        ukuran_file TEXT DEFAULT '0 MB',
        sinopsis TEXT,
        cover_buku TEXT,
        file_pdf TEXT NOT NULL,
        jumlah_unduh INTEGER DEFAULT 0,
        jumlah_baca INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Tayang',
        is_featured INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Migration: pastikan kolom jumlah_baca ada di buku_publikasi
    cursor.execute("PRAGMA table_info(buku_publikasi)")
    cols_buku = [col[1] for col in cursor.fetchall()]
    if 'jumlah_baca' not in cols_buku:
        cursor.execute("ALTER TABLE buku_publikasi ADD COLUMN jumlah_baca INTEGER DEFAULT 0")
        cursor.execute("UPDATE buku_publikasi SET jumlah_baca = 0 WHERE jumlah_baca IS NULL")
        conn.commit()

    # 11.1 Kategori Buku Publikasi
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kategori_publikasi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT UNIQUE NOT NULL,
        urutan INTEGER DEFAULT 0
    )
    ''')

    conn.commit()

    # Seed Admin Users (Super Admin & Admin) if not exists
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO users (username, password_hash, nama, role, status)
        VALUES (?, ?, ?, 'superadmin', 'aktif')
        ''', ('admin', generate_password_hash('admin123'), 'Kepala Desa / Super Admin'))
    else:
        cursor.execute("UPDATE users SET role = 'superadmin' WHERE username = 'admin'")

    cursor.execute("SELECT id FROM users WHERE username = 'operator'")
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO users (username, password_hash, nama, role, status)
        VALUES (?, ?, ?, 'admin', 'aktif')
        ''', ('operator', generate_password_hash('operator123'), 'Staf Pelayanan / Operator Desa'))
    conn.commit()

    # Seed Profil Desa if not exists
    cursor.execute("SELECT COUNT(*) FROM profil_desa")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO profil_desa (
            id, nama_desa, kecamatan, kabupaten, provinsi, kode_pos, kode_wilayah,
            alamat, telepon, email, jam_pelayanan, nama_kades, periode_kades,
            foto_kades, sambutan_kades, visi, misi, luas_wilayah, koordinat_lat, koordinat_lng
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            1, "Kersik", "Marang Kayu", "Kutai Kartanegara", "Kalimantan Timur",
            "75385", "64.02.17.2005", "Jalan Langaseng Dusun Empang RT.003, Desa Papayan",
            "0821-5020-8664", "pemdes@kersik.desa.id",
            "Senin - Kamis (08.00 - 15.00) & Jum'at (08.00 - 11.00) WITA",
            "Jumadi, S.Sos", "2021 - 2027", "static/images/kades.jpg",
            "Selamat Datang di Portal Resmi Informasi & Pelayanan Publik Desa Papayan. Kami berkomitmen mewujudkan keterbukaan informasi, pelayanan cepat bebas calo, dan optimalisasi potensi wisata Pantai Biru Kersik serta konservasi mangrove berkelanjutan.",
            "Terwujudnya Desa Papayan yang Maju, Sejahtera, Transparan, Berbasis Wisata Bahari dan Lingkungan Hidup Lestari.",
            "1. Meningkatkan pelayanan publik prima berbasis teknologi digital.\n2. Mengembangkan potensi pariwisata bahari Pantai Biru Kersik dan ekonomi kreatif pesisir.\n3. Menjaga kelestarian ekosistem mangrove dan prestasi Program Kampung Iklim (Proklim).\n4. Meningkatkan kapasitas ekonomi nelayan dan pemberdayaan UMKM lokal.",
            "42,85 km²", -0.0682, 117.3854
        ))
        conn.commit()

    # Seed Perangkat Desa
    cursor.execute("SELECT COUNT(*) FROM perangkat_desa")
    if cursor.fetchone()[0] == 0:
        aparaturs = [
            ("Jumadi, S.Sos", "Kepala Desa Papayan", "static/images/kades.jpg", "0821-5020-8664", "Mewujudkan Desa Papayan yang Maju, Sejahtera, Transparan, Berbasis Wisata Bahari.", 1),
            ("Rahmat Hidayat, S.P", "Sekretaris Desa", "static/images/sekdes.jpg", "0812-4455-8899", "Mendukung tata kelola administrasi pemerintahan desa yang akuntabel dan cepat.", 2),
            ("Siti Aminah, A.Md", "Kaur Keuangan", "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&auto=format&fit=crop&q=80", "0823-1122-3344", "Menjaga transparansi dan akuntabilitas pengelolaan APBDes demi pembangunan nyata.", 3),
            ("Muhammad Yusuf", "Kasi Pemerintahan", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80", "0852-3344-5566", "Melayani tertib administrasi kependudukan dan pertanahan secara ramah dan profesional.", 4),
            ("Fatimah Azzahra, S.Pd", "Kasi Kesejahteraan & Pelayanan", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80", "0813-7788-9900", "Mendorong pemberdayaan sosial, posyandu, dan layanan masyarakat umum.", 5),
            ("Baharuddin, S.T", "Kaur Umum & Perencanaan", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80", "0821-9988-7766", "Perencanaan infrastruktur fisik terpadu: jalan pesisir dan dermaga nelayan.", 6),
            ("H. Syamsir", "Kepala Dusun Empang", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&auto=format&fit=crop&q=80", "0813-1234-5678", "Mengawal keharmonisan warga dan pembangunan di kawasan Dusun Empang.", 7),
            ("Rustam Efendi", "Kepala Dusun Kersik", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&auto=format&fit=crop&q=80", "0853-2233-4455", "Membangun gotong royong dan kemitraan kelompok nelayan pesisir Dusun Kersik.", 8)
        ]
        cursor.executemany('''
        INSERT INTO perangkat_desa (nama, jabatan, foto, kontak, sambutan_singkat, urutan)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', aparaturs)
        conn.commit()

    # Seed Jabatan Struktural
    cursor.execute("SELECT COUNT(*) FROM jabatan_struktural")
    if cursor.fetchone()[0] == 0:
        default_jabatans = [
            ("Kepala Desa", 1),
            ("Sekretaris Desa", 2),
            ("Kaur Keuangan", 3),
            ("Kasi Pemerintahan", 4),
            ("Kasi Kesejahteraan", 5),
            ("Kasi Pelayanan", 6),
            ("Kaur Umum & Perencanaan", 7),
            ("Kaur Tata Usaha & Umum", 8),
            ("Kaur Perencanaan", 9),
            ("Kepala Dusun", 10),
            ("Ketua BPD", 11),
            ("Anggota BPD", 12),
            ("Ketua LPM", 13),
            ("Staf Administrasi Desa", 14),
        ]
        # Also include all existing distinct positions in perangkat_desa
        cursor.execute("SELECT DISTINCT jabatan FROM perangkat_desa WHERE jabatan IS NOT NULL AND jabatan != ''")
        for row in cursor.fetchall():
            jab = row[0].strip()
            if not any(j[0].lower() == jab.lower() for j in default_jabatans):
                default_jabatans.append((jab, 20))

        for nama_j, urut in default_jabatans:
            cursor.execute("INSERT OR IGNORE INTO jabatan_struktural (nama_jabatan, urutan) VALUES (?, ?)", (nama_j, urut))
        conn.commit()

    # Seed Wisata
    cursor.execute("SELECT COUNT(*) FROM wisata")
    if cursor.fetchone()[0] == 0:
        destinasi = [
            ("Pantai Biru Kersik (Pantai Kersik)", "Wisata Bahari Unggulan",
             "Ikon pariwisata bahari Desa Papayan yang berbatasan langsung dengan Selat Makassar. Menampilkan bentangan pasir bersih, deretan cemara laut rindang, dan jembatan kayu estetik yang menjorok ke laut.",
             "Jembatan Foto Laut, Camping Ground, Saung Santai, Warung Kuliner, Toilet, Homestay",
             "Rp 5.000 / orang", "Pesisir Selat Makassar, Dusun Kersik", "static/images/pantai_kersik.jpg", 1),
            ("Ekowisata & Konservasi Mangrove Kersik", "Ekowisata Lingkungan (Proklim)",
             "Kawasan hutan bakau rimbun penahan abrasi pantai yang dikelola swadaya oleh Pokdarwis dan Pemdes Papayan. Menghantarkan Desa Papayan meraih penghargaan Kampung Iklim (Proklim) Utama dari KLHK RI.",
             "Track Kayu Susur Mangrove, Pusat Pembibitan Bakau, Spot Bird Watching, Edukasi Adopsi Mangrove",
             "Gratis / Donasi Bibit", "Kawasan Pesisir Muara, Desa Papayan", "static/images/mangrove.jpg", 2),
            ("Kampung Nelayan & Wisata Tambak", "Wisata Budidaya & Pemancingan",
             "Menyajikan pengalaman memancing air payau, melihat budidaya udang windu dan ikan bandeng, serta proses tradisional pembuatan ikan asin dan terasi khas pesisir Kutai Kartanegara.",
             "Spot Pemancingan, Sewa Perahu Nelayan, Warung Ikan Bakar Segar, Pusat Pengolahan Ikan",
             "Sesuai aktivitas sewa", "Dusun Empang & Muara Kersik", "static/images/tambak.jpg", 3)
        ]
        cursor.executemany('''
        INSERT INTO wisata (nama, kategori, deskripsi, fasilitas, tiket, lokasi, gambar, urutan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', destinasi)
        conn.commit()

    # Seed UMKM
    cursor.execute("SELECT COUNT(*) FROM umkm")
    if cursor.fetchone()[0] == 0:
        produk = [
            ("Terasi Udang Rebon Asli Kersik (Khas Marang Kayu)", "KWT Melati Pesisir Kersik", 25000, "Pack 250gr",
             "Dibuat dari 100% udang rebon tangkapan nelayan Desa Papayan, diolah alami tanpa bahan kimia, harum gurih dan legit.", "6282150208664", "static/images/produk_terasi.jpg", 4.9, 450),
            ("Kerupuk Ikan Tenggiri Gurih Renyah", "UMKM Pesisir Berkah Kersik", 20000, "Bungkus 200gr",
             "Olahan ikan tenggiri segar hasil laut Selat Makassar. Renyah, gurih nikmat untuk oleh-oleh khas Kukar.", "6282150208664", "static/images/produk_kerupuk.jpg", 4.8, 380),
            ("Ikan Asin Kering Super (Tenggiri & Biawan)", "Kelompok Nelayan Dusun Empang", 45000, "Pack 500gr",
             "Ikan segar tangkapan harian yang dikeringkan di bawah sinar matahari alami pesisir. Tebal dan gurih.", "6282150208664", "static/images/nelayan.jpg", 4.9, 290),
            ("Souvenir Kerajinan Kerang & Miniatur Perahu", "Karang Taruna Bahari Kersik", 35000, "Pcs",
             "Karya seni tangan pemuda desa memanfaatkan limbah kerang pesisir menjadi hiasan rumah estetik.", "6282150208664", "https://images.unsplash.com/photo-1544816155-12df9643f363?w=800&auto=format&fit=crop&q=80", 4.7, 120)
        ]
        cursor.executemany('''
        INSERT INTO umkm (nama, produsen, harga, satuan, deskripsi, kontak_wa, gambar, rating, terjual)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', produk)
        conn.commit()

    # Seed Berita
    cursor.execute("SELECT COUNT(*) FROM berita")
    if cursor.fetchone()[0] == 0:
        news = [
            ("Pemdes Papayan Gelar Gerakan Tanam 1.000 Mangrove Perkuat Ketahanan Proklim Pesisir", "Lingkungan & Wisata", "Humas Pemdes Papayan", "12 Oktober 2026", "static/images/mangrove.jpg",
             "Sebagai peraih penghargaan Proklim Utama KLHK, warga bersama Pokdarwis dan pelajar menanam 1.000 bibit mangrove di pesisir Selat Makassar.",
             "Desa Papayan kembali menegaskan komitmennya dalam menjaga kelestarian ekosistem bahari. Pada Minggu pagi, Pemerintah Desa Papayan bersama Dinas Lingkungan Hidup Kabupaten Kutai Kartanegara dan ratusan warga Dusun Empang menggelar aksi penanaman 1.000 bibit mangrove jenis Rhizophora di area bibir pantai. Kepala Desa Papayan, Jumadi S.Sos, menyatakan bahwa gerakan ini menjaga keberlanjutan penghargaan Kampung Iklim (Proklim) Utama sekaligus mencegah bahaya abrasi bagi pemukiman nelayan."),
            ("Kunjungan Wisatawan Pantai Biru Kersik Meningkat Pesat pada Akhir Pekan", "Pariwisata Desa", "Pokdarwis Kersik", "04 Oktober 2026", "static/images/pantai_kersik.jpg",
             "Pantai Biru Kersik menjadi primadona wisata keluarga asal Samarinda dan Bontang berkat jembatan laut dan suasana cemara yang asri.",
             "Pantai Biru Kersik terus menarik animo pelancong dari berbagai kabupaten/kota di Kalimantan Timur. Akses jalan yang semakin mulus dari simpang Marang Kayu membuat wisatawan dari Bontang, Samarinda, dan Tenggarong berbondong-bondong datang berkemah dan menikmati kuliner laut bakar segar di saung-saung Pokdarwis. Pihak Pemdes juga terus melengkapi fasilitas sanitasi dan tempat ibadah di kawasan pantai."),
            ("Penyaluran BLT Dana Desa dan Bantuan Alat Tangkap Nelayan Berjalan Lancar", "Pemerintahan & Sosial", "Kasi Kesejahteraan", "25 September 2026", "static/images/kantor_desa.jpg",
             "Sebanyak 65 KPM menerima BLT triwulan ketiga dan 20 kelompok nelayan menerima jaring ramah lingkungan di Balai Pertemuan Desa.",
             "Transparansi dan ketepatan sasaran penyaluran bantuan sosial senantiasa menjadi prioritas utama Pemdes Papayan. Bertempat di Balai Pertemuan Kantor Desa Papayan, BPD dan Pendamping Desa turut mengawasi penyerahan bantuan tunai bersumber dari Dana Desa tahun 2026 serta alat kelengkapan keselamatan bagi nelayan tangkap tradisional.")
        ]
        cursor.executemany('''
        INSERT INTO berita (judul, kategori, penulis, tanggal, gambar, ringkasan, isi)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', news)
        conn.commit()

    # Seed Kategori Berita
    cursor.execute("SELECT COUNT(*) FROM kategori_berita")
    if cursor.fetchone()[0] == 0:
        default_kategori = [
            ("Pemerintahan & Sosial", 1),
            ("Lingkungan & Wisata", 2),
            ("Pariwisata Desa", 3),
            ("Pembangunan & Infrastruktur", 4),
            ("Ekonomi & UMKM", 5),
            ("Pengumuman & Agenda", 6),
        ]
        cursor.execute("SELECT DISTINCT kategori FROM berita WHERE kategori IS NOT NULL AND kategori != ''")
        for row in cursor.fetchall():
            kat = row[0].strip()
            if not any(k[0].lower() == kat.lower() for k in default_kategori):
                default_kategori.append((kat, len(default_kategori) + 1))

        for nama_k, urut in default_kategori:
            cursor.execute("INSERT OR IGNORE INTO kategori_berita (nama, urutan) VALUES (?, ?)", (nama_k, urut))
        conn.commit()

    # Seed APBDes
    cursor.execute("SELECT COUNT(*) FROM apbdes")
    if cursor.fetchone()[0] == 0:
        sumber = [
            {"sumber": "Dana Desa (APBN)", "nominal": 1120000000, "persen": 44.1},
            {"sumber": "Alokasi Dana Desa (ADD Kukar)", "nominal": 980000000, "persen": 38.6},
            {"sumber": "Bagi Hasil Pajak & Retribusi Daerah", "nominal": 220000000, "persen": 8.7},
            {"sumber": "Pendapatan Asli Desa (BUMDes & Wisata)", "nominal": 140000000, "persen": 5.5},
            {"sumber": "Bantuan Keuangan Provinsi / CSR", "nominal": 80000000, "persen": 3.1}
        ]
        belanja = [
            {"bidang": "Penyelenggaraan Pemerintahan Desa", "nominal": 780000000, "persen": 31.3},
            {"bidang": "Pelaksanaan Pembangunan Desa (Pesisir)", "nominal": 990000000, "persen": 39.8},
            {"bidang": "Pembinaan Kemasyarakatan Desa", "nominal": 260000000, "persen": 10.4},
            {"bidang": "Pemberdayaan Masyarakat (Pelatihan Nelayan & UMKM)", "nominal": 340000000, "persen": 13.7},
            {"bidang": "Penanggulangan Bencana & Darurat", "nominal": 120000000, "persen": 4.8}
        ]
        cursor.execute('''
        INSERT INTO apbdes (id, tahun, pendapatan_total, belanja_total, pembiayaan_netto, data_sumber_json, data_belanja_json)
        VALUES (1, 2026, 2540000000, 2490000000, 50000000, ?, ?)
        ''', (json.dumps(sumber), json.dumps(belanja)))
        conn.commit()

    # Seed Statistik & SLS (Satuan Lingkungan Setempat)
    sample_sls_2026 = [
        (2026, 1, "RT 001 RW 001", 88, 97, 185, 63),
        (2026, 2, "RT 002 RW 001", 121, 116, 237, 81),
        (2026, 3, "RT 003 RW 001", 125, 119, 244, 92),
        (2026, 4, "RT 004 RW 001", 96, 101, 197, 67),
        (2026, 5, "RT 005 RW 001", 69, 52, 121, 42),
        (2026, 6, "RT 001 RW 002", 61, 54, 115, 46),
        (2026, 7, "RT 002 RW 002", 75, 73, 148, 51),
        (2026, 8, "RT 003 RW 002", 73, 74, 147, 54),
        (2026, 9, "RT 004 RW 002", 87, 68, 155, 62),
        (2026, 10, "RT 001 RW 003", 147, 135, 282, 94),
        (2026, 11, "RT 002 RW 003", 115, 114, 229, 80),
        (2026, 12, "RT 001 RW 004", 116, 116, 232, 92),
        (2026, 13, "RT 002 RW 004", 89, 100, 189, 70),
        (2026, 14, "RT 003 RW 004", 115, 101, 216, 85),
        (2026, 15, "RT 001 RW 005", 115, 125, 240, 84),
        (2026, 16, "RT 002 RW 005", 101, 83, 184, 69),
        (2026, 17, "RT 003 RW 005", 111, 114, 225, 78),
        (2026, 18, "RT 004 RW 005", 139, 114, 253, 85),
        (2026, 19, "RT 001 RW 006", 74, 78, 152, 54),
        (2026, 20, "RT 002 RW 006", 72, 67, 139, 52),
        (2026, 21, "RT 003 RW 006", 45, 47, 92, 34),
        (2026, 22, "RT 001 RW 007", 96, 102, 198, 67),
        (2026, 23, "RT 002 RW 007", 97, 94, 191, 69),
        (2026, 24, "RT 001 RW 008", 96, 81, 177, 59),
        (2026, 25, "RT 002 RW 008", 86, 85, 171, 57),
        (2026, 26, "RT 003 RW 008", 95, 84, 179, 61),
    ]

    cursor.execute("SELECT COUNT(*) FROM statistik_sls WHERE tahun = 2026")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO statistik_sls (tahun, no_urut, nama_sls, laki_laki, perempuan, total, keluarga)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_sls_2026)
        conn.commit()

    # Seed Statistik Kelompok Umur (Piramida Penduduk 2026)
    sample_umur_2026 = [
        (2026, 1, "0 - 4", 121, 138, 259),
        (2026, 2, "5 - 9", 165, 137, 302),
        (2026, 3, "10 - 14", 191, 166, 357),
        (2026, 4, "15 - 19", 188, 198, 386),
        (2026, 5, "20 - 24", 204, 162, 366),
        (2026, 6, "25 - 29", 215, 173, 388),
        (2026, 7, "30 - 34", 162, 183, 345),
        (2026, 8, "35 - 39", 153, 123, 276),
        (2026, 9, "40 - 44", 143, 150, 293),
        (2026, 10, "45 - 49", 149, 180, 329),
        (2026, 11, "50 - 54", 192, 166, 358),
        (2026, 12, "54 - 59", 163, 180, 343),
        (2026, 13, "60 - 64", 174, 143, 317),
        (2026, 14, "65 - 69", 121, 120, 241),
        (2026, 15, "70 - 74", 66, 81, 147),
        (2026, 16, "75+", 97, 94, 191),
    ]

    cursor.execute("SELECT COUNT(*) FROM statistik_umur WHERE tahun = 2026")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO statistik_umur (tahun, no_urut, kelompok_umur, laki_laki, perempuan, total)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_umur_2026)
        conn.commit()

    # Seed Statistik Penduduk Berdasarkan Tingkat Pendidikan (2026) dari data resmi Pemerintah Desa Papayan
    sample_pendidikan_2026 = [
        (2026, 1, 'RT 001 RW 001', 17, 62, 0, 0, 0, 0, 23, 2, 0, 0, 0, 44, 4, 0, 0, 0, 0, 0, 1, 17, 0, 0, 0, 170),
        (2026, 2, 'RT 002 RW 001', 24, 52, 0, 0, 0, 0, 30, 1, 0, 2, 0, 59, 11, 1, 0, 0, 1, 0, 3, 27, 0, 0, 0, 211),
        (2026, 3, 'RT 003 RW 001', 14, 67, 0, 0, 0, 0, 34, 0, 0, 0, 0, 61, 7, 0, 0, 0, 3, 0, 4, 26, 0, 1, 0, 217),
        (2026, 4, 'RT 004 RW 001', 16, 92, 0, 0, 0, 0, 43, 0, 0, 0, 0, 24, 0, 0, 0, 0, 0, 0, 1, 4, 0, 1, 0, 181),
        (2026, 5, 'RT 005 RW 001', 10, 33, 0, 0, 0, 0, 19, 0, 0, 0, 0, 34, 3, 0, 0, 0, 1, 0, 1, 4, 0, 0, 0, 105),
        (2026, 6, 'RT 001 RW 002', 11, 50, 0, 0, 0, 0, 21, 0, 0, 0, 0, 15, 4, 1, 0, 0, 1, 0, 0, 6, 0, 2, 0, 111),
        (2026, 7, 'RT 002 RW 002', 34, 45, 0, 0, 0, 0, 37, 0, 0, 0, 0, 17, 5, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0, 142),
        (2026, 8, 'RT 003 RW 002', 40, 28, 0, 0, 0, 0, 39, 0, 0, 0, 0, 8, 6, 0, 0, 0, 1, 0, 3, 2, 0, 1, 0, 128),
        (2026, 9, 'RT 004 RW 002', 30, 51, 0, 0, 0, 0, 27, 0, 0, 0, 0, 25, 5, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0, 142),
        (2026, 10, 'RT 001 RW 003', 92, 38, 0, 0, 0, 0, 56, 0, 0, 1, 0, 51, 12, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 253),
        (2026, 11, 'RT 002 RW 003', 62, 29, 0, 0, 0, 0, 51, 0, 0, 0, 0, 38, 13, 0, 0, 0, 0, 0, 2, 6, 0, 0, 0, 201),
        (2026, 12, 'RT 001 RW 004', 13, 121, 0, 0, 0, 0, 37, 0, 0, 0, 0, 29, 11, 0, 0, 0, 0, 0, 1, 10, 0, 0, 0, 222),
        (2026, 13, 'RT 002 RW 004', 18, 78, 0, 0, 0, 0, 20, 0, 0, 0, 0, 30, 18, 3, 0, 0, 0, 0, 2, 11, 0, 1, 0, 181),
        (2026, 14, 'RT 003 RW 004', 16, 93, 0, 0, 0, 0, 25, 0, 0, 0, 0, 32, 8, 3, 0, 0, 0, 0, 5, 14, 0, 3, 0, 199),
        (2026, 15, 'RT 001 RW 005', 55, 71, 1, 0, 0, 0, 32, 3, 0, 0, 0, 24, 16, 1, 0, 0, 0, 0, 4, 15, 0, 0, 0, 222),
        (2026, 16, 'RT 002 RW 005', 34, 54, 0, 0, 0, 0, 30, 3, 0, 0, 0, 23, 15, 1, 0, 0, 0, 0, 0, 11, 0, 0, 0, 171),
        (2026, 17, 'RT 003 RW 005', 24, 110, 0, 0, 0, 0, 33, 0, 0, 0, 0, 23, 13, 1, 0, 0, 0, 0, 0, 3, 0, 0, 0, 207),
        (2026, 18, 'RT 004 RW 005', 34, 97, 0, 0, 0, 0, 44, 0, 0, 0, 0, 37, 14, 1, 0, 0, 0, 0, 2, 6, 0, 0, 0, 235),
        (2026, 19, 'RT 001 RW 006', 15, 77, 0, 0, 0, 0, 22, 2, 0, 0, 0, 18, 5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 140),
        (2026, 20, 'RT 002 RW 006', 17, 67, 0, 0, 0, 0, 24, 2, 0, 0, 0, 11, 3, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 132),
        (2026, 21, 'RT 003 RW 006', 9, 47, 0, 0, 0, 0, 11, 2, 0, 0, 0, 6, 4, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 83),
        (2026, 22, 'RT 001 RW 007', 15, 94, 0, 0, 0, 0, 50, 0, 0, 0, 0, 19, 3, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 183),
        (2026, 23, 'RT 002 RW 007', 23, 82, 0, 0, 0, 0, 39, 0, 0, 0, 0, 24, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 171),
        (2026, 24, 'RT 001 RW 008', 27, 80, 0, 0, 0, 0, 37, 0, 0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 1, 3, 0, 0, 0, 160),
        (2026, 25, 'RT 002 RW 008', 23, 67, 0, 0, 0, 0, 34, 0, 0, 0, 0, 24, 4, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 154),
        (2026, 26, 'RT 003 RW 008', 19, 82, 0, 0, 0, 0, 36, 0, 0, 0, 0, 17, 4, 0, 0, 0, 0, 0, 1, 5, 0, 1, 0, 165),
    ]

    cursor.execute("SELECT COUNT(*) FROM statistik_pendidikan WHERE tahun = 2026")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO statistik_pendidikan (
            tahun, no_urut, nama_sls, tidak_sekolah, sd, mi, paket_a, sdlb, spm_ula,
            smp, mts, smp_lb, paket_b, spm_wustha, sma, smk, ma, mak, sma_lb, paket_c,
            spm_ulya, diploma, s1, profesi, s2, s3, jumlah
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_pendidikan_2026)
        conn.commit()

    sample_perkawinan_2026 = [
        (2026, 1, 'RT 001 RW 001', 82, 85, 4, 14, 185),
        (2026, 2, 'RT 002 RW 001', 95, 122, 7, 13, 237),
        (2026, 3, 'RT 003 RW 001', 90, 128, 8, 18, 244),
        (2026, 4, 'RT 004 RW 001', 84, 95, 3, 15, 197),
        (2026, 5, 'RT 005 RW 001', 48, 67, 4, 2, 121),
        (2026, 6, 'RT 001 RW 002', 35, 66, 4, 10, 115),
        (2026, 7, 'RT 002 RW 002', 61, 76, 1, 10, 148),
        (2026, 8, 'RT 003 RW 002', 54, 74, 5, 14, 147),
        (2026, 9, 'RT 004 RW 002', 54, 89, 1, 11, 155),
        (2026, 10, 'RT 001 RW 003', 114, 152, 4, 12, 282),
        (2026, 11, 'RT 002 RW 003', 89, 119, 6, 15, 229),
        (2026, 12, 'RT 001 RW 004', 76, 127, 5, 24, 232),
        (2026, 13, 'RT 002 RW 004', 67, 101, 5, 16, 189),
        (2026, 14, 'RT 003 RW 004', 68, 131, 3, 14, 216),
        (2026, 15, 'RT 001 RW 005', 93, 122, 6, 19, 240),
        (2026, 16, 'RT 002 RW 005', 69, 94, 5, 16, 184),
        (2026, 17, 'RT 003 RW 005', 83, 124, 4, 14, 225),
        (2026, 18, 'RT 004 RW 005', 100, 133, 5, 15, 253),
        (2026, 19, 'RT 001 RW 006', 56, 88, 1, 7, 152),
        (2026, 20, 'RT 002 RW 006', 48, 75, 3, 13, 139),
        (2026, 21, 'RT 003 RW 006', 36, 49, 0, 7, 92),
        (2026, 22, 'RT 001 RW 007', 82, 100, 5, 11, 198),
        (2026, 23, 'RT 002 RW 007', 78, 88, 10, 15, 191),
        (2026, 24, 'RT 001 RW 008', 69, 98, 1, 9, 177),
        (2026, 25, 'RT 002 RW 008', 67, 92, 5, 7, 171),
        (2026, 26, 'RT 003 RW 008', 67, 101, 1, 10, 179)
    ]

    cursor.execute("SELECT COUNT(*) FROM statistik_perkawinan WHERE tahun = 2026")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO statistik_perkawinan (
            tahun, no_urut, nama_sls, belum_kawin, kawin, cerai_hidup, cerai_mati, total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_perkawinan_2026)
        conn.commit()

    sample_pencatatan_nikah_2026 = [
        (2026, 1, 'RT 001 RW 001', 76, 10, 0, 86),
        (2026, 2, 'RT 002 RW 001', 100, 23, 0, 123),
        (2026, 3, 'RT 003 RW 001', 117, 11, 0, 128),
        (2026, 4, 'RT 004 RW 001', 96, 0, 0, 96),
        (2026, 5, 'RT 005 RW 001', 53, 14, 0, 67),
        (2026, 6, 'RT 001 RW 002', 66, 0, 0, 66),
        (2026, 7, 'RT 002 RW 002', 81, 1, 0, 82),
        (2026, 8, 'RT 003 RW 002', 75, 1, 0, 76),
        (2026, 9, 'RT 004 RW 002', 100, 0, 0, 100),
        (2026, 10, 'RT 001 RW 003', 137, 23, 0, 160),
        (2026, 11, 'RT 002 RW 003', 106, 23, 0, 129),
        (2026, 12, 'RT 001 RW 004', 129, 1, 0, 130),
        (2026, 13, 'RT 002 RW 004', 104, 0, 0, 104),
        (2026, 14, 'RT 003 RW 004', 137, 1, 1, 139),
        (2026, 15, 'RT 001 RW 005', 102, 21, 0, 123),
        (2026, 16, 'RT 002 RW 005', 70, 25, 0, 95),
        (2026, 17, 'RT 003 RW 005', 108, 16, 0, 124),
        (2026, 18, 'RT 004 RW 005', 111, 22, 0, 133),
        (2026, 19, 'RT 001 RW 006', 92, 1, 0, 93),
        (2026, 20, 'RT 002 RW 006', 75, 0, 0, 75),
        (2026, 21, 'RT 003 RW 006', 51, 1, 0, 52),
        (2026, 22, 'RT 001 RW 007', 94, 8, 0, 102),
        (2026, 23, 'RT 002 RW 007', 84, 6, 0, 90),
        (2026, 24, 'RT 001 RW 008', 72, 26, 0, 98),
        (2026, 25, 'RT 002 RW 008', 68, 24, 0, 92),
        (2026, 26, 'RT 003 RW 008', 72, 29, 0, 101)
    ]

    cursor.execute("SELECT COUNT(*) FROM statistik_pencatatan_nikah WHERE tahun = 2026")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO statistik_pencatatan_nikah (
            tahun, no_urut, nama_sls, kawin_tercatat, kawin_belum_tercatat, kawin_tidak_tercatat, total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_pencatatan_nikah_2026)
        conn.commit()

    sample_agama_2026 = [
        (2026, 1, 'RT 001 RW 001', 185, 0, 0, 0, 0, 0, 0, 185),
        (2026, 2, 'RT 002 RW 001', 237, 0, 0, 0, 0, 0, 0, 237),
        (2026, 3, 'RT 003 RW 001', 244, 0, 0, 0, 0, 0, 0, 244),
        (2026, 4, 'RT 004 RW 001', 197, 0, 0, 0, 0, 0, 0, 197),
        (2026, 5, 'RT 005 RW 001', 121, 0, 0, 0, 0, 0, 0, 121),
        (2026, 6, 'RT 001 RW 002', 115, 0, 0, 0, 0, 0, 0, 115),
        (2026, 7, 'RT 002 RW 002', 148, 0, 0, 0, 0, 0, 0, 148),
        (2026, 8, 'RT 003 RW 002', 147, 0, 0, 0, 0, 0, 0, 147),
        (2026, 9, 'RT 004 RW 002', 155, 0, 0, 0, 0, 0, 0, 155),
        (2026, 10, 'RT 001 RW 003', 282, 0, 0, 0, 0, 0, 0, 282),
        (2026, 11, 'RT 002 RW 003', 229, 0, 0, 0, 0, 0, 0, 229),
        (2026, 12, 'RT 001 RW 004', 232, 0, 0, 0, 0, 0, 0, 232),
        (2026, 13, 'RT 002 RW 004', 189, 0, 0, 0, 0, 0, 0, 189),
        (2026, 14, 'RT 003 RW 004', 216, 0, 0, 0, 0, 0, 0, 216),
        (2026, 15, 'RT 001 RW 005', 240, 0, 0, 0, 0, 0, 0, 240),
        (2026, 16, 'RT 002 RW 005', 184, 0, 0, 0, 0, 0, 0, 184),
        (2026, 17, 'RT 003 RW 005', 225, 0, 0, 0, 0, 0, 0, 225),
        (2026, 18, 'RT 004 RW 005', 253, 0, 0, 0, 0, 0, 0, 253),
        (2026, 19, 'RT 001 RW 006', 152, 0, 0, 0, 0, 0, 0, 152),
        (2026, 20, 'RT 002 RW 006', 139, 0, 0, 0, 0, 0, 0, 139),
        (2026, 21, 'RT 003 RW 006', 92, 0, 0, 0, 0, 0, 0, 92),
        (2026, 22, 'RT 001 RW 007', 198, 0, 0, 0, 0, 0, 0, 198),
        (2026, 23, 'RT 002 RW 007', 191, 0, 0, 0, 0, 0, 0, 191),
        (2026, 24, 'RT 001 RW 008', 177, 0, 0, 0, 0, 0, 0, 177),
        (2026, 25, 'RT 002 RW 008', 171, 0, 0, 0, 0, 0, 0, 171),
        (2026, 26, 'RT 003 RW 008', 179, 0, 0, 0, 0, 0, 0, 179)
    ]

    cursor.execute("SELECT COUNT(*) FROM statistik_agama WHERE tahun = 2026")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO statistik_agama (
            tahun, no_urut, nama_sls, islam, kristen, katholik, budha, hindu, konghucu, kepercayaan_lainnya, total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_agama_2026)
        conn.commit()

    sample_bansos_2026 = [
        (2026, 1, 'RT 001 RW 001', 9, 18, 0, 0, 0, 2, 0, 0, 4, 33),
        (2026, 2, 'RT 002 RW 001', 1, 11, 0, 0, 0, 0, 1, 3, 4, 20),
        (2026, 3, 'RT 003 RW 001', 7, 21, 0, 0, 0, 1, 1, 2, 2, 34),
        (2026, 4, 'RT 004 RW 001', 15, 37, 1, 0, 0, 34, 0, 4, 0, 91),
        (2026, 5, 'RT 005 RW 001', 3, 6, 0, 0, 0, 0, 0, 1, 2, 12),
        (2026, 6, 'RT 001 RW 002', 3, 17, 0, 0, 0, 4, 0, 12, 14, 50),
        (2026, 7, 'RT 002 RW 002', 8, 14, 0, 0, 0, 8, 1, 15, 1, 47),
        (2026, 8, 'RT 003 RW 002', 4, 21, 0, 0, 0, 9, 0, 0, 1, 35),
        (2026, 9, 'RT 004 RW 002', 6, 21, 0, 0, 0, 26, 0, 28, 13, 94),
        (2026, 10, 'RT 001 RW 003', 8, 28, 0, 0, 0, 21, 0, 0, 0, 57),
        (2026, 11, 'RT 002 RW 003', 2, 6, 0, 0, 0, 15, 0, 0, 0, 23),
        (2026, 12, 'RT 001 RW 004', 12, 32, 0, 0, 0, 0, 0, 1, 1, 46),
        (2026, 13, 'RT 002 RW 004', 8, 18, 0, 0, 0, 0, 0, 6, 0, 32),
        (2026, 14, 'RT 003 RW 004', 4, 16, 0, 0, 0, 0, 0, 0, 0, 20),
        (2026, 15, 'RT 001 RW 005', 9, 30, 0, 0, 0, 15, 0, 17, 0, 71),
        (2026, 16, 'RT 002 RW 005', 6, 22, 0, 0, 0, 5, 1, 30, 3, 67),
        (2026, 17, 'RT 003 RW 005', 14, 21, 0, 0, 0, 16, 7, 11, 4, 73),
        (2026, 18, 'RT 004 RW 005', 15, 26, 0, 0, 0, 16, 3, 6, 5, 71),
        (2026, 19, 'RT 001 RW 006', 7, 12, 0, 0, 0, 2, 0, 3, 3, 27),
        (2026, 20, 'RT 002 RW 006', 4, 14, 0, 0, 0, 2, 0, 7, 9, 36),
        (2026, 21, 'RT 003 RW 006', 7, 8, 0, 0, 0, 1, 0, 0, 0, 16),
        (2026, 22, 'RT 001 RW 007', 7, 9, 0, 0, 0, 10, 0, 0, 0, 26),
        (2026, 23, 'RT 002 RW 007', 7, 24, 0, 0, 0, 13, 1, 3, 0, 48),
        (2026, 24, 'RT 001 RW 008', 6, 22, 0, 0, 0, 16, 0, 0, 0, 44),
        (2026, 25, 'RT 002 RW 008', 3, 11, 0, 0, 0, 5, 0, 0, 0, 19),
        (2026, 26, 'RT 003 RW 008', 7, 18, 0, 0, 0, 8, 0, 0, 0, 33)
    ]

    cursor.execute("SELECT COUNT(*) FROM statistik_bansos WHERE tahun = 2026")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO statistik_bansos (
            tahun, no_urut, nama_sls, pkh, bpnt, bos, bapanas, stunting, pbi_jkn, blt, blt_dd, lainnya, total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_bansos_2026)
        conn.commit()

    sample_sls_26 = [
        'RT 001 RW 001', 'RT 002 RW 001', 'RT 003 RW 001', 'RT 004 RW 001', 'RT 005 RW 001',
        'RT 001 RW 002', 'RT 002 RW 002', 'RT 003 RW 002', 'RT 004 RW 002',
        'RT 001 RW 003', 'RT 002 RW 003',
        'RT 001 RW 004', 'RT 002 RW 004', 'RT 003 RW 004',
        'RT 001 RW 005', 'RT 002 RW 005', 'RT 003 RW 005', 'RT 004 RW 005',
        'RT 001 RW 006', 'RT 002 RW 006', 'RT 003 RW 006',
        'RT 001 RW 007', 'RT 002 RW 007',
        'RT 001 RW 008', 'RT 002 RW 008', 'RT 003 RW 008'
    ]

    sample_anak_2026 = [
        (2026, i + 1, sls_name, 0, 0, 0, 0, 0)
        for i, sls_name in enumerate(sample_sls_26)
    ]

    cursor.execute("SELECT COUNT(*) FROM statistik_anak WHERE tahun = 2026")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO statistik_anak (
            tahun, no_urut, nama_sls, anak_yatim, anak_piatu, yatim_piatu, orang_tua_lengkap, total_anak
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_anak_2026)
        conn.commit()

    sample_gizi_buruk_2026 = [
        (2026, i + 1, sls_name, 1, 10, 10.0)
        for i, sls_name in enumerate(sample_sls_26)
    ]

    cursor.execute("SELECT COUNT(*) FROM statistik_gizi_buruk WHERE tahun = 2026")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO statistik_gizi_buruk (
            tahun, no_urut, nama_sls, anak_gizi_buruk, jumlah_anak_balita, persentase
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_gizi_buruk_2026)
        conn.commit()

    sample_stunting_2026 = [
        (2026, i + 1, sls_name, 1, 10, 10.0)
        for i, sls_name in enumerate(sample_sls_26)
    ]

    cursor.execute("SELECT COUNT(*) FROM statistik_stunting WHERE tahun = 2026")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO statistik_stunting (
            tahun, no_urut, nama_sls, anak_stunting, jumlah_anak_balita, persentase
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_stunting_2026)
        conn.commit()



    usia = [
        {"label": "0 - 14 Th (Anak)", "jumlah": 1160},
        {"label": "15 - 24 Th (Pemuda)", "jumlah": 945},
        {"label": "25 - 45 Th (Dewasa)", "jumlah": 1695},
        {"label": "46 - 60 Th (Lansia Awal)", "jumlah": 742},
        {"label": "> 60 Th (Lansia)", "jumlah": 356}
    ]
    pekerjaan = [
        {"label": "Nelayan & Budidaya Laut", "jumlah": 1610},
        {"label": "Petani & Perkebunan", "jumlah": 612},
        {"label": "Pedagang & UMKM", "jumlah": 485},
        {"label": "Pekerja Tambak/Jasa", "jumlah": 368},
        {"label": "PNS/Guru/Perangkat", "jumlah": 158},
        {"label": "Lainnya", "jumlah": 1665}
    ]

    cursor.execute("SELECT COUNT(*) FROM statistik")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO statistik (id, tahun, total_penduduk, laki_laki, perempuan, kepala_keluarga, penduduk_sementara, mutasi_penduduk, data_usia_json, data_pekerjaan_json)
        VALUES (1, 2026, 4898, 2504, 2394, 1748, 84, 27, ?, ?)
        ''', (json.dumps(usia), json.dumps(pekerjaan)))
        conn.commit()
    else:
        cursor.execute('''
        UPDATE statistik SET 
            tahun = 2026,
            total_penduduk = 4898,
            laki_laki = 2504,
            perempuan = 2394,
            kepala_keluarga = 1748,
            data_usia_json = ?,
            data_pekerjaan_json = ?
        WHERE id = 1
        ''', (json.dumps(usia), json.dumps(pekerjaan)))
        conn.commit()

    # Seed contoh permohonan surat & pengaduan
    cursor.execute("SELECT COUNT(*) FROM layanan_surat")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO layanan_surat (no_reg, jenis_surat, nik, nama, wa, dusun, rt, keperluan, status, catatan_admin)
        VALUES 
        ('KSK-2026-1082', 'Surat Keterangan Usaha (SKU)', '6402171203850001', 'Rusli Effendi', '081255443322', 'Dusun Empang', '003', 'Pengajuan Kredit Usaha Nelayan di Bank Kaltimtara', 'Diproses', 'Berkas KTP & Foto Tambak terverifikasi'),
        ('KSK-2026-1045', 'Surat Keterangan Domisili (SKD)', '6402175508920003', 'Hj. Mardiana', '082199887766', 'Dusun Kersik', '002', 'Persyaratan Pendaftaran Anak Masuk Sekolah', 'Selesai', 'Surat sudah diambil oleh pemohon')
        ''')
        conn.commit()

    # Seed Kategori Pengaduan & Aspirasi Warga
    cursor.execute("SELECT COUNT(*) FROM kategori_pengaduan")
    if cursor.fetchone()[0] == 0:
        default_kategori_aduan = [
            ("Umum", "Aspirasi, saran umum, dan usulan pembangunan fasilitas desa", 1),
            ("Sosial", "Bantuan sosial, kemasyarakatan, kegiatan warga, dan kepemudaan", 2),
            ("Keamanan", "Ketertiban lingkungan, ronda malam/poskamling, dan perlindungan warga", 3),
            ("Kesehatan", "Layanan posyandu, balita stunting, sanitasi, dan kesehatan lingkungan", 4),
            ("Kebersihan", "Pengelolaan sampah, saluran drainase, kebersihan sungai dan lingkungan", 5),
        ]
        for nama_ka, ket_ka, urut_ka in default_kategori_aduan:
            cursor.execute("INSERT OR IGNORE INTO kategori_pengaduan (nama, keterangan, urutan) VALUES (?, ?, ?)", (nama_ka, ket_ka, urut_ka))
        conn.commit()

    cursor.execute("SELECT COUNT(*) FROM pengaduan")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO pengaduan (no_tiket, nama, kontak, kategori, pesan, status, tanggapan_admin, uraian_tindak_lanjut)
        VALUES 
        ('ADUAN-48192', 'Pak Syahrul', '081344221100', 'Keamanan', 'Lampu penerangan jalan gang masuk RT 003 padam 2 titik, mohon perbaikan segera agar warga merasa aman saat malam hari.', 'Perlu Perlakuan Khusus', 'Sudah diteruskan ke Kaur Umum dan teknisi PLN.', 'Memerlukan penggantian tiang & panel meteran baru yang dikoordinasikan dengan pihak PLN cabang. Pengerjaan dijadwalkan selesai akhir pekan ini.'),
        ('ADUAN-39201', 'Ibu Nurhayati', '085277889911', 'Kebersihan', 'Sampah di tempat penampungan sementara dekat lapangan perlu diangkut rutin setiap 2 hari sekali agar tidak menumpuk.', 'Sudah Diselesaikan', 'Jadwal armada kebersihan telah diperbaharui.', 'Petugas kebersihan desa telah mengangkut seluruh tumpukan sampah dan menyepakati jadwal pengangkutan rutin tiap hari Selasa dan Jumat pagi.'),
        ('ADUAN-51203', 'Bapak Wahyu Pratama', '081298765432', 'Sosial', 'Pengajuan verifikasi ulang calon penerima bantuan sembako untuk lansia tunggal di wilayah RT 004.', 'Belum Ditanggapi', '', '')
        ''')
        conn.commit()
    else:
        # Perbarui kategori lama agar selaras dengan kategori baru jika masih memakai kategori lama
        cursor.execute("UPDATE pengaduan SET kategori = 'Keamanan' WHERE kategori LIKE '%Keamanan%'")
        cursor.execute("UPDATE pengaduan SET kategori = 'Kebersihan' WHERE kategori LIKE '%Lingkungan%' OR kategori LIKE '%Sampah%'")
        cursor.execute("UPDATE pengaduan SET kategori = 'Umum' WHERE kategori LIKE '%Infrastruktur%' OR kategori LIKE '%Jalan%' OR kategori LIKE '%Administrasi%'")
        cursor.execute("UPDATE pengaduan SET kategori = 'Sosial' WHERE kategori LIKE '%Bantuan%'")
        conn.commit()

    # Seed Kategori Buku Publikasi
    cursor.execute("SELECT COUNT(*) FROM kategori_publikasi")
    if cursor.fetchone()[0] == 0:
        default_kat_pub = [
            ("Profil Desa", 1),
            ("Desa Dalam Angka", 2),
            ("Laporan & Transparansi APBDes", 3),
            ("Regulasi & Kebijakan Desa", 4),
            ("Panduan & Edukasi Warga", 5),
            ("Majalah & Warta Desa", 6),
        ]
        for nama_kp, urut_kp in default_kat_pub:
            cursor.execute("INSERT OR IGNORE INTO kategori_publikasi (nama, urutan) VALUES (?, ?)", (nama_kp, urut_kp))
        conn.commit()

    # Seed Buku Publikasi
    cursor.execute("SELECT COUNT(*) FROM buku_publikasi")
    if cursor.fetchone()[0] == 0:
        sample_buku = [
            (
                "Buku Profil Desa Papayan 2026",
                "Profil Desa",
                "Tim Penyusun Profil Desa",
                "2026",
                "Edisi Khusus Pemekaran & Wisata",
                68,
                "2.4 MB",
                "Buku dokumentasi komprehensif mengenai gambaran umum Desa Papayan, sejarah kepemimpinan, demografi, potensi pariwisata pesisir Pantai Biru, serta prestasi peraih Program Kampung Iklim (Proklim) Utama KLHK RI.",
                "static/images/kantor_desa.jpg",
                "static/docs/publikasi/buku_profil_desa_kersik_2026.pdf",
                142,
                "Tayang",
                1
            ),
            (
                "Desa Papayan Dalam Angka 2026",
                "Desa Dalam Angka",
                "Pemerintah Desa Papayan",
                "2026",
                "Kompilasi Data Tahunan",
                54,
                "1.9 MB",
                "Publikasi statistik resmi tahunan yang memuat data sektoral kependudukan, kelompok nelayan tangkap, produksi perikanan & budidaya tambak udang, sarana pendidikan, dan peta perekonomian desa pesisir.",
                "static/images/nelayan.jpg",
                "static/docs/publikasi/buku_desa_kersik_dalam_angka_2026.pdf",
                89,
                "Tayang",
                0
            ),
            (
                "Laporan Akuntabilitas & Realisasi APBDes 2025/2026",
                "Laporan & Transparansi APBDes",
                "Kaur Keuangan & Sekretariat Desa",
                "2026",
                "Laporan Resmi Transparansi",
                42,
                "3.1 MB",
                "Laporan pertanggungjawaban realisasi penerimaan Dana Desa (APBN), Alokasi Dana Desa (ADD Kukar), dan Belanja Desa untuk pembangunan jalan pesisir, dermaga nelayan, dan program ketahanan pangan.",
                "static/images/tambak.jpg",
                "static/docs/publikasi/laporan_transparansi_apbdes_2025_2026.pdf",
                64,
                "Tayang",
                0
            ),
            (
                "Buku Saku Panduan Wisata & Ekologi Pesisir",
                "Panduan & Edukasi Warga",
                "Pokdarwis & Pengelola Proklim",
                "2026",
                "Cetakan I / 2026",
                32,
                "1.8 MB",
                "Buku panduan saku praktis bagi wisatawan, pegiat lingkungan, dan pelajar mengenai rute wisata bahari Pantai Biru Kersik, tata cara adopsi bibit mangrove, serta etika menjaga kelestarian ekosistem pantai.",
                "static/images/mangrove.jpg",
                "static/docs/publikasi/buku_saku_panduan_wisata_pesisir.pdf",
                115,
                "Tayang",
                0
            ),
            (
                "Dokumen RKPDes Kersik Tahun 2026",
                "Regulasi & Kebijakan Desa",
                "BPD & Tim Perencana Desa",
                "2026",
                "Dokumen Rencana Kerja",
                86,
                "4.2 MB",
                "Dokumen Rencana Kerja Pemerintah Desa (RKPDes) tahun anggaran 2026 yang memuat arah prioritas pembangunan fisik desa, penguatan ekonomi nelayan, dan program pemberdayaan UMKM lokal.",
                "static/images/banner1.png",
                "static/docs/publikasi/dokumen_rkpdes_kersik_2026.pdf",
                37,
                "Tayang",
                0
            )
        ]
        cursor.executemany('''
        INSERT INTO buku_publikasi (
            judul, kategori, penulis, tahun, edisi, jumlah_halaman, ukuran_file,
            sinopsis, cover_buku, file_pdf, jumlah_unduh, status, is_featured
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_buku)
        conn.commit()

    # 13. Running Text (Teks Berjalan / Pengumuman Bergerak)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS running_texts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teks TEXT NOT NULL,
        urutan INTEGER DEFAULT 1,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM running_texts")
    if cursor.fetchone()[0] == 0:
        default_running = [
            ("🕒 Jam Pelayanan: Senin - Kamis (08.00 - 15.00) & Jum'at (08.00 - 11.00) WIB", 1, 1),
            ("🏛️ Selamat Datang di Portal Resmi Informasi & Layanan Mandiri Pemerintah Desa", 2, 1),
            ("📄 Urus surat keterangan resmi (SKU, SKD, SKTM, dll.) secara online mandiri 24 jam melalui menu Layanan Surat", 3, 1),
            ("📢 Sampaikan aspirasi & aduan masyarakat melalui tombol Pengaduan di sudut kiri bawah website", 4, 1)
        ]
        cursor.executemany("INSERT INTO running_texts (teks, urutan, is_active) VALUES (?, ?, ?)", default_running)
        conn.commit()

    conn.close()

def record_activity_log(action, details=None, username=None, user_id=None, ip_address=None, user_agent=None):
    """Mencatat aktivitas audit keamanan dan tindakan admin ke basis data"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO activity_logs (user_id, username, action, details, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, action, details, ip_address, user_agent))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Gagal mencatat log aktivitas: {e}")

if __name__ == '__main__':
    init_db()
    print("Database Desa Papayan berhasil diinisialisasi dan disiapkan.")

