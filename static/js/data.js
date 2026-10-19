/**
 * Data Lengkap Desa Papayan, Kecamatan Jatiwaras, Kabupaten Tasikmalaya, Jawa Barat
 * Portal Resmi Informasi & Pelayanan Publik Pemerintah Desa Papayan
 */

const desaData = {
  identitas: {
    namaDesa: "Papayan",
    sebutan: "Desa Papayan",
    tagline: "Desa Digital, Mandiri, dan Berprestasi",
    subtagline: "Pemerintah Desa Papayan, Kecamatan Jatiwaras, Kabupaten Tasikmalaya",
    kecamatan: "Jatiwaras",
    kabupaten: "Tasikmalaya",
    provinsi: "Jawa Barat",
    kodePos: "46197",
    kodeWilayah: "32.06.39.2001",
    alamatKantor: "Jalan Raya Papayan, Kecamatan Jatiwaras, Kabupaten Tasikmalaya, Jawa Barat 46197",
    telepon: "0821-7991-8783",
    email: "pemdes@papayan.desa.id",
    jamPelayanan: "Senin - Kamis (08.00 - 15.00) & Jum'at (08.00 - 11.00) WIB",
    koordinat: [-7.4782, 108.2055], // Pusat Pemerintahan Desa Papayan, Tasikmalaya
    tahunBerdiri: "1982",
    luasWilayah: "28,45 km²",
    batasWilayah: {
      utara: "Berbatasan dengan Desa Sukakerta / Desa Janggala",
      selatan: "Berbatasan dengan Desa Kertarahayu / Desa Jatiwaras",
      barat: "Berbatasan dengan Desa Sukaraja / Sungai Ciwulan",
      timur: "Berbatasan dengan Desa Neglasari / Desa Setiawangi"
    }
  },

  statistik: {
    totalPenduduk: 4945,
    lakiLaki: 2510,
    perempuan: 2435,
    kepalaKeluarga: 1735,
    pendudukSementara: 45,
    mutasiPenduduk: 18,
    dusun: 4, // Dusun Demung Landung, Dusun Ranca Sari, Dusun Margahayu, Dusun Cihaur
    rt: 26,
    kategoriPekerjaan: [
      { label: "Petani & Buruh Tani", jumlah: 1820, persen: 45 },
      { label: "Wiraswasta / Pedagang / UMKM", jumlah: 840, persen: 21 },
      { label: "Karyawan Swasta / BUMN", jumlah: 612, persen: 15 },
      { label: "Buruh Harian & Pertukangan", jumlah: 450, persen: 11 },
      { label: "PNS / Guru / TNI / POLRI", jumlah: 185, persen: 5 },
      { label: "Lainnya", jumlah: 120, persen: 3 }
    ],
    rentangUsia: [
      { label: "0 - 14 Tahun (Anak)", jumlah: 918 },
      { label: "15 - 24 Tahun (Pemuda)", jumlah: 752 },
      { label: "25 - 45 Tahun (Dewasa)", jumlah: 1720 },
      { label: "46 - 60 Tahun (Lansia Awal)", jumlah: 948 },
      { label: "> 60 Tahun (Lansia)", jumlah: 607 }
    ],
    pendidikan: [
      { label: "SD / Sederajat", jumlah: 1240 },
      { label: "SMP / Sederajat", jumlah: 1110 },
      { label: "SMA / SMK", jumlah: 1680 },
      { label: "Diploma / Sarjana", jumlah: 495 }
    ]
  },

  apbdes: {
    tahun: 2026,
    pendapatanTotal: 2540000000,
    belanjaTotal: 2490000000,
    pembiayaanNetto: 50000000,
    sumberPendapatan: [
      { sumber: "Dana Desa (APBN)", nominal: 1120000000, persen: 44.1 },
      { sumber: "Alokasi Dana Desa (ADD Kab. Tasikmalaya)", nominal: 980000000, persen: 38.6 },
      { sumber: "Bagi Hasil Pajak & Retribusi Daerah", nominal: 220000000, persen: 8.7 },
      { sumber: "Pendapatan Asli Desa (BUMDes & Pasar)", nominal: 140000000, persen: 5.5 },
      { sumber: "Bantuan Keuangan Provinsi Jawa Barat", nominal: 80000000, persen: 3.1 }
    ],
    alokasiBelanja: [
      { bidang: "Penyelenggaraan Pemerintahan Desa", nominal: 780000000, persen: 31.3 },
      { bidang: "Pelaksanaan Pembangunan Infrastruktur Desa", nominal: 990000000, persen: 39.8 },
      { bidang: "Pembinaan Kemasyarakatan Desa", nominal: 260000000, persen: 10.4 },
      { bidang: "Pemberdayaan Masyarakat & UMKM Pertanian", nominal: 340000000, persen: 13.7 },
      { bidang: "Penanggulangan Bencana & Keadaan Mendesak", nominal: 120000000, persen: 4.8 }
    ]
  },

  idm: {
    tahun: 2026,
    status: "DESA MAJU (Menuju Mandiri)",
    skorTotal: 0.8124,
    target: "Desa Mandiri",
    dimensi: [
      { nama: "Indeks Ketahanan Sosial (IKS)", skor: 0.8250, kategori: "Tinggi" },
      { nama: "Indeks Ketahanan Ekonomi (IKE)", skor: 0.7890, kategori: "Maju" },
      { nama: "Indeks Ketahanan Lingkungan (IKL)", skor: 0.8232, kategori: "Sangat Baik" }
    ]
  },

  perangkatDesa: [
    {
      nama: "Irwan Setiawan, S.Kom, M.T.",
      jabatan: "Kepala Desa Papayan",
      foto: "/static/images/kades.jpg",
      sambutanSingkat: "Mewujudkan Desa Papayan yang Maju, Sejahtera, Transparan, Berbasis Transformasi Digital.",
      kontak: "0821-7991-8783"
    },
    {
      nama: "Rahmat Hidayat, S.P",
      jabatan: "Sekretaris Desa",
      foto: "/static/images/sekdes.jpg",
      sambutanSingkat: "Mendukung tata kelola administrasi pemerintahan desa yang akuntabel, cepat, dan melayani warga setulus hati.",
      kontak: "0812-4455-8899"
    },
    {
      nama: "Siti Aminah, A.Md",
      jabatan: "Kaur Keuangan",
      foto: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&auto=format&fit=crop&q=80",
      sambutanSingkat: "Menjaga transparansi dan akuntabilitas pengelolaan APBDes demi pembangunan desa nyata.",
      kontak: "0823-1122-3344"
    },
    {
      nama: "Muhammad Yusuf",
      jabatan: "Kasi Pemerintahan",
      foto: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80",
      sambutanSingkat: "Melayani tertib administrasi kependudukan dan pertanahan desa secara ramah dan profesional.",
      kontak: "0852-3344-5566"
    },
    {
      nama: "Fatimah Azzahra, S.Pd",
      jabatan: "Kasi Kesejahteraan & Pelayanan",
      foto: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80",
      sambutanSingkat: "Mendorong pemberdayaan sosial, posyandu, kesehatan balita & lansia, serta layanan masyarakat umum.",
      kontak: "0813-7788-9900"
    },
    {
      nama: "Baharuddin, S.T",
      jabatan: "Kaur Umum & Perencanaan",
      foto: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80",
      sambutanSingkat: "Perencanaan infrastruktur fisik terpadu: jalan poros desa, irigasi pertanian, dan sarana publik.",
      kontak: "0821-9988-7766"
    },
    {
      nama: "H. Syamsir",
      jabatan: "Kepala Dusun Demung Landung",
      foto: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&auto=format&fit=crop&q=80",
      sambutanSingkat: "Mengawal keharmonisan warga dan percepatan program pembangunan di kawasan Dusun Demung Landung.",
      kontak: "0813-1234-5678"
    },
    {
      nama: "Rustam Efendi",
      jabatan: "Kepala Dusun Ranca Sari",
      foto: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&auto=format&fit=crop&q=80",
      sambutanSingkat: "Membangun gotong royong dan kemitraan masyarakat di wilayah Dusun Ranca Sari.",
      kontak: "0853-2233-4455"
    }
  ],

  wisata: [
    {
      id: "agrowisata-papayan",
      nama: "Agrowisata & Pertanian Terpadu Papayan",
      kategori: "Agrowisata & Edukasi",
      deskripsi: "Kawasan percontohan pertanian hortikultura, persawahan terasering, dan kebun bibit unggul binaan kelompok tani Desa Papayan.",
      fasilitas: ["Saung Tani", "Pusat Bibit Tanaman", "Spot Edukasi Tani", "Area Parkir", "Toilet & Musholla"],
      gambar: "/static/images/banner1.png",
      lokasi: "Dusun Ranca Sari, Desa Papayan",
      tiket: "Gratis"
    },
    {
      id: "taman-desa-papayan",
      nama: "Taman Rekreasi & Lapang Desa Papayan",
      kategori: "Ruang Terbuka Hijau",
      deskripsi: "Pusat kegiatan olahraga, kebugaran masyarakat, serta ruang interaksi pagelaran seni budaya warga Desa Papayan.",
      fasilitas: ["Lapang Sepakbola", "Jogging Track", "Gazebo Warga", "Kios UMKM", "Area Bermain Anak"],
      gambar: "/static/images/banner2.png",
      lokasi: "Dusun Margahayu, Desa Papayan",
      tiket: "Gratis"
    }
  ],

  umkm: [
    {
      id: 1,
      nama: "Madu Murni Asli Hutan Desa Papayan",
      produsen: "Kelompok Tani Lestari Papayan",
      harga: 85000,
      satuan: "Botol 350ml",
      rating: 4.9,
      terjual: 320,
      gambar: "/static/images/banner1.png",
      deskripsi: "Madu hutan murni alami tanpa campuran pemanis, dipanen langsung oleh kelompok tani hutan Desa Papayan, berkhasiat menjaga imunitas tubuh.",
      kontakWa: "6282179918783"
    },
    {
      id: 2,
      nama: "Keripik Tempe Renyah Gurih Desa Papayan",
      produsen: "Ibu Ani Papayan Berkah",
      harga: 15000,
      satuan: "Bungkus 200gr",
      rating: 4.8,
      terjual: 410,
      gambar: "/static/images/banner2.png",
      deskripsi: "Keripik tempe renyah bumbu rempah tradisional khas olahan rumahan warga Papayan. Renyah, gurih, dan halal.",
      kontakWa: "6282179918783"
    }
  ],

  berita: [
    {
      id: "berita-1",
      judul: "Pemerintah Desa Papayan Ikuti Pembinaan Program Desa Cantik (Cinta Statistik) 2026",
      tanggal: "18 Oktober 2026",
      kategori: "Pemerintahan",
      penulis: "Humas Pemdes Papayan",
      gambar: "/static/images/uploads/b2_1792274407.jpeg",
      ringkasan: "Desa Papayan terpilih dalam pembinaan Program Desa Cantik oleh BPS Kabupaten Tasikmalaya untuk penguatan tata kelola data kependudukan dan statistik desa berbasis SLS.",
      isi: "Desa Papayan, Kecamatan Jatiwaras terpilih sebagai salah satu desa binaan Program Desa Cantik (Desa Cinta Statistik) tahun 2026 yang diselenggarakan oleh Badan Pusat Statistik (BPS) Kabupaten Tasikmalaya."
    },
    {
      id: "berita-2",
      judul: "Penyaluran Bantuan Langsung Tunai (BLT) Dana Desa Papayan Berjalan Lancar & Tertib",
      tanggal: "15 Oktober 2026",
      kategori: "Sosial & Masyarakat",
      penulis: "Kaur Keuangan",
      gambar: "/static/images/banner1.png",
      ringkasan: "Pemerintah Desa Papayan menyalurkan BLT Dana Desa kepada puluhan Keluarga Penerima Manfaat (KPM) bertempat di Aula Pertemuan Desa.",
      isi: "Penyaluran Bantuan Langsung Tunai bersumber dari Dana Desa (BLT-DD) tahap terkini telah dilaksanakan secara tertib di Balai Pertemuan Desa Papayan."
    },
    {
      id: "berita-3",
      judul: "Musrenbangdes Penetapan RKPDes Papayan Fokus pada Peningkatan Pertanian & Layanan Digital",
      tanggal: "10 Oktober 2026",
      kategori: "Pembangunan",
      penulis: "Sekretariat Desa",
      gambar: "/static/images/banner2.png",
      ringkasan: "Musyawarah perencanaan pembangunan desa menyepakati prioritas anggaran tahun 2026 untuk perbaikan jalan usaha tani dan layanan digital warga.",
      isi: "Pemerintah Desa Papayan sukses menggelar Musyawarah Perencanaan Pembangunan Desa (Musrenbangdes). Berdasarkan musyawarah mufakat seluruh unsur kelembagaan desa, disepakati program prioritas meliputi perbaikan infrastruktur jalan pertanian dan digitalisasi pelayanan warga."
    }
  ],

  titikPeta: [
    {
      nama: "Kantor Desa Papayan",
      lat: -7.4782,
      lng: 108.2055,
      kategori: "Pemerintahan",
      deskripsi: "Pusat pelayanan administrasi & pemerintahan resmi Desa Papayan.",
      alamat: "Jl. Raya Papayan, Kec. Jatiwaras, Kab. Tasikmalaya",
      icon: "building-columns"
    },
    {
      nama: "Balai Pertemuan & GOR Desa Papayan",
      lat: -7.4785,
      lng: 108.2050,
      kategori: "Fasilitas Publik",
      deskripsi: "Gedung serbaguna dan sarana musyawarah warga Desa Papayan.",
      alamat: "Dusun Margahayu, Desa Papayan",
      icon: "users"
    },
    {
      nama: "Poskesdes / Pustu Desa Papayan",
      lat: -7.4778,
      lng: 108.2060,
      kategori: "Kesehatan",
      deskripsi: "Pelayanan kesehatan dasar, ibu dan anak, serta posyandu warga.",
      alamat: "Dusun Ranca Sari, Desa Papayan",
      icon: "heart-pulse"
    },
    {
      nama: "Masjid Jami' Desa Papayan",
      lat: -7.4770,
      lng: 108.2052,
      kategori: "Ibadah",
      deskripsi: "Pusat ibadah dan kegiatan keagamaan masyarakat Desa Papayan.",
      alamat: "Dusun Demung Landung, Desa Papayan",
      icon: "mosque"
    },
    {
      nama: "Sentra Agrowisata & Pertanian Papayan",
      lat: -7.4720,
      lng: 108.2070,
      kategori: "Pertanian & Potensi",
      deskripsi: "Kawasan percontohan pertanian dan perkebunan produktif warga.",
      alamat: "Dusun Ranca Sari, Desa Papayan",
      icon: "leaf"
    }
  ],

  layananSurat: [
    { id: "sku", kode: "510", nama: "Surat Keterangan Usaha (SKU)", syarat: ["Fotokopi KTP & KK", "Pengantar RT", "Foto Tempat Usaha"] },
    { id: "skd", kode: "470", nama: "Surat Keterangan Domisili (SKD)", syarat: ["Fotokopi KTP & KK", "Surat Pengantar RT"] },
    { id: "sktm", kode: "401", nama: "Surat Keterangan Tidak Mampu (SKTM)", syarat: ["Fotokopi KK & KTP", "Surat Pernyataan / Pengantar RT", "Foto Rumah"] },
    { id: "skbm", kode: "474", nama: "Surat Keterangan Belum Menikah", syarat: ["Fotokopi KTP & KK Pemohon", "Surat Pengantar RT", "Pernyataan Belum Menikah Bermaterai"] },
    { id: "skck", kode: "331", nama: "Surat Pengantar SKCK Polsek", syarat: ["Fotokopi KTP & KK", "Pas Foto 4x6 2 lembar", "Pengantar RT"] }
  ],

  galeri: [
    { judul: "Pelatihan Penguatan Kapasitas Data Desa Cantik 2026", url: "static/images/uploads/b2_1792274407.jpeg", kategori: "Pemerintahan" },
    { judul: "Penyaluran Bantuan Langsung Tunai di Balai Desa", url: "static/images/banner1.png", kategori: "Sosial" },
    { judul: "Musrenbang Penetapan RKPDes Papayan", url: "static/images/banner2.png", kategori: "Pembangunan" },
    { judul: "Kantor & Pelayanan Administrasi Desa Papayan", url: "static/images/kantor_desa.jpg", kategori: "Pemerintahan" }
  ]
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = desaData;
}
