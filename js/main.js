/**
 * Main Interactive Logic untuk Website Resmi Desa Kersik
 */

document.addEventListener('DOMContentLoaded', () => {
  initHeroCarousel();
  initVisitorCounter();
  initPerangkatDesa();
  initWisataSection();
  initUmkmSection();
  initBeritaSection();
  initGaleriSection();
  initLeafletMap();
  initCharts();
  initLayananSurat();
  initPengaduanForm();
  initMobileMenu();
});

/* ==========================================================
   1. HERO CAROUSEL
   ========================================================== */
let currentSlide = 0;
const slides = [
  {
    image: "assets/images/banner1.png",
    fallback: "assets/images/pantai_kersik.jpg",
    tag: "Wisata Bahari Unggulan",
    title: "Selamat Datang di Website Resmi Desa Kersik",
    desc: "Menjelajahi pesona Pantai Biru Kersik, kelestarian mangrove pesisir, dan kemajuan masyarakat Marang Kayu, Kutai Kartanegara."
  },
  {
    image: "assets/images/banner2.png",
    fallback: "assets/images/mangrove.jpg",
    tag: "Penghargaan Lingkungan Hidup",
    title: "Penerima Sertifikat Proklim Utama KLHK RI",
    desc: "Komitmen nyata masyarakat Desa Kersik dalam menjaga kelestarian lingkungan pesisir dan ketahanan iklim terpadu."
  },
  {
    image: "assets/images/pantai_kersik.jpg",
    tag: "Transformasi Digital 2026",
    title: "Pelayanan Publik Cepat, Transparan & Akuntabel",
    desc: "Nikmati kemudahan layanan pengajuan surat online mandiri, transparansi APBDes, dan keterbukaan informasi desa."
  }
];

function initHeroCarousel() {
  const container = document.getElementById('hero-slides-container');
  const dotsContainer = document.getElementById('carousel-dots');
  if (!container) return;

  container.innerHTML = slides.map((slide, index) => `
    <div class="carousel-slide absolute inset-0 w-full h-full transition-opacity duration-1000 ${index === 0 ? 'opacity-100 z-10' : 'opacity-0 z-0'}" data-slide="${index}">
      <img src="${slide.image}" onerror="this.src='${slide.fallback || 'assets/images/pantai_kersik.jpg'}'" class="w-full h-full object-cover brightness-[0.45]" alt="${slide.title}">
      <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-black/30 flex items-center">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full text-white pt-12 md:pt-16">
          <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-600/90 text-white backdrop-blur-md mb-4 border border-emerald-400/30">
            <span class="w-2 h-2 rounded-full bg-emerald-300 animate-ping"></span>
            ${slide.tag}
          </span>
          <h1 class="text-3xl sm:text-5xl lg:text-6xl font-extrabold max-w-3xl leading-tight text-white drop-shadow-md">
            ${slide.title}
          </h1>
          <p class="mt-4 text-base sm:text-xl text-gray-200 max-w-2xl leading-relaxed">
            ${slide.desc}
          </p>
          <div class="mt-8 flex flex-wrap gap-4">
            <a href="#layanan-surat" class="px-6 py-3.5 rounded-xl font-bold bg-emerald-500 hover:bg-emerald-600 text-white shadow-lg shadow-emerald-500/30 transition transform hover:-translate-y-0.5 flex items-center gap-2">
              <i class="fa-solid fa-file-signature"></i> Layanan Surat Mandiri
            </a>
            <a href="#wisata" class="px-6 py-3.5 rounded-xl font-bold bg-white/20 hover:bg-white/30 text-white backdrop-blur-md border border-white/30 transition transform hover:-translate-y-0.5 flex items-center gap-2">
              <i class="fa-solid fa-compass"></i> Jelajahi Potensi Desa
            </a>
          </div>
        </div>
      </div>
    </div>
  `).join('');

  if (dotsContainer) {
    dotsContainer.innerHTML = slides.map((_, i) => `
      <button onclick="goToSlide(${i})" class="w-3 h-3 rounded-full transition-all duration-300 ${i === 0 ? 'w-8 bg-emerald-400' : 'bg-white/60 hover:bg-white'}" aria-label="Slide ${i+1}"></button>
    `).join('');
  }

  // Auto play
  setInterval(nextSlide, 6000);
}

