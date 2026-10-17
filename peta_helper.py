import os
import json
import io
import zipfile
import urllib.request
import xml.etree.ElementTree as ET
from database import get_db

DEFAULT_KML_URL = 'https://www.google.com/maps/d/kml?mid=1dkqA9acPAb0AOLjjlN6Vb_meNM6nc1k'
LOCAL_KML_PATH = os.path.join(os.path.dirname(__file__), 'desa_polygon.kml')
GEOJSON_CACHE_PATH = os.path.join(os.path.dirname(__file__), 'static', 'data', 'peta_sls.geojson')

# Data Koordinat Pusat SLS (RT/RW) Resmi Desa Papayan
RT_COORDINATES_MAP = {
    'RT 001 RW 003': {'lat': -7.4683202, 'lng': 108.2062075, 'dusun': 'DUSUN RANCA SARI', 'nama_lengkap': 'RT 001 RW 003 DUSUN RANCA SARI'},
    'RT 002 RW 003': {'lat': -7.4700012, 'lng': 108.2069189, 'dusun': 'DUSUN RANCA SARI', 'nama_lengkap': 'RT 002 RW 003 DUSUN RANCA SARI'},
    'RT 002 RW 006': {'lat': -7.4867264, 'lng': 108.1981448, 'dusun': 'DUSUN CIHAUR', 'nama_lengkap': 'RT 002 RW 006 DUSUN CIHAUR'},
    'RT 001 RW 006': {'lat': -7.4934828, 'lng': 108.1959009, 'dusun': 'DUSUN CIHAUR', 'nama_lengkap': 'RT 001 RW 006 DUSUN CIHAUR'},
    'RT 003 RW 006': {'lat': -7.4893041, 'lng': 108.1948713, 'dusun': 'DUSUN CIHAUR', 'nama_lengkap': 'RT 003 RW 006 DUSUN CIHAUR'},
    'RT 001 RW 002': {'lat': -7.4659631, 'lng': 108.2088363, 'dusun': 'DUSUN RANCA SARI', 'nama_lengkap': 'RT 001 RW 002 DUSUN RANCA SARI'},
    'RT 002 RW 002': {'lat': -7.4669964, 'lng': 108.2111364, 'dusun': 'DUSUN RANCA SARI', 'nama_lengkap': 'RT 002 RW 002 DUSUN RANCA SARI'},
    'RT 004 RW 002': {'lat': -7.4699779, 'lng': 108.2142913, 'dusun': 'DUSUN RANCA SARI', 'nama_lengkap': 'RT 004 RW 002 DUSUN RANCA SARI'},
    'RT 003 RW 002': {'lat': -7.4664316, 'lng': 108.2100832, 'dusun': 'DUSUN RANCA SARI', 'nama_lengkap': 'RT 003 RW 002 DUSUN RANCA SARI'},
    'RT 002 RW 004': {'lat': -7.4812463, 'lng': 108.2049746, 'dusun': 'DUSUN MARGAHAYU', 'nama_lengkap': 'RT 002 RW 004 DUSUN MARGAHAYU'},
    'RT 001 RW 005': {'lat': -7.4905728, 'lng': 108.2050619, 'dusun': 'DUSUN CIHAUR', 'nama_lengkap': 'RT 001 RW 005 DUSUN CIHAUR'},
    'RT 002 RW 005': {'lat': -7.4935217, 'lng': 108.2028620, 'dusun': 'DUSUN CIHAUR', 'nama_lengkap': 'RT 002 RW 005 DUSUN CIHAUR'},
    'RT 003 RW 005': {'lat': -7.4935720, 'lng': 108.2008101, 'dusun': 'DUSUN CIHAUR', 'nama_lengkap': 'RT 003 RW 005 DUSUN CIHAUR'},
    'RT 002 RW 001': {'lat': -7.4654130, 'lng': 108.2005275, 'dusun': 'DUSUN DEMUNG LANDUNG', 'nama_lengkap': 'RT 002 RW 001 DUSUN DEMUNG LANDUNG'},
    'RT 002 RW 007': {'lat': -7.4646261, 'lng': 108.2065185, 'dusun': 'DUSUN DEMUNG LANDUNG', 'nama_lengkap': 'RT 002 RW 007 DUSUN DEMUNG LANDUNG'},
    'RT 001 RW 007': {'lat': -7.4631743, 'lng': 108.2088620, 'dusun': 'DUSUN DEMUNG LANDUNG', 'nama_lengkap': 'RT 001 RW 007 DUSUN DEMUNG LANDUNG'},
    'RT 005 RW 001': {'lat': -7.4657286, 'lng': 108.2028884, 'dusun': 'DUSUN DEMUNG LANDUNG', 'nama_lengkap': 'RT 005 RW 001 DUSUN DEMUNG LANDUNG'},
    'RT 003 RW 008': {'lat': -7.4793564, 'lng': 108.2078790, 'dusun': 'DUSUN MARGAHAYU', 'nama_lengkap': 'RT 003 RW 008 DUSUN MARGAHAYU'},
    'RT 002 RW 008': {'lat': -7.4770852, 'lng': 108.2093253, 'dusun': 'DUSUN MARGAHAYU', 'nama_lengkap': 'RT 002 RW 008 DUSUN MARGAHAYU'},
    'RT 001 RW 008': {'lat': -7.4758422, 'lng': 108.2063846, 'dusun': 'DUSUN MARGAHAYU', 'nama_lengkap': 'RT 001 RW 008 DUSUN MARGAHAYU'},
    'RT 004 RW 001': {'lat': -7.4618315, 'lng': 108.2009951, 'dusun': 'DUSUN DEMUNG LANDUNG', 'nama_lengkap': 'RT 004 RW 001 DUSUN DEMUNG LANDUNG'},
    'RT 003 RW 001': {'lat': -7.4679330, 'lng': 108.2035854, 'dusun': 'DUSUN DEMUNG LANDUNG', 'nama_lengkap': 'RT 003 RW 001 DUSUN DEMUNG LANDUNG'},
    'RT 001 RW 001': {'lat': -7.4627341, 'lng': 108.2033712, 'dusun': 'DUSUN DEMUNG LANDUNG', 'nama_lengkap': 'RT 001 RW 001 DUSUN DEMUNG LANDUNG'},
    'RT 003 RW 004': {'lat': -7.4827780, 'lng': 108.2026430, 'dusun': 'DUSUN MARGAHAYU', 'nama_lengkap': 'RT 003 RW 004 DUSUN MARGAHAYU'},
    'RT 001 RW 004': {'lat': -7.4793031, 'lng': 108.2047908, 'dusun': 'DUSUN MARGAHAYU', 'nama_lengkap': 'RT 001 RW 004 DUSUN MARGAHAYU'},
    'RT 004 RW 005': {'lat': -7.4975062, 'lng': 108.2013711, 'dusun': 'DUSUN CIHAUR', 'nama_lengkap': 'RT 004 RW 005 DUSUN CIHAUR'},
}

