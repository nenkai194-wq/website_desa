/**
 * SISTEM MODE PENCAHAYAAN (TERANG & GELAP)
 * Pengaturan pencahayaan ramah mata pengunjung website Desa Papayan
 */

// 1. Eksekusi awal secepat mungkin (Mencegah FOUC / kedipan layar)
(function initThemeImmediately() {
  try {
    const saved = localStorage.getItem('desa_papayan_theme');
    if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  } catch (e) {}
})();

// 2. Fungsi Toggle Terang / Gelap
window.toggleThemeMode = function() {
  const isDark = document.documentElement.classList.toggle('dark');
  try {
    localStorage.setItem('desa_papayan_theme', isDark ? 'dark' : 'light');
  } catch (e) {}
  updateThemeToggleUI(isDark);
};

// 3. Update Visual Seluruh Tombol & Ikon
window.updateThemeToggleUI = function(isDark) {
  if (typeof isDark === 'undefined') {
    isDark = document.documentElement.classList.contains('dark');
  }

  // Header Desktop
  const icon = document.getElementById('theme-toggle-icon');
  const text = document.getElementById('theme-toggle-text');
  const btn = document.getElementById('theme-toggle-btn');
  if (icon) {
    icon.className = isDark ? 'fa-solid fa-sun text-amber-300 text-sm sm:text-base animate-spin-slow' : 'fa-solid fa-moon text-amber-200 text-sm sm:text-base';
  }
  if (text) {
    text.innerText = isDark ? 'Mode Terang' : 'Mode Gelap';
  }
  if (btn) {
    btn.title = isDark ? 'Beralih ke Mode Terang' : 'Beralih ke Mode Gelap';
    btn.setAttribute('aria-label', isDark ? 'Beralih ke Mode Terang' : 'Beralih ke Mode Gelap');
  }

  // Mobile Drawer
  const iconMob = document.getElementById('theme-toggle-icon-mobile');
  const textMob = document.getElementById('theme-toggle-text-mobile');
  if (iconMob) {
    iconMob.className = isDark ? 'fa-solid fa-sun text-amber-300 w-4' : 'fa-solid fa-moon text-amber-200 w-4';
  }
  if (textMob) {
    textMob.innerText = isDark ? 'Mode Terang' : 'Mode Gelap';
  }

  // Floating Button (jika ada)
  const iconFloat = document.getElementById('theme-toggle-icon-float');
  const textFloat = document.getElementById('theme-toggle-text-float');
  if (iconFloat) {
    iconFloat.className = isDark ? 'fa-solid fa-sun text-amber-300 text-sm' : 'fa-solid fa-moon text-amber-200 text-sm';
  }
  if (textFloat) {
    textFloat.innerText = isDark ? 'Terang' : 'Gelap';
  }

  // Admin Header (jika di panel admin)
  const iconAdmin = document.getElementById('theme-toggle-icon-admin');
  const textAdmin = document.getElementById('theme-toggle-text-admin');
  if (iconAdmin) {
    iconAdmin.className = isDark ? 'fa-solid fa-sun text-amber-400 text-xs' : 'fa-solid fa-moon text-slate-400 text-xs';
  }
  if (textAdmin) {
    textAdmin.innerText = isDark ? 'Terang' : 'Gelap';
  }
};

// 4. Sinkronisasi UI saat DOM Loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    updateThemeToggleUI();
  });
} else {
  updateThemeToggleUI();
}
