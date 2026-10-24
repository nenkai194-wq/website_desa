/**
 * Visitor Counter Dinamis Website Desa Papayan
 * Mengelola statistik pengunjung (Hari Ini, Minggu Ini, Bulan Ini, Total Kunjungan)
 * secara dinamis dengan persistensi localStorage dan live real-time simulation.
 */
(function() {
  function formatRibuan(n) {
    return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  }

  function parseAngka(text, defVal) {
    if (!text) return defVal;
    const clean = text.replace(/[^0-9]/g, '');
    const val = parseInt(clean, 10);
    return isNaN(val) ? defVal : val;
  }

  function getTodayString() {
    const d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }

  function updateDom(stats, animate) {
    const elToday = document.getElementById('count-today');
    const elWeek = document.getElementById('count-week');
    const elMonth = document.getElementById('count-month');
    const elTotal = document.getElementById('count-total');

    // Juga dukung widget floating jika ada
    const floatToday = document.getElementById('stat-val-today');
    const floatWeek = document.getElementById('stat-val-week');
    const floatMonth = document.getElementById('stat-val-month');
    const floatTotal = document.getElementById('stat-val-total');
    const pillToday = document.getElementById('pill-stat-today');

    if (elToday) elToday.innerText = formatRibuan(stats.today);
    if (elWeek) elWeek.innerText = formatRibuan(stats.week);
    if (elMonth) elMonth.innerText = formatRibuan(stats.month);
    if (elTotal) elTotal.innerText = formatRibuan(stats.total);

    if (floatToday) floatToday.innerText = formatRibuan(stats.today);
    if (floatWeek) floatWeek.innerText = formatRibuan(stats.week);
    if (floatMonth) floatMonth.innerText = formatRibuan(stats.month);
    if (floatTotal) floatTotal.innerText = formatRibuan(stats.total);
    if (pillToday) pillToday.innerText = formatRibuan(stats.today);

    if (animate && elToday) {
      elToday.classList.add('text-emerald-400');
      setTimeout(() => elToday.classList.remove('text-emerald-400'), 1500);
    }
  }

  function initStats() {
    const todayStr = getTodayString();
    const elToday = document.getElementById('count-today');
    const elWeek = document.getElementById('count-week');
    const elMonth = document.getElementById('count-month');
    const elTotal = document.getElementById('count-total');

    let baseToday = elToday ? parseAngka(elToday.innerText, 158) : 158;
    let baseWeek = elWeek ? parseAngka(elWeek.innerText, 1175) : 1175;
    let baseMonth = elMonth ? parseAngka(elMonth.innerText, 4249) : 4249;
    let baseTotal = elTotal ? parseAngka(elTotal.innerText, 28928) : 28928;

    let saved = null;
    try {
      saved = JSON.parse(localStorage.getItem('desa_papayan_visitor_stats'));
    } catch(e) {}

    const now = Date.now();
    let stats = {
      date: todayStr,
      today: baseToday,
      week: baseWeek,
      month: baseMonth,
      total: baseTotal,
      lastUpdate: now
    };

    if (saved && typeof saved.today === 'number') {
      if (saved.date === todayStr) {
        // Masih hari yang sama, gunakan nilai tersimpan yang lebih tinggi
        stats.today = Math.max(baseToday, saved.today);
        stats.week = Math.max(baseWeek, saved.week);
        stats.month = Math.max(baseMonth, saved.month);
        stats.total = Math.max(baseTotal, saved.total);
      } else {
        // Hari berganti
        stats.today = 142 + Math.floor(Math.random() * 8);
        stats.week = Math.max(baseWeek, saved.week + stats.today);
        stats.month = Math.max(baseMonth, saved.month + stats.today);
        stats.total = Math.max(baseTotal, saved.total + stats.today);
      }

      // Kunjungan baru: jika sudah lebih dari 20 detik sejak pembaruan terakhir
      if (!saved.lastUpdate || (now - saved.lastUpdate > 20000)) {
        stats.today += 1;
        stats.week += 1;
        stats.month += 1;
        stats.total += 1;
        stats.lastUpdate = now;
      }
    } else {
      stats.today += 1;
      stats.week += 1;
      stats.month += 1;
      stats.total += 1;
    }

    try {
      localStorage.setItem('desa_papayan_visitor_stats', JSON.stringify(stats));
    } catch(e) {}

    updateDom(stats, false);

    // Live dynamic increment berkala (simulasi pengunjung online aktif di portal desa)
    function jadwalkanLiveHit() {
      // Waktu acak antara 25 s/d 55 detik
      const delay = 25000 + Math.random() * 30000;
      setTimeout(() => {
        // Peluang 75% bertambah 1 pengunjung
        if (Math.random() < 0.75) {
          stats.today += 1;
          stats.week += 1;
          stats.month += 1;
          stats.total += 1;
          stats.lastUpdate = Date.now();
          try {
            localStorage.setItem('desa_papayan_visitor_stats', JSON.stringify(stats));
          } catch(e) {}
          updateDom(stats, true);
        }
        jadwalkanLiveHit();
      }, delay);
    }
    jadwalkanLiveHit();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initStats);
  } else {
    initStats();
  }
})();
