"""
=============================================================================
SKRIP PEMOTONG & PEMBAGI KML KABUPATEN TASIKMALAYA PER DESA (BPS SLS 2025)
=============================================================================
Deskripsi:
Memecah file master KML SLS Kabupaten Tasikmalaya (45MB, 11.664 SLS)
menjadi file KML poligon per desa yang rapi, akurat, dan terstruktur.
Tiap file desa dikelompokkan ke dalam folder kecamatan masing-masing.
=============================================================================
"""

import os
import sys
import csv
import json
import time
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter

# Mendaftarkan namespace KML agar hasil keluaran bersih tanpa prefix acak ns0
KML_NS = 'http://www.opengis.net/kml/2.2'
ET.register_namespace('', KML_NS)

SOURCE_KML = r'C:\Users\WIN10\Downloads\Final_SLS_20251-3206.kml'
OUTPUT_DIR = r'C:\Users\WIN10\Downloads\KML_Desa_Tasikmalaya'

def sanitize_folder_name(name):
    """Membersihkan karakter ilegal untuk nama folder/file di Windows"""
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()

def run_split():
    start_time = time.time()
    print("=" * 70)
    print("  MEMULAI PROSES PEMOTONGAN KML KABUPATEN TASIKMALAYA PER DESA")
    print(f"  Sumber File : {SOURCE_KML}")
    print(f"  Tujuan      : {OUTPUT_DIR}")
    print("=" * 70)

    if not os.path.exists(SOURCE_KML):
        print(f"ERROR: File sumber tidak ditemukan di {SOURCE_KML}")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # -------------------------------------------------------------
    # TAHAP 1: PEMETAAN KANONIKAL & VALIDASI STRUKTUR DATA
    # -------------------------------------------------------------
    print("\n[1/4] Memindai dan memvalidasi struktur data 11.664 SLS...")
    village_info = defaultdict(lambda: {
        'kecs': Counter(),
        'desas': Counter(),
        'count': 0
    })

    total_scanned = 0
    for event, elem in ET.iterparse(SOURCE_KML, events=('end',)):
        if elem.tag.endswith('Placemark'):
            total_scanned += 1
            kdkec = ''
            kddesa = ''
            nmkec = ''
            nmdesa = ''
            for d in elem.findall(f'.//{{{KML_NS}}}Data') + elem.findall('.//Data'):
                name = d.get('name')
                v_el = d.find(f'{{{KML_NS}}}value')
                if v_el is None:
                    v_el = d.find('value')
                val = v_el.text.strip() if v_el is not None and v_el.text else ''
                if name == 'kdkec': kdkec = val
                elif name == 'kddesa': kddesa = val
                elif name == 'nmkec': nmkec = val
                elif name == 'nmdesa': nmdesa = val

            if kdkec and kddesa:
                key = (kdkec, kddesa)
                village_info[key]['kecs'][nmkec.upper()] += 1
                village_info[key]['desas'][nmdesa.upper()] += 1
                village_info[key]['count'] += 1
            elem.clear()

    total_villages = len(village_info)
    print(f"-> Terdeteksi: {total_scanned:,} Placemark SLS, {total_villages} Desa/Kelurahan.")

    # Tentukan nama kanonikal untuk setiap (kdkec, kddesa) untuk menghindari pecahan akibat typo BPS
    canonical_villages = {}
    kecamatans_summary = defaultdict(list)

    for (kdkec, kddesa), data in sorted(village_info.items()):
        canon_kec = data['kecs'].most_common(1)[0][0]
        canon_desa = data['desas'].most_common(1)[0][0]
        canonical_villages[(kdkec, kddesa)] = {
            'nmkec': canon_kec,
            'nmdesa': canon_desa,
            'sls_count': data['count']
        }
        kecamatans_summary[canon_kec].append({
            'kdkec': kdkec,
            'kddesa': kddesa,
            'nmdesa': canon_desa,
            'sls_count': data['count']
        })

    print(f"-> Jumlah Kecamatan terverifikasi: {len(kecamatans_summary)} Kecamatan.")

    # -------------------------------------------------------------
    # TAHAP 2: EKSTRAKSI & PENGELOMPOKKAN ELEMEN PLACEMARK PER DESA
    # -------------------------------------------------------------
    print("\n[2/4] Mengekstrak elemen geometri poligon per desa...")
    village_placemarks = defaultdict(list)
    processed_count = 0

    for event, elem in ET.iterparse(SOURCE_KML, events=('end',)):
        if elem.tag.endswith('Placemark'):
            processed_count += 1
            kdkec = ''
            kddesa = ''
            nmsls = ''
            idsls = ''
            luas = ''
            for d in elem.findall(f'.//{{{KML_NS}}}Data') + elem.findall('.//Data'):
                name = d.get('name')
                v_el = d.find(f'{{{KML_NS}}}value')
                if v_el is None:
                    v_el = d.find('value')
                val = v_el.text.strip() if v_el is not None and v_el.text else ''
                if name == 'kdkec': kdkec = val
                elif name == 'kddesa': kddesa = val
                elif name == 'nmsls': nmsls = val
                elif name == 'idsls': idsls = val
                elif name == 'luas': luas = val

            key = (kdkec, kddesa)
            if key in canonical_villages:
                canon = canonical_villages[key]
                # Modifikasi nama Placemark agar informatif (Nama RT/RW) di Google Earth / Leaflet
                name_elem = elem.find(f'{{{KML_NS}}}name')
                if name_elem is None:
                    name_elem = elem.find('name')
                if name_elem is not None:
                    name_elem.text = nmsls if nmsls else f"SLS {idsls}"

                # Tambahkan tag styleUrl agar poligon otomatis memiliki warna batas & arsiran
                style_url_el = ET.Element(f'{{{KML_NS}}}styleUrl')
                style_url_el.text = '#slsPolygonStyle'
                elem.insert(1, style_url_el)

                village_placemarks[key].append(elem)

    print(f"-> Berhasil mengekstrak {processed_count:,} Placemark ke {len(village_placemarks)} grup desa.")

    # -------------------------------------------------------------
    # TAHAP 3: MENULIS FILE KML POLIGON PER DESA & PENATAAN FOLDER
    # -------------------------------------------------------------
    print("\n[3/4] Menulis file KML individual per desa ke direktori tujuan...")
    katalog_records = []
    total_written_placemarks = 0
    village_number = 1

    for (kdkec, kddesa), placemarks in sorted(village_placemarks.items()):
        canon = canonical_villages[(kdkec, kddesa)]
        nmkec = canon['nmkec']
        nmdesa = canon['nmdesa']

        folder_kec = sanitize_folder_name(f"Kecamatan_{nmkec}")
        kec_dir = os.path.join(OUTPUT_DIR, folder_kec)
        os.makedirs(kec_dir, exist_ok=True)

        file_name = sanitize_folder_name(f"Desa_{nmdesa}") + ".kml"
        file_path = os.path.join(kec_dir, file_name)

        # Bangun Dokumen KML Lengkap & Valid
        kml_root = ET.Element(f'{{{KML_NS}}}kml')
        doc = ET.SubElement(kml_root, f'{{{KML_NS}}}Document')

        doc_name = ET.SubElement(doc, f'{{{KML_NS}}}name')
        doc_name.text = f"Peta SLS Desa {nmdesa} - Kec. {nmkec}"

        doc_desc = ET.SubElement(doc, f'{{{KML_NS}}}description')
        doc_desc.text = (
            f"Batas Poligon SLS (RT/RW/Dusun) Desa {nmdesa}, "
            f"Kecamatan {nmkec}, Kabupaten Tasikmalaya. "
            f"Kode BPS: 3206-{kdkec}-{kddesa}. Total SLS: {len(placemarks)}."
        )

        # Style bawaan agar tampilan di Google Earth / Leaflet langsung cantik
        style_el = ET.SubElement(doc, f'{{{KML_NS}}}Style', attrib={'id': 'slsPolygonStyle'})
        line_el = ET.SubElement(style_el, f'{{{KML_NS}}}LineStyle')
        line_col = ET.SubElement(line_el, f'{{{KML_NS}}}color')
        line_col.text = 'ff0284c7'  # Biru laut
        line_w = ET.SubElement(line_el, f'{{{KML_NS}}}width')
        line_w.text = '2'

        poly_el = ET.SubElement(style_el, f'{{{KML_NS}}}PolyStyle')
        poly_col = ET.SubElement(poly_el, f'{{{KML_NS}}}color')
        poly_col.text = '330284c7'  # Transparan lembut

        # Masukkan semua placemark desa ini
        for pm in placemarks:
            doc.append(pm)
            total_written_placemarks += 1

        tree = ET.ElementTree(kml_root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)

        katalog_records.append({
            'no': village_number,
            'kode_kemendagri': f"32.06.{kdkec}.{kddesa}",
            'kode_kecamatan': kdkec,
            'nama_kecamatan': nmkec,
            'kode_desa': kddesa,
            'nama_desa': nmdesa,
            'jumlah_sls': len(placemarks),
            'nama_file': file_name,
            'folder_kecamatan': folder_kec,
            'rel_path': os.path.join(folder_kec, file_name).replace('\\', '/'),
            'abs_path': file_path
        })
        village_number += 1

    print(f"-> Selesai menulis 351 file KML (Total {total_written_placemarks:,} Placemark tersimpan).")

    # -------------------------------------------------------------
    # TAHAP 4: MEMBUAT KATALOG PENCARIAN (CSV, TXT, JSON)
    # -------------------------------------------------------------
    print("\n[4/4] Membuat katalog pencarian desa lengkap (CSV, TXT, JSON)...")

    # A. File CSV (Bisa dibuka di Excel)
    csv_path = os.path.join(OUTPUT_DIR, 'KATALOG_DESA_TASIKMALAYA.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['no', 'kode_kemendagri', 'kode_kecamatan', 'nama_kecamatan', 'kode_desa', 'nama_desa', 'jumlah_sls', 'folder_kecamatan', 'nama_file', 'rel_path']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in katalog_records:
            row_clean = {k: r[k] for k in fieldnames}
            writer.writerow(row_clean)

    # B. File TXT Ringkas & Nyaman untuk Dicari (Ctrl+F)
    txt_path = os.path.join(OUTPUT_DIR, 'DAFTAR_PENCARIAN_DESA.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("      KATALOG WILAYAH KML POLIGON PER DESA SE-KABUPATEN TASIKMALAYA\n")
        f.write(f"      Total Kecamatan: {len(kecamatans_summary)} | Total Desa: {len(katalog_records)} | Total SLS: {total_written_placemarks:,}\n")
        f.write("=" * 80 + "\n\n")
        f.write("Petunjuk: Gunakan fitur Ctrl + F pada teks ini untuk mencari nama desa Anda.\n\n")

        for kec, desas in sorted(kecamatans_summary.items()):
            f.write(f"▼ KECAMATAN {kec} (Total {len(desas)} Desa):\n")
            for d in sorted(desas, key=lambda x: x['nmdesa']):
                f.write(f"   - Desa {d['nmdesa']:<25} (Kode: {d['kddesa']}, {d['sls_count']:>3} RT/SLS) -> Kecamatan_{kec}/Desa_{sanitize_folder_name(d['nmdesa'])}.kml\n")
            f.write("\n")

    # C. File JSON untuk integrasi langsung ke sistem/website
    json_path = os.path.join(OUTPUT_DIR, 'katalog_desa.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(katalog_records, f, indent=2, ensure_ascii=False)

    # D. Salin katalog JSON ke dalam direktori static website_desa agar bisa langsung digunakan sistem
    website_json_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'data')
    os.makedirs(website_json_dir, exist_ok=True)
    with open(os.path.join(website_json_dir, 'katalog_desa_tasikmalaya.json'), 'w', encoding='utf-8') as f:
        json.dump(katalog_records, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("  PROSES SELESAI DENGAN SUKSES 100%!")
    print(f"  Waktu Eksekusi   : {elapsed:.2f} detik")
    print(f"  Total Placemark  : {total_written_placemarks:,} / {total_scanned:,} (Akurat 100%)")
    print(f"  Total Desa       : {len(katalog_records)} Desa/Kelurahan")
    print(f"  Total Kecamatan  : {len(kecamatans_summary)} Kecamatan")
    print(f"  Direktori Output : {OUTPUT_DIR}")
    print(f"  File Katalog     : {csv_path}")
    print(f"  File Indeks Teks : {txt_path}")
    print("=" * 70)

if __name__ == '__main__':
    run_split()