window.goToSlide = function(index) {
  const allSlides = document.querySelectorAll('.carousel-slide');
  const dots = document.querySelectorAll('#carousel-dots button');
  if (!allSlides.length) return;

  allSlides.forEach((s, i) => {
    if (i === index) {
      s.classList.remove('opacity-0', 'z-0');
      s.classList.add('opacity-100', 'z-10');
    } else {
      s.classList.remove('opacity-100', 'z-10');
      s.classList.add('opacity-0', 'z-0');
    }
  });

  dots.forEach((d, i) => {
    if (i === index) {
      d.classList.add('w-8', 'bg-emerald-400');
      d.classList.remove('bg-white/60');
    } else {
      d.classList.remove('w-8', 'bg-emerald-400');
      d.classList.add('bg-white/60');
    }
  });

  currentSlide = index;
};

window.nextSlide = function() {
  currentSlide = (currentSlide + 1) % slides.length;
  goToSlide(currentSlide);
};

window.prevSlide = function() {
  currentSlide = (currentSlide - 1 + slides.length) % slides.length;
  goToSlide(currentSlide);
};

/* ==========================================================
   2. VISITOR COUNTER
   ========================================================== */
function initVisitorCounter() {
  const today = document.getElementById('count-today');
  const month = document.getElementById('count-month');
  const total = document.getElementById('count-total');
  
  if (today) today.innerText = "142";
  if (month) month.innerText = "3.840";
  if (total) total.innerText = "28.519";
}

/* ==========================================================
   3. PERANGKAT DESA / SOTK
   ========================================================== */
function initPerangkatDesa() {
  const container = document.getElementById('perangkat-desa-grid');
  if (!container) return;

  container.innerHTML = desaData.perangkatDesa.map(item => `
    <div class="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 card-hover flex flex-col">
      <div class="relative h-64 overflow-hidden bg-gray-100">
        <img src="${item.foto}" alt="${item.nama}" class="w-full h-full object-cover transition duration-500 hover:scale-105" onerror="this.src='https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80'">
        <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent p-4 text-white">
          <p class="text-xs uppercase tracking-wider font-semibold text-emerald-300">${item.jabatan}</p>
          <h3 class="font-bold text-lg leading-snug">${item.nama}</h3>
        </div>
      </div>
      <div class="p-4 flex-1 flex flex-col justify-between">
        <p class="text-xs text-gray-500 italic mb-4 leading-relaxed">"${item.sambutanSingkat}"</p>
        <div class="pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-600">
          <span class="flex items-center gap-1.5 text-emerald-700 font-medium">
            <i class="fa-solid fa-id-badge"></i> Perangkat Desa
          </span>
          <a href="https://wa.me/${item.kontak.replace(/[^0-9]/g, '')}" target="_blank" class="hover:text-emerald-600 flex items-center gap-1 font-semibold">
            <i class="fa-brands fa-whatsapp text-emerald-500 text-sm"></i> Kontak
          </a>
        </div>
      </div>
    </div>
  `).join('');
}

/* ==========================================================
   4. WISATA & POTENSI DESA
   ========================================================== */
function initWisataSection() {
  const container = document.getElementById('wisata-grid');
  if (!container) return;

  container.innerHTML = desaData.wisata.map(w => `
    <div class="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 card-hover flex flex-col group">
      <div class="relative h-56 overflow-hidden">
        <img src="${w.gambar}" alt="${w.nama}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
        <div class="absolute top-3 left-3 bg-emerald-700/90 backdrop-blur-md text-white text-xs font-bold px-3 py-1 rounded-full shadow-sm">
          ${w.kategori}
        </div>
      </div>
      <div class="p-6 flex-1 flex flex-col">
        <h3 class="text-xl font-bold text-gray-900 group-hover:text-emerald-700 transition">${w.nama}</h3>
        <p class="text-xs font-semibold text-gray-400 mt-1 flex items-center gap-1.5">
          <i class="fa-solid fa-location-dot text-emerald-600"></i> ${w.lokasi}
        </p>
        <p class="text-sm text-gray-600 mt-3 leading-relaxed flex-1">${w.deskripsi}</p>
        
        <div class="mt-4 pt-4 border-t border-gray-100">
          <p class="text-xs font-bold text-gray-700 mb-2">Fasilitas Utama:</p>
          <div class="flex flex-wrap gap-1.5 mb-4">
            ${w.fasilitas.map(f => `<span class="bg-emerald-50 text-emerald-800 text-[11px] font-medium px-2 py-0.5 rounded-md">${f}</span>`).join('')}
          </div>
          <div class="flex items-center justify-between pt-2">
            <span class="text-xs font-bold text-emerald-800 bg-emerald-100/70 px-2.5 py-1 rounded-lg">
              ${w.tiket}
            </span>
            <button onclick="bukaModalWisata('${w.id}')" class="text-xs font-bold text-emerald-700 hover:text-emerald-800 flex items-center gap-1">
              Detail Lengkap <i class="fa-solid fa-arrow-right"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  `).join('');
}

