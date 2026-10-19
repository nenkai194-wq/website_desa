import sqlite3
import json

conn = sqlite3.connect('desa.db')
cursor = conn.cursor()

print("1. Membersihkan tabel wisata dari data pesisir / Kalimantan...")
cursor.execute("""
    DELETE FROM wisata 
    WHERE LOWER(deskripsi) LIKE '%makassar%' 
       OR LOWER(deskripsi) LIKE '%kutai%' 
       OR LOWER(deskripsi) LIKE '%selat%'
       OR LOWER(nama) LIKE '%pantai%' 
       OR LOWER(nama) LIKE '%mangrove%' 
       OR LOWER(nama) LIKE '%nelayan%' 
       OR LOWER(nama) LIKE '%tambak%'
       OR (longitude IS NOT NULL AND longitude > 115)
""")

# Masukkan destinasi / landmark resmi Desa Papayan dengan koordinat valid di Tasikmalaya
cursor.execute("SELECT COUNT(*) FROM wisata")
if cursor.fetchone()[0] == 0:
    papayan_wisata = [
        (
            "Agrowisata & Pertanian Terpadu Papayan",
            "Agrowisata & Edukasi",
            "Kawasan percontohan pertanian modern, kebun bibit hortikultura, dan perkebunan produktif yang dikelola kelompok tani Desa Papayan.",
            "Area Parkir, Saung Tani, Pusat Edukasi Pertanian, Toilet, Musholla",
            "Gratis",
            "Dusun Ranca Sari, Desa Papayan",
            "static/images/banner1.png",
            1,
            -7.4720,
            108.2070,
            "Disetujui"
        ),
        (
            "Taman Rekreasi & Lapang Desa Papayan",
            "Ruang Terbuka Hijau",
            "Pusat kegiatan olahraga, kebugaran masyarakat, dan pagelaran seni budaya warga Desa Papayan di dekat balai pertemuan desa.",
            "Jogging Track, Lapang Sepakbola, Gazebo, Kios UMKM, Toilet",
            "Gratis",
            "Dusun Margahayu, Desa Papayan",
            "static/images/banner2.png",
            2,
            -7.4785,
            108.2045,
            "Disetujui"
        )
    ]
    cursor.executemany("""
        INSERT INTO wisata (nama, kategori, deskripsi, fasilitas, tiket, lokasi, gambar, urutan, latitude, longitude, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, papayan_wisata)
print(f"   Wisata dibersihkan. Jumlah sekarang: {cursor.execute('SELECT COUNT(*) FROM wisata').fetchone()[0]}")

print("2. Membersihkan tabel umkm dari data pesisir / Kalimantan...")
cursor.execute("""
    DELETE FROM umkm 
    WHERE LOWER(nama) LIKE '%marang kayu%' 
       OR LOWER(deskripsi) LIKE '%makassar%' 
       OR LOWER(deskripsi) LIKE '%kukar%' 
       OR LOWER(produsen) LIKE '%nelayan%' 
       OR LOWER(produsen) LIKE '%kerang%' 
       OR (longitude IS NOT NULL AND longitude > 115)
""")
# Pastikan UMKM yang tersisa memiliki koordinat di wilayah Papayan
cursor.execute("UPDATE umkm SET latitude = -7.4760, longitude = 108.2065 WHERE nama LIKE '%Madu%'")
cursor.execute("UPDATE umkm SET latitude = -7.4775, longitude = 108.2050 WHERE nama LIKE '%Keripik%'")
print(f"   UMKM dibersihkan. Jumlah sekarang: {cursor.execute('SELECT COUNT(*) FROM umkm').fetchone()[0]}")

print("3. Memperbarui tabel berita untuk Desa Papayan...")
cursor.execute("DELETE FROM berita WHERE LOWER(ringkasan) LIKE '%makassar%' OR LOWER(ringkasan) LIKE '%bontang%' OR LOWER(ringkasan) LIKE '%nelayan%' OR LOWER(judul) LIKE '%mangrove%' OR LOWER(judul) LIKE '%pantai%'")
cursor.execute("SELECT COUNT(*) FROM berita")
if cursor.fetchone()[0] < 3:
    berita_baru = [
        (
            "Pemerintah Desa Papayan Ikuti Pembinaan Program Desa Cantik (Cinta Statistik) 2026",
            "Pemerintahan",
            "Humas Pemdes Papayan",
            "2026-10-18",
            "static/images/uploads/b2_1792274407.jpeg",
            "Desa Papayan terpilih dalam pembinaan Program Desa Cantik oleh BPS Kabupaten Tasikmalaya untuk penguatan tata kelola data kependudukan dan statistik desa berbasis SLS.",
            "Desa Papayan, Kecamatan Jatiwaras terpilih sebagai salah satu desa binaan Program Desa Cantik (Desa Cinta Statistik) tahun 2026 yang diselenggarakan oleh Badan Pusat Statistik (BPS) Kabupaten Tasikmalaya. Melalui program ini, seluruh aparatur desa dilatih mengelola data statistik kependudukan dan demografi RT/RW secara terpadu, mutakhir, dan akurat demi kelancaran perencanaan pembangunan desa.",
            "Tayang"
        ),
        (
            "Penyaluran Bantuan Langsung Tunai (BLT) Dana Desa Papayan Berjalan Lancar & Tertib",
            "Sosial & Masyarakat",
            "Kaur Keuangan",
            "2026-10-15",
            "static/images/banner1.png",
            "Pemerintah Desa Papayan menyalurkan BLT Dana Desa kepada puluhan Keluarga Penerima Manfaat (KPM) bertempat di Aula Pertemuan Desa.",
            "Penyaluran Bantuan Langsung Tunai bersumber dari Dana Desa (BLT-DD) tahap terkini telah dilaksanakan secara tertib di Balai Pertemuan Desa Papayan. Hadir dalam acara Kepala Desa, BPD, Babinsa, dan Bhabinkamtibmas guna mendampingi para penerima manfaat. Program ini diharapkan dapat meringankan beban ekonomi keluarga penerima serta menggerakkan roda ekonomi kerakyatan di tingkat dusun.",
            "Tayang"
        ),
        (
            "Musrenbangdes Penetapan RKPDes Papayan Fokus pada Peningkatan Pertanian & Layanan Digital",
            "Pembangunan",
            "Sekretariat Desa",
            "2026-10-10",
            "static/images/banner2.png",
            "Musyawarah perencanaan pembangunan desa menyepakati prioritas anggaran tahun 2026 untuk perbaikan jalan usaha tani dan layanan digital warga.",
            "Pemerintah Desa Papayan sukses menggelar Musyawarah Perencanaan Pembangunan Desa (Musrenbangdes). Berdasarkan musyawarah mufakat seluruh unsur kelembagaan desa, disepakati program prioritas meliputi perbaikan infrastruktur jalan pertanian, pengadaan sarana air bersih, pemberdayaan UMKM lokal, dan optimalisasi sistem informasi pelayanan desa.",
            "Tayang"
        )
    ]
    cursor.executemany("""
        INSERT INTO berita (judul, kategori, penulis, tanggal, gambar, ringkasan, isi, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, berita_baru)
print("   Berita diperbarui.")

print("4. Memperbarui buku_publikasi...")
cursor.execute("""
    UPDATE buku_publikasi 
    SET judul = 'Buku Profil Desa Papayan 2026',
        penulis = 'Tim Penyusun Profil Desa',
        sinopsis = 'Buku dokumentasi komprehensif mengenai gambaran umum wilayah, kependudukan, kelembagaan, dan potensi Desa Papayan, Kecamatan Jatiwaras, Kabupaten Tasikmalaya.',
        cover_buku = 'static/images/banner1.png'
    WHERE id = 1
""")
cursor.execute("""
    UPDATE buku_publikasi 
    SET judul = 'Desa Papayan Dalam Angka 2026',
        penulis = 'Pemerintah Desa Papayan',
        sinopsis = 'Publikasi statistik resmi tahunan yang memuat data sektoral kependudukan, pertanian, perkebunan rakyat, sarana pendidikan, dan peta perekonomian Desa Papayan.',
        cover_buku = 'static/images/banner2.png'
    WHERE id = 2
""")
cursor.execute("""
    UPDATE buku_publikasi 
    SET judul = 'Laporan Akuntabilitas & Realisasi APBDes 2026',
        penulis = 'Kaur Keuangan & Sekretariat Desa',
        sinopsis = 'Laporan pertanggungjawaban realisasi penerimaan Dana Desa (APBN), Alokasi Dana Desa (ADD Kab. Tasikmalaya), dan PADes untuk pembangunan infrastruktur desa serta ketahanan pangan.',
        cover_buku = 'static/images/banner1.png'
    WHERE id = 3
""")
cursor.execute("""
    UPDATE buku_publikasi 
    SET judul = 'Buku Panduan Potensi Pertanian & UMKM Papayan',
        penulis = 'Pemerintah Desa & Poktan',
        sinopsis = 'Buku panduan praktis sentra budidaya pertanian, produk olahan pangan lokal, dan direktori UMKM binaan Desa Papayan.',
        cover_buku = 'static/images/banner2.png'
    WHERE id = 4
""")

print("5. Memperbarui galeri...")
cursor.execute("""
    UPDATE galeri 
    SET judul = 'Pelatihan Diversifikasi Produk Olahan Pertanian & UMKM',
        deskripsi = 'Kegiatan pembinaan ibu-ibu PKK dan kelompok tani wanita dalam pengolahan hasil panen perkebunan dan peningkatan nilai jual produk olahan lokal.',
        gambar = 'static/images/banner1.png'
    WHERE id = 4
""")
cursor.execute("""
    UPDATE galeri 
    SET judul = 'Gerakan Gotong Royong Penataan Lingkungan Dusun & Saluran Irigasi',
        deskripsi = 'Aksi swadaya bersama warga membersihkan lingkungan dan memelihara saluran irigasi persawahan di Desa Papayan.',
        gambar = 'static/images/banner2.png'
    WHERE id = 2
""")
cursor.execute("""
    UPDATE galeri 
    SET judul = 'Apresiasi Desa Berprestasi Tata Kelola Keterbukaan Informasi',
        deskripsi = 'Penghargaan atas komitmen Pemerintah Desa Papayan dalam menghadirkan keterbukaan informasi publik dan digitalisasi data statistik desa.',
        gambar = 'static/images/logo_tasikmalaya.png'
    WHERE id = 5
""")
cursor.execute("""
    UPDATE galeri 
    SET gambar = 'static/images/logo_tasikmalaya.png'
    WHERE id = 7
""")

print("6. Memperbarui popup_informasi...")
cursor.execute("""
    UPDATE popup_informasi 
    SET judul = 'Selamat Datang di Portal Resmi Desa Papayan',
        subjudul = 'Pusat Informasi & Pelayanan Administrasi Publik Desa Papayan',
        kategori = 'Pengumuman Resmi',
        isi = 'Selamat datang di portal informasi dan pelayanan digital Desa Papayan, Kecamatan Jatiwaras, Kabupaten Tasikmalaya. Manfaatkan portal ini untuk mengajukan permohonan surat online, memantau transparansi anggaran APBDes, serta mengakses peta wilayah dan produk UMKM warga desa.',
        gambar = 'static/images/banner1.png'
    WHERE id = 1
""")

print("7. Memperbarui APBDes dan Statistik Pekerjaan...")
belanja_papayan = [
    {"bidang": "Penyelenggaraan Pemerintahan Desa", "nominal": 780000000, "persen": 31.3},
    {"bidang": "Pelaksanaan Pembangunan Infrastruktur Desa", "nominal": 990000000, "persen": 39.8},
    {"bidang": "Pembinaan Kemasyarakatan Desa", "nominal": 260000000, "persen": 10.4},
    {"bidang": "Pemberdayaan Masyarakat & UMKM Pertanian", "nominal": 340000000, "persen": 13.7},
    {"bidang": "Penanggulangan Bencana & Keadaan Mendesak", "nominal": 120000000, "persen": 4.8}
]
sumber_papayan = [
    {"sumber": "Dana Desa (APBN)", "nominal": 1120000000, "persen": 44.1},
    {"sumber": "Alokasi Dana Desa (ADD Kab. Tasikmalaya)", "nominal": 980000000, "persen": 38.6},
    {"sumber": "Bagi Hasil Pajak & Retribusi Daerah", "nominal": 220000000, "persen": 8.7},
    {"sumber": "Pendapatan Asli Desa (BUMDes & Pasar)", "nominal": 140000000, "persen": 5.5},
    {"sumber": "Bantuan Keuangan Provinsi Jawa Barat", "nominal": 80000000, "persen": 3.1}
]
cursor.execute("""
    UPDATE apbdes 
    SET data_belanja_json = ?, data_sumber_json = ? 
    WHERE id = 1
""", (json.dumps(belanja_papayan), json.dumps(sumber_papayan)))

pekerjaan_papayan = [
    {"label": "Petani & Buruh Tani", "jumlah": 1820},
    {"label": "Wiraswasta / Pedagang / UMKM", "jumlah": 840},
    {"label": "Karyawan Swasta / BUMN", "jumlah": 612},
    {"label": "PNS / Guru / TNI / POLRI", "jumlah": 185},
    {"label": "Buruh Bangunan & Pertukangan", "jumlah": 450},
    {"label": "Lainnya", "jumlah": 1150}
]
cursor.execute("""
    UPDATE statistik 
    SET data_pekerjaan_json = ? 
    WHERE id = 1
""", (json.dumps(pekerjaan_papayan),))

print("8. Memperbarui nama dusun & sambutan di perangkat_desa...")
cursor.execute("""
    UPDATE perangkat_desa 
    SET sambutan_singkat = 'Perencanaan infrastruktur terpadu: jalan desa, irigasi pertanian, dan fasilitas publik.'
    WHERE id = 6
""")
cursor.execute("""
    UPDATE perangkat_desa 
    SET jabatan = 'Kepala Dusun Demung Landung',
        sambutan_singkat = 'Mengawal keharmonisan warga dan pembangunan di kawasan Dusun Demung Landung.'
    WHERE id = 7
""")
cursor.execute("""
    UPDATE perangkat_desa 
    SET jabatan = 'Kepala Dusun Ranca Sari',
        sambutan_singkat = 'Membangun gotong royong dan kemitraan masyarakat Dusun Ranca Sari.'
    WHERE id = 8
""")

print("9. Membersihkan aduan & permohonan surat bertema nelayan / pesisir Kalimantan...")
cursor.execute("DELETE FROM layanan_surat WHERE LOWER(keperluan) LIKE '%kaltimtara%' OR LOWER(keperluan) LIKE '%perahu nelayan%'")
cursor.execute("DELETE FROM pengaduan WHERE LOWER(pesan) LIKE '%dermaga nelayan%' OR LOWER(pesan) LIKE '%pantai papayan%'")

print("10. Membersihkan residual gambar berita, jabatan, dan opsi pekerjaan...")
cursor.execute("UPDATE berita SET gambar = 'static/images/banner1.png' WHERE gambar LIKE '%kersik%' OR gambar LIKE '%pantai%'")
cursor.execute("DELETE FROM jabatan_struktural WHERE nama_jabatan LIKE '%Empang%' OR nama_jabatan LIKE '%Kersik%'")
for dusun_name in ["Kepala Dusun Demung Landung", "Kepala Dusun Ranca Sari", "Kepala Dusun Margahayu", "Kepala Dusun Cihaur"]:
    cursor.execute("INSERT OR IGNORE INTO jabatan_struktural (nama_jabatan, urutan) VALUES (?, 10)", (dusun_name,))

cursor.execute("UPDATE profil_desa SET feedback_opsi_pekerjaan = REPLACE(feedback_opsi_pekerjaan, 'Nelayan / Budidaya Laut', 'Petani / Pekebun / Peternak') WHERE feedback_opsi_pekerjaan LIKE '%Nelayan%'")

cursor.execute("UPDATE buku_publikasi SET file_pdf = 'static/docs/publikasi/buku_profil_desa_papayan_2026.pdf' WHERE id = 1")
cursor.execute("UPDATE buku_publikasi SET file_pdf = 'static/docs/publikasi/buku_desa_papayan_dalam_angka_2026.pdf' WHERE id = 2")
cursor.execute("UPDATE buku_publikasi SET file_pdf = 'static/docs/publikasi/buku_saku_panduan_wisata_papayan.pdf' WHERE id = 4")

conn.commit()
conn.close()
print("=== BERHASIL MEMBERSIHKAN DATABASE DESA.DB! ===")
