# Website & Sistem Manajemen Desa Papayan, Kec. Jatiwaras, Kab. Tasikmalaya

Portal web profil desa interaktif lengkap dengan **Frontend Publik** dan **Backend CMS Admin** berbasis **Python Flask & SQLite** untuk pengelolaan data serta pelayanan publik desa secara terpadu.

---

## 🌟 Fitur Utama Sistem

### 1. Frontend Publik (`/`)
- **Beranda Interaktif**: Hero Carousel potensi unggulan Desa Papayan & Program Pembinaan Desa Cantik.
- **Menu Cepat (Quick Action)**: 8 grid navigasi cepat + App Bar mengambang pada smartphone.
- **Peta Digital & GIS SLS RT/RW (Leaflet.js)**: Titik lokasi Kantor Desa, sentra UMKM, agrowisata, dan poligon tematik batas wilayah SLS 26 RT dari 4 Dusun (Demung Landung, Ranca Sari, Margahayu, Cihaur).
- **Transparansi APBDes & Statistik**: Publikasi anggaran pendapatan/belanja serta infografis kependudukan presisi.
- **Statistik Kependudukan (Chart.js)**: Grafik interaktif kelompok usia, pekerjaan warga, tingkat pendidikan, dan data kesejahteraan.
- **Katalog UMKM (Beli Dari Desa)**: Tombol pemesanan via WhatsApp otomatis ke nomor pengrajin/produsen lokal Papayan.
- **Layanan Pengajuan Surat Mandiri**: Form online (SKU, Domisili, SKTM, dll) yang langsung tersimpan ke basis data backend dengan penerbitan nomor registrasi unik.
- **Cetak Surat Resmi Format Dinas (`/surat/<no_reg>/cetak`)**: Kop surat resmi Pemerintah Desa Papayan Kab. Tasikmalaya, QR code validasi, dan siap cetak langsung / simpan PDF.
- **Formulir Pengaduan / Aspirasi Warga**: Kanal komunikasi warga dengan nomor tiket pelacakan otomatis.

---

### 2. Backend & Panel Admin CMS (`/admin`)
- **Keamanan & Autentikasi**: Sistem login berbasis sesi dan password hashing (`Werkzeug`).
- **Dashboard Ringkasan**: Indikator jumlah surat masuk, aduan baru, berita aktif, dan produk UMKM.
- **Manajemen Permohonan Surat (`/admin/surat`)**:
  - Filter berkas: *Menunggu*, *Diproses*, *Selesai*.
  - Update status permohonan dan catatan admin.
  - Tombol **Cetak Surat Resmi** berkop dinas.
- **Manajemen Aspirasi Warga (`/admin/pengaduan`)**:
  - Tinjau pesan warga dan kirim tanggapan resmi dari pihak Pemdes.
- **Manajemen Berita & Pengumuman (`/admin/berita`)**:
  - Tambah, edit, dan hapus artikel berita kegiatan desa.
- **Manajemen Produk UMKM (`/admin/umkm`)**:
  - Tambah/edit produk, harga, satuan, foto, dan nomor WhatsApp penjual.
- **Manajemen Wisata & Potensi (`/admin/wisata`)**:
  - Kelola daya tarik wisata alam, agrowisata, tiket, fasilitas, koordinat, dan foto.
- **Manajemen Aparatur SOTK (`/admin/aparatur`)**:
  - Kelola data Kepala Desa, Sekretaris, Kasi, Kaur, dan Kadus.
  - Kelola Sejarah Desa & Rekam Jejak Kepala Desa dari Masa ke Masa.
- **Pengaturan Statistik & APBDes (`/admin/statistik`)**:
  - Update data penduduk, SLS RT/RW, dan angka realisasi APBDes (otomatis memperbarui grafik di website publik).
- **Pengaturan Identitas Desa (`/admin/profil`)**:
  - Kelola alamat kantor, telepon, email, jam pelayanan, sambutan Kades, dan visi-misi.

---

## 🔑 Kredensial Login Administrator

- **URL Login Admin**: `http://localhost:5000/admin/login`
- **Username**: `admin`
- **Password**: `admin123`

---

## 🚀 Cara Menjalankan Aplikasi

1. Pastikan dependensi Flask terpasang (sudah tersedia pada lingkungan Python).
2. Jalankan backend:
   ```bash
   python app.py
   ```
3. Buka peramban (browser):
   - **Website Publik**: [http://localhost:5000](http://localhost:5000)
   - **Panel Admin CMS**: [http://localhost:5000/admin](http://localhost:5000/admin)

---

## 📁 Struktur Direktori Proyek

```
website_desa/
├── app.py                     # Backend Flask (Route publik, API, & Admin CMS)
├── database.py                # Skema SQLite desa.db & data seeding
├── desa.db                    # Basis data SQLite lokal
├── templates/                 # Template antarmuka Jinja2
│   ├── index.html             # Halaman portal publik terpadu Desa Papayan
│   ├── surat_cetak.html       # Format cetak surat resmi berkop dinas
│   ├── base_admin.html        # Layout master panel admin
│   └── admin/
│       ├── login.html         # Halaman login administrator
│       ├── dashboard.html     # Ikhtisar statistik & aktivitas desa
│       ├── surat.html         # Manajemen permohonan surat masuk
│       ├── pengaduan.html     # Manajemen aduan & tanggapan warga
│       ├── berita.html        # CRUD artikel & warta desa
│       ├── umkm.html          # CRUD produk UMKM warga
│       ├── wisata.html        # CRUD potensi & objek wisata desa
│       ├── aparatur.html      # CRUD SOTK perangkat desa
│       ├── statistik.html     # Form update kependudukan & APBDes
│       └── profil.html        # Form profil, kontak, & visi-misi
├── static/                    # Berkas statis
│   ├── css/
│   │   └── style.css          # Styling Outfit & kustomisasi cetak
│   ├── js/
│   │   ├── data.js            # Data pendukung
│   │   └── main.js            # Slider, Leaflet Map, Chart.js
│   └── images/                # Logo Kutai Kartanegara, foto pantai & produk
└── README.md                  # Dokumentasi teknis
```