window.bukaModalWisata = function(id) {
  const w = desaData.wisata.find(item => item.id === id);
  if (!w) return;

  const modal = document.getElementById('general-modal');
  const modalContent = document.getElementById('general-modal-content');

  modalContent.innerHTML = `
    <div class="p-6 sm:p-8">
      <div class="flex items-center justify-between pb-4 border-b border-gray-100 mb-4">
        <div>
          <span class="text-xs font-bold text-emerald-600 uppercase tracking-wider">${w.kategori}</span>
          <h3 class="text-2xl font-bold text-gray-900">${w.nama}</h3>
        </div>
        <button onclick="tutupModal()" class="text-gray-400 hover:text-gray-600 p-2 text-xl font-bold">&times;</button>
      </div>
      <img src="${w.gambar}" class="w-full h-72 object-cover rounded-xl mb-4" alt="${w.nama}">
      <p class="text-gray-700 leading-relaxed text-sm mb-4">${w.deskripsi}</p>
      <div class="bg-emerald-50 p-4 rounded-xl border border-emerald-100 mb-4">
        <h4 class="font-bold text-emerald-900 text-sm mb-2"><i class="fa-solid fa-circle-check text-emerald-600 mr-1"></i> Fasilitas & Layanan Wisatawan:</h4>
        <ul class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-emerald-800">
          ${w.fasilitas.map(f => `<li class="flex items-center gap-2"><i class="fa-solid fa-check text-emerald-500"></i> ${f}</li>`).join('')}
        </ul>
      </div>
      <div class="flex items-center justify-between text-xs text-gray-500 pt-2">
        <span><i class="fa-solid fa-map-pin mr-1 text-emerald-600"></i> ${w.lokasi}</span>
        <a href="#peta" onclick="tutupModal()" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-4 py-2 rounded-lg text-xs flex items-center gap-1.5">
          <i class="fa-solid fa-map"></i> Lihat di Peta Desa
        </a>
      </div>
    </div>
  `;

  modal.classList.remove('hidden');
};

/* ==========================================================
   5. UMKM & BELANJA DARI DESA
   ========================================================== */
function initUmkmSection() {
  const container = document.getElementById('umkm-grid');
  if (!container) return;

  container.innerHTML = desaData.umkm.map(prod => `
    <div class="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 card-hover flex flex-col group">
      <div class="relative h-52 overflow-hidden bg-gray-50">
        <img src="${prod.gambar}" alt="${prod.nama}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
        <span class="absolute top-3 right-3 bg-white/90 backdrop-blur-md text-emerald-700 text-xs font-bold px-2.5 py-1 rounded-full shadow-sm flex items-center gap-1">
          <i class="fa-solid fa-star text-amber-400"></i> ${prod.rating} (${prod.terjual} terjual)
        </span>
      </div>
      <div class="p-5 flex-1 flex flex-col">
        <span class="text-[11px] font-semibold text-emerald-700 uppercase tracking-wider">${prod.produsen}</span>
        <h3 class="font-bold text-gray-900 text-base mt-1 line-clamp-1 group-hover:text-emerald-700 transition">${prod.nama}</h3>
        <p class="text-xs text-gray-500 mt-2 line-clamp-2 leading-relaxed flex-1">${prod.deskripsi}</p>
        
        <div class="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between">
          <div>
            <p class="text-[11px] text-gray-400">Harga / ${prod.satuan}</p>
            <p class="text-lg font-black text-emerald-700">Rp ${prod.harga.toLocaleString('id-ID')}</p>
          </div>
          <a href="https://wa.me/${prod.kontakWa}?text=Halo%20Admin%20Desa%20Kersik,%20saya%20tertarik%20membeli%20produk%20UMKM:%20${encodeURIComponent(prod.nama)}" target="_blank" class="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center gap-1.5 shadow-sm transition">
            <i class="fa-brands fa-whatsapp text-sm"></i> Beli
          </a>
        </div>
      </div>
    </div>
  `).join('');
}

