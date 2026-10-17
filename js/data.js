/**
 * Data Lengkap Desa Kersik, Kecamatan Marang Kayu, Kabupaten Kutai Kartanegara
 * Diadopsi dari identitas resmi https://kersik.desa.id/
 */

const desaData = {
  identitas: {
    namaDesa: "Kersik",
    sebutan: "Desa Kersik",
    tagline: "Desa Wisata Pesisir Marang Kayu - Menuju Desa Maju & Berkelanjutan",
    subtagline: "Penerima Penghargaan Kampung Iklim (Proklim) Utama KLHK Republik Indonesia",
    kecamatan: "Marang Kayu",
    kabupaten: "Kutai Kartanegara",
    provinsi: "Kalimantan Timur",
    kodePos: "75385",
    kodeWilayah: "64.02.17.2005",
    alamatKantor: "Jalan Langaseng Dusun Empang RT.003, Desa Kersik",
    telepon: "0821-5020-8664",
    email: "pemdes@kersik.desa.id",
    jamPelayanan: "Senin - Kamis (08.00 - 15.00) & Jum'at (08.00 - 11.00)",
    koordinat: [-0.0682, 117.3854], // Pesisir Marang Kayu Kutai Kartanegara
    tahunBerdiri: "1982",
    luasWilayah: "42,85 km²",
    batasWilayah: {
      utara: "Desa Sebuntal",
      selatan: "Selat Makassar / Desa Santan Ulu",
      barat: "Desa Semangko",
      timur: "Selat Makassar"
    }
  },

  statistik: {
    totalPenduduk: 2486,
    lakiLaki: 1278,
    perempuan: 1208,
    kepalaKeluarga: 742,
    pendudukSementara: 84,
    mutasiPenduduk: 27,
    dusun: 3, // Dusun Empang, Dusun Kersik, Dusun Muara
    rt: 10,
    kategoriPekerjaan: [
      { label: "Nelayan & Budidaya Laut", jumlah: 820, persen: 48 },
      { label: "Petani & Perkebunan", jumlah: 310, persen: 18 },
      { label: "Pedagang & UMKM", jumlah: 245, persen: 14 },
      { label: "Pekerja Tambak/Jasa", jumlah: 185, persen: 11 },
      { label: "PNS/Guru/Perangkat", jumlah: 80, persen: 5 },
      { label: "Lainnya", jumlah: 70, persen: 4 }
    ],
    rentangUsia: [
      { label: "0 - 14 Tahun (Anak)", jumlah: 590 },
      { label: "15 - 24 Tahun (Pemuda)", jumlah: 480 },
      { label: "25 - 45 Tahun (Dewasa)", jumlah: 860 },
      { label: "46 - 60 Tahun (Lansia Awal)", jumlah: 376 },
      { label: "> 60 Tahun (Lansia)", jumlah: 180 }
    ],
    pendidikan: [
      { label: "SD / Sederajat", jumlah: 640 },
      { label: "SMP / Sederajat", jumlah: 710 },
      { label: "SMA / SMK", jumlah: 840 },
      { label: "Diploma / Sarjana", jumlah: 296 }
    ]
  },

  apbdes: {
    tahun: 2026,
    pendapatanTotal: 2540000000,
    belanjaTotal: 2490000000,
    pembiayaanNetto: 50000000,
    sumberPendapatan: [
      { sumber: "Dana Desa (APBN)", nominal: 1120000000, persen: 44.1 },
      { sumber: "Alokasi Dana Desa (ADD Kukar)", nominal: 980000000, persen: 38.6 },
      { sumber: "Bagi Hasil Pajak & Retribusi Daerah", nominal: 220000000, persen: 8.7 },
      { sumber: "Pendapatan Asli Desa (BUMDes & Wisata)", nominal: 140000000, persen: 5.5 },
      { sumber: "Bantuan Keuangan Provinsi / CSR", nominal: 80000000, persen: 3.1 }
    ],
    alokasiBelanja: [
      { bidang: "Penyelenggaraan Pemerintahan Desa", nominal: 780000000, persen: 31.3 },
      { bidang: "Pelaksanaan Pembangunan Desa (Infrastruktur & Pesisir)", nominal: 990000000, persen: 39.8 },
      { bidang: "Pembinaan Kemasyarakatan Desa", nominal: 260000000, persen: 10.4 },
      { bidang: "Pemberdayaan Masyarakat (Pelatihan Nelayan & UMKM)", nominal: 340000000, persen: 13.7 },
      { bidang: "Penanggulangan Bencana & Darurat", nominal: 120000000, persen: 4.8 }
    ]
  },

  idm: {
    tahun: 2026,
    status: "DESA MAJU (Menuju Mandiri)",
    skorTotal: 0.7984,
    target: "Desa Mandiri",
    dimensi: [
      { nama: "Indeks Ketahanan Sosial (IKS)", skor: 0.8120, kategori: "Tinggi" },
      { nama: "Indeks Ketahanan Ekonomi (IKE)", skor: 0.7740, kategori: "Sedang Menuju Maju" },
      { nama: "Indeks Ketahanan Lingkungan (IKL)", skor: 0.8092, kategori: "Sangat Baik (Proklim)" }
    ]
  },

  perangkatDesa: [
    {
      nama: "Jumadi, S.Sos",
      jabatan: "Kepala Desa Kersik",
      foto: "assets/images/kades.jpg",
      sambutanSingkat: "Mewujudkan Desa Kersik yang Maju, Sejahtera, Transparan, Berbasis Wisata Bahari dan Lingkungan Berkelanjutan.",
      kontak: "0821-5020-8664"
    },
    {
      nama: "Rahmat Hidayat, S.P",
      jabatan: "Sekretaris Desa",
      foto: "assets/images/sekdes.jpg",
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
      sambutanSingkat: "Mendorong pemberdayaan sosial, posyandu, pendidikan anak nelayan, dan layanan masyarakat umum.",
      kontak: "0813-7788-9900"
    },
    {
      nama: "Baharuddin, S.T",
      jabatan: "Kaur Umum & Perencanaan",
      foto: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80",
      sambutanSingkat: "Perencanaan infrastruktur fisik terpadu: jalan pesisir, dermaga nelayan, dan fasilitas penunjang wisata.",
      kontak: "0821-9988-7766"
    },
    {
      nama: "H. Syamsir",
      jabatan: "Kepala Dusun Empang",
      foto: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&auto=format&fit=crop&q=80",
      sambutanSingkat: "Mengawal keharmonisan warga dan percepatan program pembangunan di kawasan Dusun Empang.",
      kontak: "0813-1234-5678"
    },
    {
      nama: "Rustam Efendi",
      jabatan: "Kepala Dusun Kersik",
      foto: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&auto=format&fit=crop&q=80",
      sambutanSingkat: "Membangun gotong royong dan kemitraan kelompok nelayan di pesisir Dusun Kersik.",
      kontak: "0853-2233-4455"
    }
  ],

  wisata: [
    {
      id: "pantai-biru-kersik",
      nama: "Pantai Biru Kersik (Pantai Kersik)",
      kategori: "Wisata Bahari Unggulan",
      deskripsi: "Ikon pariwisata bahari Desa Kersik yang berbatasan langsung dengan Selat Makassar. Menampilkan bentangan pasir bersih, ombak tenang, deretan cemara laut rindang, dan jembatan kayu estetik yang menjorok ke laut.",
      fasilitas: ["Jembatan Foto Laut", "Camping Ground", "Saung / Gazebo Santai", "Warung Kuliner Pesisir", "Toilet & Kamar Bilas", "Homestay Warga"],
      gambar: "assets/images/pantai_kersik.jpg",
      lokasi: "Pesisir Selat Makassar, Dusun Kersik",
      tiket: "Rp 5.000 / orang (Kebersihan & Parkir Pokdarwis)"
    },
    {
      id: "mangrove-kersik",
      nama: "Ekowisata & Konservasi Mangrove Kersik",
      kategori: "Ekowisata & Lingkungan (Proklim)",
      deskripsi: "Kawasan hutan bakau rimbun penahan abrasi pantai yang dikelola swadaya oleh Pokdarwis dan Pemdes Kersik. Menghantarkan Desa Kersik meraih penghargaan Kampung Iklim (Proklim) Utama dari KLHK RI.",
      fasilitas: ["Track Kayu Susur Mangrove", "Pusat Pembibitan Bakau", "Spot Bird Watching", "Edukasi Adopsi Pohon Mangrove", "Pondok Edukasi"],
      gambar: "assets/images/mangrove.jpg",
      lokasi: "Kawasan Pesisir Muara, Desa Kersik",
      tiket: "Gratis / Donasi Bibit Mangrove"
    },
    {
      id: "kampung-nelayan-tambak",
      nama: "Kampung Nelayan & Wisata Edukasi Tambak",
      kategori: "Wisata Budidaya & Pemancingan",
      deskripsi: "Menyajikan pengalaman memancing air payau, melihat budidaya udang windu dan ikan bandeng, serta proses tradisional pembuatan ikan asin dan terasi khas pesisir Kutai Kartanegara.",
      fasilitas: ["Spot Pemancingan", "Sewa Perahu Nelayan", "Warung Ikan Bakar Segar", "Pusat Pengolahan Ikan"],
      gambar: "assets/images/tambak.jpg",
      lokasi: "Dusun Empang & Muara Kersik",
      tiket: "Sesuai aktivitas / sewa alat"
    }
  ],

  umkm: [
    {
      id: 1,
      nama: "Terasi Udang Rebon Asli Kersik (Khas Marang Kayu)",
      produsen: "KWT Melati Pesisir Kersik",
      harga: 25000,
      satuan: "Pack 250gr",
      rating: 4.9,
      terjual: 450,
      gambar: "assets/images/produk_terasi.jpg",
      deskripsi: "Dibuat dari 100% udang rebon tangkapan nelayan Desa Kersik, diolah secara alami tanpa bahan pengawet kimia, harum gurih dan sangat legit untuk sambal.",
      kontakWa: "6282150208664"
    },
    {
      id: 2,
      nama: "Kerupuk Ikan Tenggiri Gurih Renyah",
      produsen: "UMKM Pesisir Berkah Kersik",
      harga: 20000,
      satuan: "Bungkus 200gr",
      rating: 4.8,
      terjual: 380,
      gambar: "assets/images/produk_kerupuk.jpg",
      deskripsi: "Olahan ikan tenggiri segar hasil laut Selat Makassar. Renyah, gurih nikmat, cocok untuk oleh-oleh khas Kutai Kartanegara.",
      kontakWa: "6282150208664"
    },
    {
      id: 3,
      nama: "Ikan Asin Kering Super (Tenggiri & Biawan)",
      produsen: "Kelompok Nelayan Dusun Empang",
      harga: 45000,
      satuan: "Pack 500gr",
      rating: 4.9,
      terjual: 290,
      gambar: "assets/images/nelayan.jpg",
      deskripsi: "Ikan segar hasil tangkapan harian yang dikeringkan dengan penjemuran sinar matahari pesisir. Daging tebal, gurih dan higienis.",
      kontakWa: "6282150208664"
    },
    {
      id: 4,
      nama: "Souvenir Miniatur Perahu & Kerajinan Kerang Laut",
      produsen: "Karang Taruna Bahari Kersik",
      harga: 35000,
      satuan: "Pcs",
      rating: 4.7,
      terjual: 120,
      gambar: "https://images.unsplash.com/photo-1544816155-12df9643f363?w=800&auto=format&fit=crop&q=80",
      deskripsi: "Karya seni tangan pemuda desa memanfaatkan limbah kerang pesisir pantai dan kayu lokal menjadi hiasan rumah bernilai tinggi.",
      kontakWa: "6282150208664"
    }
  ],

  berita: [
    {
      id: "berita-1",
      judul: "Pemdes Kersik Gelar Gerakan Tanam 1.000 Mangrove Perkuat Ketahanan Proklim Pesisir",
      tanggal: "12 Oktober 2026",
      kategori: "Lingkungan & Wisata",
      penulis: "Humas Pemdes Kersik",
      gambar: "assets/images/mangrove.jpg",
      ringkasan: "Sebagai peraih penghargaan Proklim Utama KLHK, warga bersama Pokdarwis dan pelajar menanam 1.000 bibit mangrove di pesisir Selat Makassar.",
      isi: "Desa Kersik kembali menegaskan komitmennya dalam menjaga kelestarian ekosistem bahari. Pada Minggu pagi, Pemerintah Desa Kersik bersama Dinas Lingkungan Hidup Kabupaten Kutai Kartanegara dan ratusan warga Dusun Empang menggelar aksi penanaman 1.000 bibit mangrove jenis Rhizophora di area bibir pantai. Kepala Desa Kersik, Jumadi S.Sos, menyatakan bahwa gerakan ini menjaga keberlanjutan penghargaan Kampung Iklim (Proklim) Utama sekaligus mencegah bahaya abrasi bagi pemukiman nelayan."
    },
    {
      id: "berita-2",
      judul: "Kunjungan Wisatawan Pantai Biru Kersik Meningkat Pesat pada Akhir Pekan",
      tanggal: "04 Oktober 2026",
      kategori: "Pariwisata Desa",
      penulis: "Pokdarwis Kersik",
      gambar: "assets/images/pantai_kersik.jpg",
      ringkasan: "Pantai Biru Kersik menjadi primadona wisata keluarga asal Samarinda dan Bontang berkat jembatan laut dan suasana cemara yang asri.",
      isi: "Pantai Biru Kersik terus menarik animo pelancong dari berbagai kabupaten/kota di Kalimantan Timur. Akses jalan yang semakin mulus dari simpang Marang Kayu membuat wisatawan dari Bontang, Samarinda, dan Tenggarong berbondong-bondong datang berkemah dan menikmati kuliner laut bakar segar di saung-saung Pokdarwis. Pihak Pemdes juga terus melengkapi fasilitas sanitasi dan tempat ibadah di kawasan pantai."
    },
    {
      id: "berita-3",
      judul: "Penyaluran BLT Dana Desa dan Bantuan Alat Tangkap Nelayan Berjalan Lancar",
      tanggal: "25 September 2026",
      kategori: "Pemerintahan & Sosial",
      penulis: "Kasi Kesejahteraan",
      gambar: "assets/images/kantor_desa.jpg",
      ringkasan: "Sebanyak 65 KPM menerima BLT triwulan ketiga dan 20 kelompok nelayan menerima jaring ramah lingkungan di Balai Pertemuan Desa.",
      isi: "Transparansi dan ketepatan sasaran penyaluran bantuan sosial senantiasa menjadi prioritas utama Pemdes Kersik. Bertempat di Balai Pertemuan Kantor Desa Kersik, BPD dan Pendamping Desa turut mengawasi penyerahan bantuan tunai bersumber dari Dana Desa tahun 2026 serta alat kelengkapan keselamatan bagi nelayan tangkap tradisional."
    }
  ],

  titikPeta: [
    {
      nama: "Kantor Desa Kersik",
      lat: -0.0682,
      lng: 117.3854,
      kategori: "Pemerintahan",
      deskripsi: "Pusat pelayanan administrasi & pemerintahan Desa Kersik.",
      alamat: "Jl. Langaseng Dusun Empang RT.003",
      icon: "building-columns"
    },
    {
      nama: "Pantai Biru Kersik (Pantai Kersik)",
      lat: -0.0635,
      lng: 117.3980,
      kategori: "Wisata",
      deskripsi: "Destinasi wisata bahari unggulan, jembatan laut, dan camping ground.",
      alamat: "Pesisir Dusun Kersik",
      icon: "umbrella-beach"
    },
    {
      nama: "Ekowisata & Mangrove Center Kersik",
      lat: -0.0725,
      lng: 117.3910,
      kategori: "Lingkungan",
      deskripsi: "Kawasan edukasi konservasi bakau dan peraih Proklim Utama KLHK.",
      alamat: "Kawasan Muara Pesisir",
      icon: "tree"
    },
    {
      nama: "Dermaga Pendaratan Ikan (TPI Nelayan)",
      lat: -0.0660,
      lng: 117.3940,
      kategori: "Perikanan",
      deskripsi: "Pusat bongkar muat hasil laut nelayan dan spot pasar ikan segar.",
      alamat: "Dusun Empang Pesisir",
      icon: "ship"
    },
    {
      nama: "Puskesmas Pembantu (Pustu) Kersik",
      lat: -0.0690,
      lng: 117.3830,
      kategori: "Kesehatan",
      deskripsi: "Pelayanan kesehatan dasar, ibu dan anak, serta pengobatan warga.",
      alamat: "Jl. Poros Desa Kersik",
      icon: "heart-pulse"
    },
    {
      nama: "Masjid Jami' Al-Ikhlas Kersik",
      lat: -0.0675,
      lng: 117.3860,
      kategori: "Ibadah",
      deskripsi: "Pusat ibadah dan kegiatan keagamaan masyarakat Desa Kersik.",
      alamat: "Dusun Empang",
      icon: "mosque"
    }
  ],

  layananSurat: [
    { id: "sku", kode: "510", nama: "Surat Keterangan Usaha (SKU)", syarat: ["Fotokopi KTP & KK", "Pengantar RT", "Foto Tempat Usaha"] },
    { id: "skd", kode: "470", nama: "Surat Keterangan Domisili (SKD)", syarat: ["Fotokopi KTP & KK", "Surat Pengantar RT"] },
    { id: "sktm", kode: "401", nama: "Surat Keterangan Tidak Mampu (SKTM)", syarat: ["Fotokopi KK & KTP", "Surat Pernyataan / Pengantar RT", "Foto Rumah"] },
    { id: "skbm", kode: "474", nama: "Surat Keterangan Belum Menikah", syarat: ["Fotokopi KTP & KK Pemohon", "Surat Pengantar RT", "Pernyataan Belum Menikah Bermaterai"] },
    { id: "skck", kode: "331", nama: "Surat Pengantar SKCK Polsek", syarat: ["Fotokopi KTP & KK", "Pas Foto 4x6 2 lembar", "Pengantar RT"] },
    { id: "skk", kode: "472", nama: "Surat Keterangan Kelahiran / Kematian", syarat: ["Surat Keterangan Bidan/RS", "KTP Orang Tua / Saksi", "Buku Nikah & KK"] }
  ],

  galeri: [
    { judul: "Panorama Jembatan Pantai Biru Kersik", url: "assets/images/pantai_kersik.jpg", kategori: "Wisata" },
    { judul: "Kawasan Hutan Mangrove Lestari Kersik", url: "assets/images/mangrove.jpg", kategori: "Lingkungan" },
    { judul: "Aktivitas Perahu Nelayan Selat Makassar", url: "assets/images/nelayan.jpg", kategori: "Masyarakat" },
    { judul: "Hamparan Tambak Budidaya Udang & Bandeng", url: "assets/images/tambak.jpg", kategori: "Potensi" },
    { judul: "Gedung Balai & Kantor Desa Kersik", url: "assets/images/kantor_desa.jpg", kategori: "Pemerintahan" },
    { judul: "Produk Olahan Terasi Rebon & Kerupuk UMKM", url: "assets/images/produk_terasi.jpg", kategori: "UMKM" }
  ]
};
