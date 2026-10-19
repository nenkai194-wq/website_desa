import os
import re
import urllib.request

def export_site():
    base_url = 'http://localhost:8080'
    
    pages = [
        ('/', 'index.html'),
        ('/peta', 'peta.html'),
        ('/publikasi', 'publikasi.html'),
        ('/pembangunan', 'pembangunan.html')
    ]
    
    pub_docs = {
        '1': 'static/docs/publikasi/buku_profil_desa_papayan_2026.pdf',
        '2': 'static/docs/publikasi/buku_desa_papayan_dalam_angka_2026.pdf',
        '3': 'static/docs/publikasi/laporan_transparansi_apbdes_2025_2026.pdf',
        '4': 'static/docs/publikasi/buku_saku_panduan_wisata_papayan.pdf'
    }

    # Simulation script to handle form submissions gracefully on GitHub Pages
    gh_pages_shim = """
<script>
// GitHub Pages Mock Handler for API endpoints
(function() {
  if (window.location.hostname.includes('github.io')) {
    const originalFetch = window.fetch;
    window.fetch = async function(url, options) {
      if (typeof url === 'string') {
        if (url.includes('/api/surat/ajukan')) {
          const fakeReg = 'REG-DESA-' + Math.floor(100000 + Math.random() * 900000);
          return new Response(JSON.stringify({
            success: true,
            no_reg: fakeReg,
            cetak_url: '#',
            message: 'Permohonan surat berhasil disimulasikan di GitHub Pages.'
          }), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }
        if (url.includes('/api/pengaduan/kirim')) {
          const fakeTiket = 'PPD-' + new Date().getFullYear() + '-' + Math.floor(1000 + Math.random() * 9000);
          return new Response(JSON.stringify({
            success: true,
            nomor_tiket: fakeTiket,
            message: 'Pengaduan berhasil dicatat dalam mode online.'
          }), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }
        if (url.includes('/api/feedback/kirim')) {
          return new Response(JSON.stringify({
            success: true,
            message: 'Terima kasih atas penilaian kepuasan Anda!'
          }), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }
        if (url.includes('/api/umkm/ajukan') || url.includes('/api/wisata/ajukan') || url.includes('/galeri/ajukan')) {
          return new Response(JSON.stringify({
            success: true,
            message: 'Pengajuan data berhasil diterima.'
          }), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }
        if (url.includes('/api/pengaduan/tracking/')) {
          const parts = url.split('/api/pengaduan/tracking/');
          const tiket = parts[1] || 'DEMO';
          return new Response(JSON.stringify({
            success: true,
            aduan: {
              nomor_tiket: decodeURIComponent(tiket),
              status: 'Sedang Diproses',
              kategori: 'Pelayanan Publik',
              perihal: 'Pengecekan Berkas Online',
              created_at: new Date().toLocaleDateString('id-ID'),
              tanggapan: 'Pengaduan Anda telah masuk antrean verifikasi tim administrasi desa.'
            }
          }), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }
      }
      return originalFetch.apply(this, arguments);
    };
  }
})();
</script>
"""

    for route, filename in pages:
        url = base_url + route
        print(f"Mengambil {url} -> {filename}...")
        try:
            with urllib.request.urlopen(url) as resp:
                content = resp.read().decode('utf-8')
        except Exception as e:
            print(f"Gagal mengambil {url}: {e}")
            continue

        # 1. Transform /static/ paths to relative static/
        content = content.replace('"/static/', '"static/')
        content = content.replace("'/static/", "'static/")
        content = content.replace('url(/static/', 'url(static/')
        content = content.replace('url("/static/', 'url("static/')
        content = content.replace("url('/static/", "url('static/")
        content = content.replace('content="/static/', 'content="static/')
        content = content.replace("content='/static/", "content='static/")

        # 2. Transform navigation routes
        content = re.sub(r'href=["\']/peta["\']', 'href="peta.html"', content)
        content = re.sub(r'href=["\']/publikasi["\']', 'href="publikasi.html"', content)
        content = re.sub(r'href=["\']/pembangunan["\']', 'href="pembangunan.html"', content)
        content = re.sub(r'href=["\']/#([^"\']+)["\']', r'href="index.html#\1"', content)
        content = re.sub(r'href=["\']/["\']', 'href="index.html"', content)

        # 3. Transform publication download links
        for pub_id, pdf_path in pub_docs.items():
            content = content.replace(f'/publikasi/unduh/{pub_id}', pdf_path)
            content = content.replace(f'/api/publikasi/{pub_id}/counter', '#')

        # 4. Transform Admin links to friendly notification on static GitHub Pages
        content = content.replace('href="/admin/login"', 'href="#admin-modal" onclick="alert(\'Panel Admin CMS berbasis server Python Flask. Pada hosting statis GitHub Pages, silakan jalankan website di komputer lokal atau deploy ke server cloud backend untuk mengakses Dashboard CMS Admin.\'); return false;"')
        content = content.replace('href="/admin"', 'href="#admin-modal" onclick="alert(\'Panel Admin CMS berbasis server Python Flask. Pada hosting statis GitHub Pages, silakan jalankan website di komputer lokal atau deploy ke server cloud backend untuk mengakses Dashboard CMS Admin.\'); return false;"')

        # 5. Inject GitHub Pages shim before </head>
        if '</head>' in content:
            content = content.replace('</head>', gh_pages_shim + '\n</head>')
        else:
            content = gh_pages_shim + content

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Berhasil membuat {filename} ({len(content)} karakter)")

if __name__ == '__main__':
    export_site()