/* ==========================================================
   6. BERITA DESA
   ========================================================== */
function initBeritaSection() {
  const container = document.getElementById('berita-grid');
  if (!container) return;

  container.innerHTML = desaData.berita.map(b => `
    <article class="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 card-hover flex flex-col">
      <div class="relative h-48 overflow-hidden">
        <img src="${b.gambar}" alt="${b.judul}" class="w-full h-full object-cover">
        <span class="absolute top-3 left-3 bg-emerald-600/90 text-white text-[11px] font-bold px-3 py-0.5 rounded-full backdrop-blur-md">
          ${b.kategori}
        </span>
      </div>
      <div class="p-5 flex-1 flex flex-col">
        <div class="flex items-center gap-3 text-xs text-gray-400 mb-2">
          <span><i class="fa-regular fa-calendar mr-1"></i> ${b.tanggal}</span>
          <span>•</span>
          <span><i class="fa-regular fa-user mr-1"></i> ${b.penulis}</span>
        </div>
        <h3 class="font-bold text-gray-900 text-base leading-snug hover:text-emerald-700 transition line-clamp-2 mb-2">
          <a href="javascript:void(0)" onclick="bukaModalBerita('${b.id}')">${b.judul}</a>
        </h3>
        <p class="text-xs text-gray-600 line-clamp-3 leading-relaxed flex-1">${b.ringkasan}</p>
        <div class="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between">
          <button onclick="bukaModalBerita('${b.id}')" class="text-xs font-bold text-emerald-700 hover:text-emerald-800 flex items-center gap-1">
            Baca Selengkapnya <i class="fa-solid fa-arrow-right text-[10px]"></i>
          </button>
        </div>
      </div>
    </article>
  `).join('');
}

window.bukaModalBerita = function(id) {
  const b = desaData.berita.find(item => item.id === id);
  if (!b) return;

  const modal = document.getElementById('general-modal');
  const modalContent = document.getElementById('general-modal-content');

  modalContent.innerHTML = `
    <div class="p-6 sm:p-8">
      <div class="flex items-center justify-between pb-4 border-b border-gray-100 mb-4">
        <div>
          <span class="text-xs font-bold text-emerald-600 uppercase tracking-wider">${b.kategori}</span>
          <h3 class="text-xl sm:text-2xl font-bold text-gray-900 mt-1">${b.judul}</h3>
          <div class="flex items-center gap-3 text-xs text-gray-400 mt-2">
            <span><i class="fa-regular fa-calendar mr-1"></i> ${b.tanggal}</span>
            <span>•</span>
            <span><i class="fa-regular fa-user mr-1"></i> Oleh ${b.penulis}</span>
          </div>
        </div>
        <button onclick="tutupModal()" class="text-gray-400 hover:text-gray-600 p-2 text-2xl font-bold">&times;</button>
      </div>
      <img src="${b.gambar}" class="w-full h-80 object-cover rounded-xl mb-6" alt="${b.judul}">
      <div class="prose text-gray-700 text-sm leading-relaxed space-y-4">
        <p class="font-semibold text-gray-800">${b.ringkasan}</p>
        <p>${b.isi}</p>
        <p>Pemerintah Desa Kersik senantiasa berkomitmen untuk memberikan keterbukaan informasi dan pelayanan terbaik bagi segenap warga maupun pelancong.</p>
      </div>
      <div class="mt-8 pt-4 border-t border-gray-100 flex justify-end">
        <button onclick="tutupModal()" class="px-5 py-2.5 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-bold">
          Tutup
        </button>
      </div>
    </div>
  `;

  modal.classList.remove('hidden');
};