def unduh_kml_dari_url(kml_url=DEFAULT_KML_URL):
    """Mengunduh file KML/KMZ dari URL Google Maps dan mengekstrak KML teksnya."""
    req = urllib.request.Request(
        kml_url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    with urllib.request.urlopen(req, timeout=15) as res:
        content = res.read()

    # Cek apakah file berupa KMZ (ZIP)
    if content[:2] == b'PK':
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            for fname in z.namelist():
                if fname.endswith('.kml'):
                    kml_text = z.read(fname).decode('utf-8', errors='ignore')
                    with open(LOCAL_KML_PATH, 'w', encoding='utf-8') as f:
                        f.write(kml_text)
                    return kml_text, 'KMZ diekstrak dan KML berhasil disimpan'
    else:
        kml_text = content.decode('utf-8', errors='ignore')
        with open(LOCAL_KML_PATH, 'w', encoding='utf-8') as f:
            f.write(kml_text)
        return kml_text, 'KML berhasil diunduh dan disimpan'

def baca_kml_poligon():
    """Membaca poligon dari desa_polygon.kml lokal atau mengunduh jika belum ada."""
    if not os.path.exists(LOCAL_KML_PATH):
        try:
            unduh_kml_dari_url()
        except Exception as e:
            print("Gagal unduh KML online:", e)

    if not os.path.exists(LOCAL_KML_PATH):
        return []

    tree = ET.parse(LOCAL_KML_PATH)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    polygons = []
    for pm in root.findall('.//kml:Placemark', ns):
        name_el = pm.find('kml:name', ns)
        name = name_el.text.strip() if name_el is not None else ''
        poly = pm.find('.//kml:Polygon', ns)
        if poly is not None:
            coords_el = poly.find('.//kml:coordinates', ns)
            if coords_el is not None and coords_el.text:
                coords = []
                for pt in coords_el.text.strip().split():
                    parts = pt.split(',')
                    if len(parts) >= 2:
                        lng = float(parts[0])
                        lat = float(parts[1])
                        coords.append([lng, lat])
                polygons.append({
                    'name': name,
                    'coordinates': coords
                })
    return polygons

def dapatkan_warna_kepadatan(total_penduduk):
    """Menentukan kode warna tematik choropleth berdasarkan jumlah penduduk per RT."""
    if total_penduduk >= 250:
        return '#7c2d12'  # Merah tua / Kepadatan Sangat Tinggi
    elif total_penduduk >= 200:
        return '#c2410c'  # Oranye tua / Kepadatan Tinggi
    elif total_penduduk >= 150:
        return '#d97706'  # Oranye-Kuning / Kepadatan Sedang
    elif total_penduduk >= 100:
        return '#059669'  # Hijau / Kepadatan Rendah-Sedang
    else:
        return '#0284c7'  # Biru / Kepadatan Rendah

def buat_geojson_sls_dengan_penduduk(tahun=2026):
    """
    Menggabungkan poligon KML dengan data demografi penduduk per RT (SLS) dari database
    menghasilkan FeatureCollection GeoJSON lengkap.
    """
    polygons = baca_kml_poligon()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, no_urut, nama_sls, nama_lengkap, dusun, laki_laki, perempuan, total, keluarga, latitude, longitude
        FROM statistik_sls 
        WHERE tahun = ?
        ORDER BY no_urut ASC, id ASC
    ''', (tahun,))
    sls_rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Indexing SLS dari database berdasarkan nama_sls (misal: "RT 001 RW 003")
    db_sls_map = {}
    for r in sls_rows:
        nama = r['nama_sls'].strip()
        db_sls_map[nama] = r

    features = []
    matched_names = set()

    for poly in polygons:
        raw_name = poly['name']
        coords = poly['coordinates']

        # Mencari SLS yang cocok dari awalan nama (misal "RT 001 RW 003 DUSUN RANCA SARI" -> "RT 001 RW 003")
        matched_sls = None
        for sls_key, sls_val in db_sls_map.items():
            if raw_name.startswith(sls_key):
                matched_sls = sls_val
                matched_names.add(sls_key)
                break

        # Fallback metadata koordinat & dusun
        meta = None
        for sls_key, m in RT_COORDINATES_MAP.items():
            if raw_name.startswith(sls_key):
                meta = m
                break

        total_jiwa = matched_sls['total'] if matched_sls else 0
        l_jiwa = matched_sls['laki_laki'] if matched_sls else 0
        p_jiwa = matched_sls['perempuan'] if matched_sls else 0
        kk = matched_sls['keluarga'] if matched_sls else 0
        no_urut = matched_sls['no_urut'] if matched_sls else 0

        center_lat = (matched_sls['latitude'] if matched_sls and matched_sls['latitude'] else (meta['lat'] if meta else None))
        center_lng = (matched_sls['longitude'] if matched_sls and matched_sls['longitude'] else (meta['lng'] if meta else None))
        dusun_nama = (matched_sls['dusun'] if matched_sls and matched_sls['dusun'] else (meta['dusun'] if meta else ''))
        sls_code = matched_sls['nama_sls'] if matched_sls else raw_name[:14]

        # Hitung centroid rata-rata dari koordinat jika belum ada
        if center_lat is None or center_lng is None:
            if coords:
                center_lat = sum(c[1] for c in coords) / len(coords)
                center_lng = sum(c[0] for c in coords) / len(coords)

        color = dapatkan_warna_kepadatan(total_jiwa)

        feature = {
            'type': 'Feature',
            'properties': {
                'id': matched_sls['id'] if matched_sls else None,
                'no_urut': no_urut,
                'nama': raw_name,
                'nama_sls': sls_code,
                'dusun': dusun_nama,
                'total_penduduk': total_jiwa,
                'laki_laki': l_jiwa,
                'perempuan': p_jiwa,
                'keluarga': kk,
                'lat': center_lat,
                'lng': center_lng,
                'color': color,
                'tahun': tahun
            },
            'geometry': {
                'type': 'Polygon',
                'coordinates': [coords]
            }
        }
        features.append(feature)

    # Simpan ke static/data/peta_sls.geojson
    geojson_data = {
        'type': 'FeatureCollection',
        'metadata': {
            'tahun': tahun,
            'total_sls': len(features),
            'kml_source': DEFAULT_KML_URL
        },
        'features': features
    }

    try:
        os.makedirs(os.path.dirname(GEOJSON_CACHE_PATH), exist_ok=True)
        with open(GEOJSON_CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, indent=2)
    except Exception as e:
        print("Gagal menyimpan cache GeoJSON:", e)

    return geojson_data
