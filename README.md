# Website & Sistem Manajemen Desa Kersik, Kec. Marang Kayu, Kab. Kutai Kartanegara

Portal web profil desa interaktif lengkap dengan **Frontend Publik** (mengadopsi [kersik.desa.id](https://kersik.desa.id/)) dan **Backend CMS Admin** berbasis **Python Flask & SQLite** untuk pengelolaan data desa secara mandiri.

---

## 🌟 Fitur Utama Sistem

### 1. Frontend Publik (`/`)
- **Beranda Interaktif**: Hero Carousel Pantai Biru Kersik & Penghargaan Proklim Utama KLHK RI.
- **Menu Cepat (Quick Action)**: 8 grid navigasi cepat + App Bar mengambang pada smartphone.
- **Peta Digital (Leaflet.js)**: Titik lokasi Kantor Desa, Pantai Kersik, Mangrove Center, Dermaga Nelayan, Pustu, dan Masjid.
- **Transparansi APBDes & IDM**: Publikasi anggaran pendapatan/belanja serta status Desa Maju (skor 0,7984).
- **Statistik Kependudukan (Chart.js)**: Grafik interaktif kelompok usia dan komposisi mata pencaharian nelayan.
- **Katalog UMKM (Beli Dari Desa)**: Tombol pemesanan via WhatsApp otomatis ke nomor perajin.
- **Layanan Pengajuan Surat Mandiri**: Form online (SKU, Domisili, SKTM, dll) yang langsung tersimpan ke basis data backend dengan penerbitan nomor registrasi unik.
- **Cetak Surat Resmi Format Dinas (`/surat/<no_reg>/cetak`)**: Kop surat resmi Pemkab Kutai Kartanegara, QR code validasi, dan siap cetak langsung / simpan PDF.
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
  - Kelola daya tarik Pantai Biru Kersik, tiket, fasilitas, dan foto.
- **Manajemen Aparatur SOTK (`/admin/aparatur`)**:
  - Kelola data Kepala Desa, Sekretaris, Kasi, Kaur, dan Kadus.
- **Pengaturan Statistik & APBDes (`/admin/statistik`)**:
  - Update jumlah penduduk dan angka realisasi APBDes (otomatis memperbarui grafik di website publik).
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
│   ├── index.html             # Halaman portal publik (adopsi kersik.desa.id)
│   ├── surat_cetak.html       # Format cetak surat resmi berkop dinas
│   ├── base_admin.html        # Layout master panel admin
│   └── admin/
│       ├── login.html         # Halaman login administrator
│       ├── dashboard.html     # Ikhtisar statistik & aktivitas desa
│       ├── surat.html         # Manajemen permohonan surat masuk
│       ├── pengaduan.html     # Manajemen aduan & tanggapan warga
│       ├── berita.html        # CRUD artikel & warta desa
│       ├── umkm.html          # CRUD produk UMKM warga
│       ├── wisata.html        # CRUD potensi & wisata bahari
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