/* ==========================================================
   7. GALERI FOTO KEGIATAN
   ========================================================== */
function initGaleriSection() {
  const container = document.getElementById('galeri-grid');
  if (!container) return;

  container.innerHTML = desaData.galeri.map(item => `
    <div class="group relative rounded-2xl overflow-hidden shadow-sm h-52 cursor-pointer" onclick="lihatFotoModal('${item.url}', '${item.judul}')">
      <img src="${item.url}" alt="${item.judul}" class="w-full h-full object-cover transition duration-500 group-hover:scale-110">
      <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition duration-300 flex flex-col justify-end p-4 text-white">
        <span class="text-[10px] font-bold text-emerald-300 uppercase tracking-wider">${item.kategori}</span>
        <h4 class="text-xs font-bold leading-tight mt-0.5">${item.judul}</h4>
      </div>
    </div>
  `).join('');
}

window.lihatFotoModal = function(url, caption) {
  const modal = document.getElementById('general-modal');
  const modalContent = document.getElementById('general-modal-content');

  modalContent.innerHTML = `
    <div class="p-4 sm:p-6 bg-black/90 text-white rounded-2xl">
      <div class="flex justify-between items-center pb-3 mb-2">
        <h4 class="text-sm font-semibold">${caption}</h4>
        <button onclick="tutupModal()" class="text-gray-300 hover:text-white text-2xl font-bold">&times;</button>
      </div>
      <img src="${url}" class="w-full max-h-[75vh] object-contain rounded-lg" alt="${caption}">
    </div>
  `;

  modal.classList.remove('hidden');
};

window.tutupModal = function() {
  const modal = document.getElementById('general-modal');
  if (modal) modal.classList.add('hidden');
};

/* ==========================================================
   8. INTERACTIVE LEAFLET MAP
   ========================================================== */
function initLeafletMap() {
  const mapElement = document.getElementById('map');
  if (!mapElement || typeof L === 'undefined') return;

  const kersikCoord = desaData.identitas.koordinat;
  const map = L.map('map').setView(kersikCoord, 14);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Desa Kersik',
    maxZoom: 19
  }).addTo(map);

  // Custom green marker icon
  const customIcon = L.divIcon({
    className: 'custom-map-pin',
    html: `<div style="background-color:#3d920c;color:white;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 10px rgba(0,0,0,0.3);border:2px solid white;">
            <i class="fa-solid fa-location-dot text-sm"></i>
          </div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 34],
    popupAnchor: [0, -30]
  });

  // Render markers
  desaData.titikPeta.forEach(pt => {
    const marker = L.marker([pt.lat, pt.lng], { icon: customIcon }).addTo(map);
    marker.bindPopup(`
      <div style="font-family:'Outfit',sans-serif;min-width:180px;padding:4px;">
        <span style="font-size:10px;text-transform:uppercase;color:#3d920c;font-weight:700;">${pt.kategori}</span>
        <h4 style="margin:2px 0 4px;font-size:14px;font-weight:700;color:#0f172a;">${pt.nama}</h4>
        <p style="margin:0 0 6px;font-size:12px;color:#475569;line-height:1.4;">${pt.deskripsi}</p>
        <p style="margin:0;font-size:11px;color:#64748b;font-weight:500;">
          <i class="fa-solid fa-map-pin" style="color:#3d920c;"></i> ${pt.alamat}
        </p>
      </div>
    `);
  });
}

/* ==========================================================
   9. STATISTIK & INFOGRAFIS (CHART.JS)
   ========================================================== */
function initCharts() {
  if (typeof Chart === 'undefined') return;

  // Chart Kategori Usia
  const ctxUsia = document.getElementById('chartUsia');
  if (ctxUsia) {
    new Chart(ctxUsia, {
      type: 'bar',
      data: {
        labels: desaData.statistik.rentangUsia.map(u => u.label),
        datasets: [{
          label: 'Jumlah Jiwa',
          data: desaData.statistik.rentangUsia.map(u => u.jumlah),
          backgroundColor: '#3d920c',
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: { grid: { color: '#f1f5f9' }, beginAtZero: true }
        }
      }
    });
  }

  // Chart Pekerjaan Warga
  const ctxPekerjaan = document.getElementById('chartPekerjaan');
  if (ctxPekerjaan) {
    new Chart(ctxPekerjaan, {
      type: 'doughnut',
      data: {
        labels: desaData.statistik.kategoriPekerjaan.map(p => p.label),
        datasets: [{
          data: desaData.statistik.kategoriPekerjaan.map(p => p.jumlah),
          backgroundColor: [
            '#3d920c', '#6bd731', '#0ea5e9', '#f59e0b', '#8b5cf6', '#94a3b8'
          ],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
        }
      }
    });
  }

  // Chart Alokasi Belanja APBDes
  const ctxApbdes = document.getElementById('chartApbdes');
  if (ctxApbdes) {
    new Chart(ctxApbdes, {
      type: 'pie',
      data: {
        labels: desaData.apbdes.alokasiBelanja.map(b => b.bidang),
        datasets: [{
          data: desaData.apbdes.alokasiBelanja.map(b => b.nominal),
          backgroundColor: [
            '#10b981', '#3b82f6', '#f59e0b', '#ec4899', '#6366f1'
          ],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 10 } } }
        }
      }
    });
  }
}

/* ==========================================================
   10. LAYANAN SURAT MANDIRI (SURAT ONLINE)
   ========================================================== */
function initLayananSurat() {
  const form = document.getElementById('form-layanan-surat');
  const selectSurat = document.getElementById('pilih-jenis-surat');
  const syaratList = document.getElementById('syarat-surat-list');

  if (selectSurat) {
    selectSurat.innerHTML = `
      <option value="">-- Pilih Jenis Layanan Surat --</option>
      ${desaData.layananSurat.map(s => `
        <option value="${s.id}">${s.nama} (${s.kode})</option>
      `).join('')}
    `;

    selectSurat.addEventListener('change', (e) => {
      const selected = desaData.layananSurat.find(s => s.id === e.target.value);
      if (selected && syaratList) {
        syaratList.innerHTML = `
          <div class="p-3 bg-emerald-50 rounded-xl border border-emerald-200 text-xs text-emerald-900 mt-2">
            <p class="font-bold mb-1"><i class="fa-solid fa-circle-info"></i> Dokumen Persyaratan yang Perlu Disiapkan:</p>
            <ul class="list-disc list-inside space-y-0.5 text-emerald-800">
              ${selected.syarat.map(item => `<li>${item}</li>`).join('')}
            </ul>
          </div>
        `;
      } else if (syaratList) {
        syaratList.innerHTML = '';
      }
    });
  }

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      
      const jenisId = document.getElementById('pilih-jenis-surat').value;
      const jenisObj = desaData.layananSurat.find(s => s.id === jenisId);
      const nik = document.getElementById('surat-nik').value;
      const nama = document.getElementById('surat-nama').value;
      const wa = document.getElementById('surat-wa').value;
      const dusun = document.getElementById('surat-dusun').value;
      const rt = document.getElementById('surat-rt').value;
      const keperluan = document.getElementById('surat-keperluan').value;

      if (!jenisObj) {
        alert("Silakan pilih jenis surat!");
        return;
      }

      // Generate nomor registrasi unik
      const noReg = `KSK-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`;

      // Buka modal bukti registrasi surat
      const modal = document.getElementById('general-modal');
      const modalContent = document.getElementById('general-modal-content');

      modalContent.innerHTML = `
        <div id="print-area" class="p-6 sm:p-8 bg-white rounded-2xl">
          <!-- Kop Surat Resmi -->
          <div class="text-center border-b-2 border-gray-800 pb-4 mb-6">
            <h4 class="text-xs uppercase font-bold tracking-widest text-gray-600">Pemerintah Kabupaten Kutai Kartanegara</h4>
            <h4 class="text-xs uppercase font-bold tracking-widest text-gray-600">Kecamatan Marang Kayu</h4>
            <h3 class="text-xl sm:text-2xl font-black uppercase text-gray-900 mt-1">Pemerintah Desa Kersik</h3>
            <p class="text-[11px] text-gray-500 mt-0.5">Alamat: Jl. Langaseng Dusun Empang RT.003, Desa Kersik, Marang Kayu 75385 | Email: pemdes@kersik.desa.id</p>
          </div>

          <div class="text-center mb-6">
            <span class="inline-block px-3 py-1 bg-emerald-100 text-emerald-800 text-xs font-bold rounded-full mb-2">
              BUKTI PENGAJUAN SURAT ONLINE MANDIRI
            </span>
            <h2 class="text-lg font-bold text-gray-900 uppercase underline">${jenisObj.nama}</h2>
            <p class="text-xs font-mono text-gray-600 mt-1">Nomor Registrasi: <strong>${noReg}</strong></p>
          </div>

          <table class="w-full text-xs text-gray-700 mb-6">
            <tbody>
              <tr class="border-b border-gray-100 py-1.5"><td class="w-36 font-semibold py-1.5">Nama Pemohon</td><td class="font-bold">: ${nama}</td></tr>
              <tr class="border-b border-gray-100 py-1.5"><td class="font-semibold py-1.5">NIK (KTP)</td><td>: ${nik}</td></tr>
              <tr class="border-b border-gray-100 py-1.5"><td class="font-semibold py-1.5">Dusun / RT</td><td>: ${dusun} / RT.${rt}</td></tr>
              <tr class="border-b border-gray-100 py-1.5"><td class="font-semibold py-1.5">Nomor WhatsApp</td><td>: ${wa}</td></tr>
              <tr class="border-b border-gray-100 py-1.5"><td class="font-semibold py-1.5">Keperluan</td><td>: ${keperluan}</td></tr>
              <tr class="border-b border-gray-100 py-1.5"><td class="font-semibold py-1.5">Waktu Pengajuan</td><td>: ${new Date().toLocaleDateString('id-ID', { dateStyle: 'full' })}</td></tr>
            </tbody>
          </table>

          <div class="p-3 bg-gray-50 border border-gray-200 rounded-xl text-xs text-gray-600 mb-6">
            <p class="font-bold text-gray-800 mb-1"><i class="fa-solid fa-circle-check text-emerald-600"></i> Petunjuk Pengambilan:</p>
            <p>1. Simpan bukti ini atau screenshot nomor registrasi Anda.</p>
            <p>2. Petugas pelayanan Desa Kersik akan memverifikasi berkas dan mengirim notifikasi WhatsApp bila surat telah selesai ditandatangani.</p>
            <p>3. Surat dapat diambil di Kantor Desa Kersik dengan membawa fotokopi dokumen persyaratan.</p>
          </div>

          <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-gray-100 no-print">
            <button onclick="window.print()" class="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center gap-2">
              <i class="fa-solid fa-print"></i> Cetak Bukti Permohonan
            </button>
            <button onclick="tutupModal()" class="px-5 py-2.5 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold text-xs">
              Selesai & Tutup
            </button>
          </div>
        </div>
      `;

      modal.classList.remove('hidden');
      form.reset();
      if (syaratList) syaratList.innerHTML = '';
    });
  }
}

/* ==========================================================
   11. FORM PENGADUAN / ASPIRASI WARGA
   ========================================================== */
function initPengaduanForm() {
  const form = document.getElementById('form-pengaduan');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const nama = document.getElementById('aduan-nama').value;
    const kategori = document.getElementById('aduan-kategori').value;
    const pesan = document.getElementById('aduan-pesan').value;

    const noTiket = `ADUAN-${Math.floor(10000 + Math.random() * 90000)}`;

    alert(`Terima kasih Bapak/Ibu ${nama}.\nAspirasi Anda mengenai [${kategori}] telah diterima oleh Humas Pemdes Kersik dengan Nomor Tiket: ${noTiket}.\nKami akan segera menindaklanjuti laporan Anda.`);
    form.reset();
  });
}

/* ==========================================================
   12. MOBILE MENU & TAB TOGGLING
   ========================================================== */
function initMobileMenu() {
  const toggleBtn = document.getElementById('mobile-menu-toggle');
  const menu = document.getElementById('mobile-menu-dropdown');

  if (toggleBtn && menu) {
    toggleBtn.addEventListener('click', () => {
      menu.classList.toggle('hidden');
    });

    // Close menu when link is clicked
    menu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        menu.classList.add('hidden');
      });
    });
  }
}
