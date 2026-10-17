import io
import csv
import re
import json
import openpyxl
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Seed data 26 RT dari gambar user
SAMPLE_SLS_DATA = [
    (1, "RT 001 RW 001", 88, 97, 63),
    (2, "RT 002 RW 001", 121, 116, 81),
    (3, "RT 003 RW 001", 125, 119, 92),
    (4, "RT 004 RW 001", 96, 101, 67),
    (5, "RT 005 RW 001", 69, 52, 42),
    (6, "RT 001 RW 002", 61, 54, 46),
    (7, "RT 002 RW 002", 75, 73, 51),
    (8, "RT 003 RW 002", 73, 74, 54),
    (9, "RT 004 RW 002", 87, 68, 62),
    (10, "RT 001 RW 003", 147, 135, 94),
    (11, "RT 002 RW 003", 115, 114, 80),
    (12, "RT 001 RW 004", 116, 116, 92),
    (13, "RT 002 RW 004", 89, 100, 70),
    (14, "RT 003 RW 004", 115, 101, 85),
    (15, "RT 001 RW 005", 115, 125, 84),
    (16, "RT 002 RW 005", 101, 83, 69),
    (17, "RT 003 RW 005", 111, 114, 78),
    (18, "RT 004 RW 005", 139, 114, 85),
    (19, "RT 001 RW 006", 74, 78, 54),
    (20, "RT 002 RW 006", 72, 67, 52),
    (21, "RT 003 RW 006", 45, 47, 34),
    (22, "RT 001 RW 007", 96, 102, 67),
    (23, "RT 002 RW 007", 97, 94, 69),
    (24, "RT 001 RW 008", 96, 81, 59),
    (25, "RT 002 RW 008", 86, 85, 57),
    (26, "RT 003 RW 008", 95, 84, 61),
]

# Seed data 16 Kelompok Umur (Piramida Penduduk) dari gambar user
SAMPLE_UMUR_DATA = [
    (1, "0 - 4", 121, 138),
    (2, "5 - 9", 165, 137),
    (3, "10 - 14", 191, 166),
    (4, "15 - 19", 188, 198),
    (5, "20 - 24", 204, 162),
    (6, "25 - 29", 215, 173),
    (7, "30 - 34", 162, 183),
    (8, "35 - 39", 153, 123),
    (9, "40 - 44", 143, 150),
    (10, "45 - 49", 149, 180),
    (11, "50 - 54", 192, 166),
    (12, "54 - 59", 163, 180),
    (13, "60 - 64", 174, 143),
    (14, "65 - 69", 121, 120),
    (15, "70 - 74", 66, 81),
    (16, "75+", 97, 94),
]

def get_excel_styles():
    header_fill = PatternFill(start_color='E67E22', end_color='E67E22', fill_type='solid') # Oranye seperti gambar
    header_font = Font(name='Calibri', size=11, bold=True, color='000000')
    
    total_fill = PatternFill(start_color='F39C12', end_color='F39C12', fill_type='solid') # Oranye terang TOTAL
    total_font = Font(name='Calibri', size=11, bold=True, color='000000')
    
    data_font = Font(name='Calibri', size=11, bold=False, color='1E293B')
    
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )
    return header_fill, header_font, total_fill, total_font, data_font, thin_border


def generate_template_excel(include_sample=True):
    """Membuat file Excel (.xlsx) template unggah statistik kependudukan SLS"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Statistik SLS"
    ws.views.sheetView[0].showGridLines = True

    header_fill, header_font, total_fill, total_font, data_font, thin_border = get_excel_styles()
    headers = ["No.", "Nama SLS", "Laki - Laki", "Perempuan", "Total", "Keluarga"]
    ws.append(headers)

    ws.row_dimensions[1].height = 26
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    rows_to_insert = SAMPLE_SLS_DATA if include_sample else []
    
    current_row = 2
    if rows_to_insert:
        for item in rows_to_insert:
            no, nama, laki, perempuan, keluarga = item
            ws.append([no, nama, laki, perempuan, f"=C{current_row}+D{current_row}", keluarga])
            
            ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
            ws.cell(row=current_row, column=3).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=4).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=5).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=6).alignment = Alignment(horizontal='center', vertical='center')

            for col in range(1, 7):
                c = ws.cell(row=current_row, column=col)
                c.font = data_font
                c.border = thin_border
            current_row += 1
    else:
        # 5 baris kosong siap isi
        for i in range(1, 6):
            ws.append([i, f"RT 00{i} RW 001", "", "", f"=C{current_row}+D{current_row}", ""])
            for col in range(1, 7):
                c = ws.cell(row=current_row, column=col)
                c.font = data_font
                c.border = thin_border
                c.alignment = Alignment(horizontal='center' if col != 2 else 'left', vertical='center')
            current_row += 1

    # Baris TOTAL (persis seperti gambar)
    total_row = current_row
    ws.row_dimensions[total_row].height = 24
    ws.append(["T O T A L", "", f"=SUM(C2:C{total_row-1})", f"=SUM(D2:D{total_row-1})", f"=SUM(E2:E{total_row-1})", f"=SUM(F2:F{total_row-1})"])
    
    for col_idx in range(1, 7):
        cell = ws.cell(row=total_row, column=col_idx)
        cell.fill = total_fill
        cell.font = total_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    # Lebar kolom
    col_widths = {1: 8, 2: 24, 3: 16, 4: 16, 5: 16, 6: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def generate_template_csv(include_sample=True):
    """Membuat file CSV template unggah statistik SLS"""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["No.", "Nama SLS", "Laki - Laki", "Perempuan", "Total", "Keluarga"])

    if include_sample:
        for item in SAMPLE_SLS_DATA:
            no, nama, laki, perempuan, keluarga = item
            writer.writerow([no, nama, laki, perempuan, laki + perempuan, keluarga])
        # Summary row
        tot_laki = sum(x[2] for x in SAMPLE_SLS_DATA)
        tot_p = sum(x[3] for x in SAMPLE_SLS_DATA)
        tot_jiwa = tot_laki + tot_p
        tot_kk = sum(x[4] for x in SAMPLE_SLS_DATA)
        writer.writerow(["TOTAL", "", tot_laki, tot_p, tot_jiwa, tot_kk])
    else:
        for i in range(1, 6):
            writer.writerow([i, f"RT 00{i} RW 001", "", "", "", ""])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def export_sls_excel(sls_rows, tahun):
    """Mengekspor data SLS tahun berjalan ke file Excel (.xlsx) dengan styling rapi"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Statistik SLS {tahun}"
    ws.views.sheetView[0].showGridLines = True

    header_fill, header_font, total_fill, total_font, data_font, thin_border = get_excel_styles()
    headers = ["No.", "Nama SLS", "Laki - Laki", "Perempuan", "Total", "Keluarga"]
    ws.append(headers)

    ws.row_dimensions[1].height = 26
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    current_row = 2
    for r in sls_rows:
        no = r.get('no_urut') or (current_row - 1)
        nama = r.get('nama_sls', '')
        laki = r.get('laki_laki', 0)
        perempuan = r.get('perempuan', 0)
        total = r.get('total') or (laki + perempuan)
        keluarga = r.get('keluarga', 0)

        ws.append([no, nama, laki, perempuan, total, keluarga])
        ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
        for c in range(3, 7):
            ws.cell(row=current_row, column=c).alignment = Alignment(horizontal='center', vertical='center')
        for c in range(1, 7):
            cell = ws.cell(row=current_row, column=c)
            cell.font = data_font
            cell.border = thin_border
        current_row += 1

    total_row = current_row
    ws.row_dimensions[total_row].height = 24
    if len(sls_rows) > 0:
        ws.append(["T O T A L", "", f"=SUM(C2:C{total_row-1})", f"=SUM(D2:D{total_row-1})", f"=SUM(E2:E{total_row-1})", f"=SUM(F2:F{total_row-1})"])
    else:
        ws.append(["T O T A L", "", 0, 0, 0, 0])

    for col_idx in range(1, 7):
        cell = ws.cell(row=total_row, column=col_idx)
        cell.fill = total_fill
        cell.font = total_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    col_widths = {1: 8, 2: 24, 3: 16, 4: 16, 5: 16, 6: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def parse_uploaded_sls_file(file_storage):
    """
    Membaca dan mem-parse file Excel (.xlsx/.xls) atau CSV (.csv) yang diunggah.
    Mendukung objek Werkzeug FileStorage maupun file-like / BytesIO stream.
    Mengembalikan: (data_list, error_msg)
    """
    filename = getattr(file_storage, 'filename', '') or getattr(file_storage, 'name', '') or ''
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    stream = getattr(file_storage, 'stream', file_storage)
    try:
        stream.seek(0)
    except Exception:
        pass

    rows_data = []

    try:
        if ext in ['xlsx', 'xlsm', 'xltx', 'xltm']:
            wb = openpyxl.load_workbook(stream, data_only=True)
            ws = wb.active
            rows_data = list(ws.iter_rows(values_only=True))
        elif ext == 'csv':
            content = stream.read()
            # Coba decode utf-8-sig atau latin-1
            text = ""
            for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
                try:
                    text = content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if not text:
                return None, "File CSV tidak dapat dibaca karena format enkoding tidak didukung."
            
            # Deteksi delimiter (koma atau titik koma)
            sample_line = text.splitlines()[0] if text.splitlines() else ""
            delimiter = ';' if ';' in sample_line and ',' not in sample_line else ','
            reader = csv.reader(io.StringIO(text), delimiter=delimiter)
            rows_data = list(reader)
        else:
            return None, "Format file tidak didukung. Harap unggah file .xlsx atau .csv."
    except Exception as e:
        return None, f"Gagal membaca file: {str(e)}"

    if not rows_data:
        return None, "File yang diunggah kosong."

    # Cari baris Header
    header_idx = -1
    col_map = {}

    for r_idx, row in enumerate(rows_data):
        cells = [str(c or '').strip().lower() for c in row]
        has_sls = any(any(k in c for k in ['sls', 'rt', 'rw', 'dusun', 'wilayah', 'nama']) for c in cells)
        has_gender = any(any(k in c for k in ['laki', 'pria', 'perempuan', 'wanita', 'erempua']) for c in cells)

        if has_sls and has_gender:
            header_idx = r_idx
            for c_idx, val in enumerate(cells):
                if any(k in val for k in ['no', 'nomor', 'urut']):
                    col_map['no'] = c_idx
                elif any(k in val for k in ['sls', 'wilayah', 'nama', 'rt', 'rw', 'dusun']) and 'no' not in val:
                    col_map['nama_sls'] = c_idx
                elif any(k in val for k in ['laki', 'pria', 'lk']):
                    col_map['laki_laki'] = c_idx
                elif any(k in val for k in ['perempuan', 'wanita', 'pr', 'erempua']):
                    col_map['perempuan'] = c_idx
                elif any(k in val for k in ['total', 'jumlah', 'jiwa']):
                    col_map['total'] = c_idx
                elif any(k in val for k in ['keluarga', 'kk']):
                    col_map['keluarga'] = c_idx
            break

    if header_idx == -1:
        # Fallback jika header tidak terdeteksi nama kolomnya secara otomatis
        # Asumsikan urutan standar: No, Nama SLS, Laki-laki, Perempuan, Total, Keluarga
        col_map = {'no': 0, 'nama_sls': 1, 'laki_laki': 2, 'perempuan': 3, 'total': 4, 'keluarga': 5}
        header_idx = 0

    parsed_records = []
    for r_idx, row in enumerate(rows_data[header_idx + 1:], start=header_idx + 2):
        if not row or not any(row):
            continue

        sls_idx = col_map.get('nama_sls', 1)
        sls_name = str(row[sls_idx] or '').strip() if sls_idx < len(row) else ''

        if not sls_name:
            continue

        clean_sls_upper = sls_name.replace(" ", "").upper()
        if clean_sls_upper.startswith("TOTAL") or clean_sls_upper.startswith("JUMLAH"):
            continue

        # No urut
        no_idx = col_map.get('no', 0)
        try:
            no_val = int(float(str(row[no_idx] or 0))) if no_idx < len(row) else len(parsed_records) + 1
        except:
            no_val = len(parsed_records) + 1

        # Laki-laki
        l_idx = col_map.get('laki_laki', 2)
        try:
            laki = int(float(str(row[l_idx] or 0))) if l_idx < len(row) else 0
        except:
            laki = 0

        # Perempuan
        p_idx = col_map.get('perempuan', 3)
        try:
            perempuan = int(float(str(row[p_idx] or 0))) if p_idx < len(row) else 0
        except:
            perempuan = 0

        # Total
        tot_idx = col_map.get('total', 4)
        try:
            total = int(float(str(row[tot_idx] or 0))) if tot_idx < len(row) else (laki + perempuan)
        except:
            total = laki + perempuan
        if total == 0 and (laki + perempuan) > 0:
            total = laki + perempuan

        # Keluarga
        kk_idx = col_map.get('keluarga', 5)
        try:
            keluarga = int(float(str(row[kk_idx] or 0))) if kk_idx < len(row) else 0
        except:
            keluarga = 0

        parsed_records.append({
            'no_urut': no_val,
            'nama_sls': sls_name,
            'laki_laki': max(0, laki),
            'perempuan': max(0, perempuan),
            'total': max(0, total),
            'keluarga': max(0, keluarga)
        })

    if not parsed_records:
        return None, "Tidak ada baris data SLS valid yang berhasil diproses dari file."

    return parsed_records, None


def sync_aggregate_statistics(conn, tahun):
    """
    Menghitung ulang total dari tabel statistik_sls untuk tahun tertentu,
    dan menyinkronkan angkanya ke tabel statistik utama.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*),
            COALESCE(SUM(laki_laki), 0),
            COALESCE(SUM(perempuan), 0),
            COALESCE(SUM(total), 0),
            COALESCE(SUM(keluarga), 0)
        FROM statistik_sls
        WHERE tahun = ?
    """, (tahun,))
    row = cursor.fetchone()
    count_sls, sum_laki, sum_perempuan, sum_total, sum_kk = row
    if sum_total == 0 and (sum_laki + sum_perempuan) > 0:
        sum_total = sum_laki + sum_perempuan

    # Update atau insert ke tabel statistik
    cursor.execute("SELECT id FROM statistik WHERE tahun = ?", (tahun,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("""
            UPDATE statistik SET 
                total_penduduk = ?,
                laki_laki = ?,
                perempuan = ?,
                kepala_keluarga = ?
            WHERE id = ?
        """, (sum_total, sum_laki, sum_perempuan, sum_kk, existing[0]))
    else:
        cursor.execute("""
            INSERT INTO statistik (tahun, total_penduduk, laki_laki, perempuan, kepala_keluarga, penduduk_sementara, mutasi_penduduk)
            VALUES (?, ?, ?, ?, ?, 0, 0)
        """, (tahun, sum_total, sum_laki, sum_perempuan, sum_kk))

    # Pastikan row id=1 selalu mencerminkan data tahun berjalan terbaru
    cursor.execute("SELECT MAX(tahun) FROM statistik_sls")
    max_year = cursor.fetchone()[0] or 2026
    if tahun == max_year:
        cursor.execute("""
            UPDATE statistik SET 
                tahun = ?,
                total_penduduk = ?,
                laki_laki = ?,
                perempuan = ?,
                kepala_keluarga = ?
            WHERE id = 1
        """, (tahun, sum_total, sum_laki, sum_perempuan, sum_kk))

    conn.commit()
    return count_sls, sum_laki, sum_perempuan, sum_total, sum_kk


# ==============================================================================
# HELPER DATA KELOMPOK UMUR & PIRAMIDA PENDUDUK
# ==============================================================================

def generate_template_umur_excel(include_sample=True):
    """Membuat file Excel (.xlsx) template unggah data kelompok umur untuk piramida penduduk"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Kelompok Umur"
    ws.views.sheetView[0].showGridLines = True

    header_fill, header_font, total_fill, total_font, data_font, thin_border = get_excel_styles()
    headers = ["No.", "Kelompok Umur", "Laki-laki", "Perempuan", "Total"]
    ws.append(headers)

    ws.row_dimensions[1].height = 26
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    rows_to_insert = SAMPLE_UMUR_DATA if include_sample else []

    current_row = 2
    if rows_to_insert:
        for item in rows_to_insert:
            no, umur, laki, perempuan = item
            ws.append([no, umur, laki, perempuan, f"=C{current_row}+D{current_row}"])
            ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=3).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=4).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=5).alignment = Alignment(horizontal='center', vertical='center')

            for col in range(1, 6):
                c = ws.cell(row=current_row, column=col)
                c.font = data_font
                c.border = thin_border
            current_row += 1
    else:
        standar_umur = ["0 - 4", "5 - 9", "10 - 14", "15 - 19", "20 - 24", "25 - 29", "30 - 34", "35 - 39", "40 - 44", "45 - 49", "50 - 54", "54 - 59", "60 - 64", "65 - 69", "70 - 74", "75+"]
        for idx, u in enumerate(standar_umur, 1):
            ws.append([idx, u, "", "", f"=C{current_row}+D{current_row}"])
            for col in range(1, 6):
                c = ws.cell(row=current_row, column=col)
                c.font = data_font
                c.border = thin_border
                c.alignment = Alignment(horizontal='center', vertical='center')
            current_row += 1

    # Baris TOTAL
    total_row = current_row
    ws.row_dimensions[total_row].height = 24
    ws.append(["T O T A L", "", f"=SUM(C2:C{total_row-1})", f"=SUM(D2:D{total_row-1})", f"=SUM(E2:E{total_row-1})"])

    for col_idx in range(1, 6):
        cell = ws.cell(row=total_row, column=col_idx)
        cell.fill = total_fill
        cell.font = total_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    col_widths = {1: 8, 2: 20, 3: 16, 4: 16, 5: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def generate_template_umur_csv(include_sample=True):
    """Membuat file CSV template unggah data kelompok umur"""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["No.", "Kelompok Umur", "Laki-laki", "Perempuan", "Total"])

    if include_sample:
        for item in SAMPLE_UMUR_DATA:
            no, umur, laki, perempuan = item
            writer.writerow([no, umur, laki, perempuan, laki + perempuan])
        tot_laki = sum(x[2] for x in SAMPLE_UMUR_DATA)
        tot_p = sum(x[3] for x in SAMPLE_UMUR_DATA)
        writer.writerow(["TOTAL", "", tot_laki, tot_p, tot_laki + tot_p])
    else:
        standar_umur = ["0 - 4", "5 - 9", "10 - 14", "15 - 19", "20 - 24", "25 - 29", "30 - 34", "35 - 39", "40 - 44", "45 - 49", "50 - 54", "54 - 59", "60 - 64", "65 - 69", "70 - 74", "75+"]
        for idx, u in enumerate(standar_umur, 1):
            writer.writerow([idx, u, "", "", ""])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def export_umur_excel(umur_rows, tahun):
    """Mengekspor data kelompok umur tahun berjalan ke Excel (.xlsx)"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Kelompok Umur {tahun}"
    ws.views.sheetView[0].showGridLines = True

    header_fill, header_font, total_fill, total_font, data_font, thin_border = get_excel_styles()
    headers = ["No.", "Kelompok Umur", "Laki-laki", "Perempuan", "Total"]
    ws.append(headers)

    ws.row_dimensions[1].height = 26
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    current_row = 2
    for r in umur_rows:
        no = r.get('no_urut') or (current_row - 1)
        umur = r.get('kelompok_umur', '')
        laki = r.get('laki_laki', 0)
        perempuan = r.get('perempuan', 0)
        total = r.get('total') or (laki + perempuan)

        ws.append([no, umur, laki, perempuan, total])
        for c in range(1, 6):
            cell = ws.cell(row=current_row, column=c)
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.font = data_font
            cell.border = thin_border
        current_row += 1

    total_row = current_row
    ws.row_dimensions[total_row].height = 24
    if len(umur_rows) > 0:
        ws.append(["T O T A L", "", f"=SUM(C2:C{total_row-1})", f"=SUM(D2:D{total_row-1})", f"=SUM(E2:E{total_row-1})"])
    else:
        ws.append(["T O T A L", "", 0, 0, 0])

    for col_idx in range(1, 6):
        cell = ws.cell(row=total_row, column=col_idx)
        cell.fill = total_fill
        cell.font = total_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    col_widths = {1: 8, 2: 20, 3: 16, 4: 16, 5: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def parse_uploaded_umur_file(file_storage):
    """
    Membaca dan mem-parse file Excel (.xlsx/.xls) atau CSV (.csv) data kelompok umur.
    Mengembalikan: (data_list, error_msg)
    """
    filename = getattr(file_storage, 'filename', '') or getattr(file_storage, 'name', '') or ''
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    stream = getattr(file_storage, 'stream', file_storage)
    try:
        stream.seek(0)
    except Exception:
        pass

    rows_data = []

    try:
        if ext in ['xlsx', 'xlsm', 'xltx', 'xltm']:
            wb = openpyxl.load_workbook(stream, data_only=True)
            ws = wb.active
            rows_data = list(ws.iter_rows(values_only=True))
        elif ext == 'csv':
            content = stream.read()
            text = ""
            for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
                try:
                    text = content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if not text:
                return None, "File CSV tidak dapat dibaca karena format enkoding tidak didukung."

            sample_line = text.splitlines()[0] if text.splitlines() else ""
            delimiter = ';' if ';' in sample_line and ',' not in sample_line else ','
            reader = csv.reader(io.StringIO(text), delimiter=delimiter)
            rows_data = list(reader)
        else:
            return None, "Format file tidak didukung. Harap unggah file .xlsx atau .csv."
    except Exception as e:
        return None, f"Gagal membaca file: {str(e)}"

    if not rows_data:
        return None, "File yang diunggah kosong."

    # Deteksi baris header
    header_idx = -1
    col_map = {}

    for r_idx, row in enumerate(rows_data):
        cells = [str(c or '').strip().lower() for c in row]
        has_age = any(any(k in c for k in ['umur', 'usia', 'kelompok', 'rentang']) for c in cells)
        has_gender = any(any(k in c for k in ['laki', 'pria', 'perempuan', 'wanita']) for c in cells)

        if has_age and has_gender:
            header_idx = r_idx
            for c_idx, val in enumerate(cells):
                if any(k in val for k in ['no', 'nomor', 'urut']):
                    col_map['no'] = c_idx
                elif any(k in val for k in ['umur', 'usia', 'kelompok', 'rentang']):
                    col_map['kelompok_umur'] = c_idx
                elif any(k in val for k in ['laki', 'pria', 'lk']):
                    col_map['laki_laki'] = c_idx
                elif any(k in val for k in ['perempuan', 'wanita', 'pr', 'erempua']):
                    col_map['perempuan'] = c_idx
                elif any(k in val for k in ['total', 'jumlah']):
                    col_map['total'] = c_idx
            break

    if header_idx == -1:
        col_map = {'no': 0, 'kelompok_umur': 1, 'laki_laki': 2, 'perempuan': 3, 'total': 4}
        header_idx = 0

    parsed_records = []
    for r_idx, row in enumerate(rows_data[header_idx + 1:], start=header_idx + 2):
        if not row or not any(row):
            continue

        umur_idx = col_map.get('kelompok_umur', 1)
        umur_str = str(row[umur_idx] or '').strip() if umur_idx < len(row) else ''

        if not umur_str:
            continue

        clean_upper = umur_str.replace(" ", "").upper()
        if clean_upper.startswith("TOTAL") or clean_upper.startswith("JUMLAH"):
            continue

        no_idx = col_map.get('no', 0)
        try:
            no_val = int(float(str(row[no_idx] or 0))) if no_idx < len(row) else len(parsed_records) + 1
        except:
            no_val = len(parsed_records) + 1

        l_idx = col_map.get('laki_laki', 2)
        try:
            laki = int(float(str(row[l_idx] or 0))) if l_idx < len(row) else 0
        except:
            laki = 0

        p_idx = col_map.get('perempuan', 3)
        try:
            perempuan = int(float(str(row[p_idx] or 0))) if p_idx < len(row) else 0
        except:
            perempuan = 0

        tot_idx = col_map.get('total', 4)
        try:
            total = int(float(str(row[tot_idx] or 0))) if tot_idx < len(row) else (laki + perempuan)
        except:
            total = laki + perempuan
        if total == 0 and (laki + perempuan) > 0:
            total = laki + perempuan

        parsed_records.append({
            'no_urut': no_val,
            'kelompok_umur': umur_str,
            'laki_laki': max(0, laki),
            'perempuan': max(0, perempuan),
            'total': max(0, total)
        })

    if not parsed_records:
        return None, "Tidak ada data baris kelompok umur valid yang berhasil diproses."

    return parsed_records, None


def sync_aggregate_umur(conn, tahun):
    """
    Menghitung ulang data kelompok umur dan menyinkronkannya ke kolom data_usia_json
    di tabel statistik untuk kompatibilitas tampilan.
    """
    import json
    cursor = conn.cursor()
    cursor.execute("SELECT kelompok_umur, laki_laki, perempuan, total FROM statistik_umur WHERE tahun = ? ORDER BY no_urut ASC, id ASC", (tahun,))
    rows = cursor.fetchall()
    if not rows:
        return 0, 0, 0, 0

    tot_laki = sum(r[1] for r in rows)
    tot_puan = sum(r[2] for r in rows)
    tot_jiwa = sum(r[3] for r in rows)

    # Petakan ke 5 kategori ringkas untuk chart bar sampingan
    # 0-14 (anak): 0-4, 5-9, 10-14
    anak = sum(r[3] for r in rows if any(k in r[0] for k in ['0 - 4', '5 - 9', '10 - 14']))
    # 15-24 (pemuda): 15-19, 20-24
    pemuda = sum(r[3] for r in rows if any(k in r[0] for k in ['15 - 19', '20 - 24']))
    # 25-45/49 (dewasa): 25-29, 30-34, 35-39, 40-44, 45-49
    dewasa = sum(r[3] for r in rows if any(k in r[0] for k in ['25 - 29', '30 - 34', '35 - 39', '40 - 44', '45 - 49']))
    # 50-64 (lansia awal): 50-54, 54-59, 55-59, 60-64
    lansia_awal = sum(r[3] for r in rows if any(k in r[0] for k in ['50 - 54', '54 - 59', '55 - 59', '60 - 64']))
    # 65+ (lansia): 65-69, 70-74, 75+
    lansia = sum(r[3] for r in rows if any(k in r[0] for k in ['65 - 69', '70 - 74', '75+']))

    usia_json = [
        {"label": "0 - 14 Th (Anak)", "jumlah": anak},
        {"label": "15 - 24 Th (Pemuda)", "jumlah": pemuda},
        {"label": "25 - 49 Th (Dewasa)", "jumlah": dewasa},
        {"label": "50 - 64 Th (Pra-Lansia)", "jumlah": lansia_awal},
        {"label": "> 65 Th (Lansia)", "jumlah": lansia}
    ]

    cursor.execute("""
        UPDATE statistik SET 
            data_usia_json = ?
        WHERE tahun = ? OR id = 1
    """, (json.dumps(usia_json), tahun))
    conn.commit()

    return len(rows), tot_laki, tot_puan, tot_jiwa


# =========================================================================
# HELPER DATA TINGKAT PENDIDIKAN PENDUDUK PER SLS (RT/RW)
# =========================================================================

PENDIDIKAN_COLUMNS = [
    ('tidak_sekolah', 'Tidak Memiliki Ijazah SD'),
    ('sd', 'SD'),
    ('mi', 'MI'),
    ('paket_a', 'PAKET A'),
    ('sdlb', 'SDLB'),
    ('spm_ula', 'SPM/PDF/Ula'),
    ('smp', 'SMP'),
    ('mts', 'MTs'),
    ('smp_lb', 'SMP LB'),
    ('paket_b', 'PAKET B'),
    ('spm_wustha', 'SPM/PDF Wustha'),
    ('sma', 'SMA'),
    ('smk', 'SMK'),
    ('ma', 'MA'),
    ('mak', 'MAK'),
    ('sma_lb', 'SMA LB'),
    ('paket_c', 'PAKET C'),
    ('spm_ulya', 'SPM/PDF Ulya'),
    ('diploma', 'DI/DII/DIII'),
    ('s1', 'DIV/S1'),
    ('profesi', 'Profesi'),
    ('s2', 'S2'),
    ('s3', 'S3'),
]

SAMPLE_PENDIDIKAN_DATA = [
    (1, 'RT 001 RW 001', 17, 62, 0, 0, 0, 0, 23, 2, 0, 0, 0, 44, 4, 0, 0, 0, 0, 0, 1, 17, 0, 0, 0, 170),
    (2, 'RT 002 RW 001', 24, 52, 0, 0, 0, 0, 30, 1, 0, 2, 0, 59, 11, 1, 0, 0, 1, 0, 3, 27, 0, 0, 0, 211),
    (3, 'RT 003 RW 001', 14, 67, 0, 0, 0, 0, 34, 0, 0, 0, 0, 61, 7, 0, 0, 0, 3, 0, 4, 26, 0, 1, 0, 217),
    (4, 'RT 004 RW 001', 16, 92, 0, 0, 0, 0, 43, 0, 0, 0, 0, 24, 0, 0, 0, 0, 0, 0, 1, 4, 0, 1, 0, 181),
    (5, 'RT 005 RW 001', 10, 33, 0, 0, 0, 0, 19, 0, 0, 0, 0, 34, 3, 0, 0, 0, 1, 0, 1, 4, 0, 0, 0, 105),
    (6, 'RT 001 RW 002', 11, 50, 0, 0, 0, 0, 21, 0, 0, 0, 0, 15, 4, 1, 0, 0, 1, 0, 0, 6, 0, 2, 0, 111),
    (7, 'RT 002 RW 002', 34, 45, 0, 0, 0, 0, 37, 0, 0, 0, 0, 17, 5, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0, 142),
    (8, 'RT 003 RW 002', 40, 28, 0, 0, 0, 0, 39, 0, 0, 0, 0, 8, 6, 0, 0, 0, 1, 0, 3, 2, 0, 1, 0, 128),
    (9, 'RT 004 RW 002', 30, 51, 0, 0, 0, 0, 27, 0, 0, 0, 0, 25, 5, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0, 142),
    (10, 'RT 001 RW 003', 92, 38, 0, 0, 0, 0, 56, 0, 0, 1, 0, 51, 12, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 253),
    (11, 'RT 002 RW 003', 62, 29, 0, 0, 0, 0, 51, 0, 0, 0, 0, 38, 13, 0, 0, 0, 0, 0, 2, 6, 0, 0, 0, 201),
    (12, 'RT 001 RW 004', 13, 121, 0, 0, 0, 0, 37, 0, 0, 0, 0, 29, 11, 0, 0, 0, 0, 0, 1, 10, 0, 0, 0, 222),
    (13, 'RT 002 RW 004', 18, 78, 0, 0, 0, 0, 20, 0, 0, 0, 0, 30, 18, 3, 0, 0, 0, 0, 2, 11, 0, 1, 0, 181),
    (14, 'RT 003 RW 004', 16, 93, 0, 0, 0, 0, 25, 0, 0, 0, 0, 32, 8, 3, 0, 0, 0, 0, 5, 14, 0, 3, 0, 199),
    (15, 'RT 001 RW 005', 55, 71, 1, 0, 0, 0, 32, 3, 0, 0, 0, 24, 16, 1, 0, 0, 0, 0, 4, 15, 0, 0, 0, 222),
    (16, 'RT 002 RW 005', 34, 54, 0, 0, 0, 0, 30, 3, 0, 0, 0, 23, 15, 1, 0, 0, 0, 0, 0, 11, 0, 0, 0, 171),
    (17, 'RT 003 RW 005', 24, 110, 0, 0, 0, 0, 33, 0, 0, 0, 0, 23, 13, 1, 0, 0, 0, 0, 0, 3, 0, 0, 0, 207),
    (18, 'RT 004 RW 005', 34, 97, 0, 0, 0, 0, 44, 0, 0, 0, 0, 37, 14, 1, 0, 0, 0, 0, 2, 6, 0, 0, 0, 235),
    (19, 'RT 001 RW 006', 15, 77, 0, 0, 0, 0, 22, 2, 0, 0, 0, 18, 5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 140),
    (20, 'RT 002 RW 006', 17, 67, 0, 0, 0, 0, 24, 2, 0, 0, 0, 11, 3, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 132),
    (21, 'RT 003 RW 006', 9, 47, 0, 0, 0, 0, 11, 2, 0, 0, 0, 6, 4, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 83),
    (22, 'RT 001 RW 007', 15, 94, 0, 0, 0, 0, 50, 0, 0, 0, 0, 19, 3, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 183),
    (23, 'RT 002 RW 007', 23, 82, 0, 0, 0, 0, 39, 0, 0, 0, 0, 24, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 171),
    (24, 'RT 001 RW 008', 27, 80, 0, 0, 0, 0, 37, 0, 0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 1, 3, 0, 0, 0, 160),
    (25, 'RT 002 RW 008', 23, 67, 0, 0, 0, 0, 34, 0, 0, 0, 0, 24, 4, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 154),
    (26, 'RT 003 RW 008', 19, 82, 0, 0, 0, 0, 36, 0, 0, 0, 0, 17, 4, 0, 0, 0, 0, 0, 1, 5, 0, 1, 0, 165),
]


def generate_template_pendidikan_excel(include_sample=True):
    """Membuat file Excel (.xlsx) template unggah data tingkat pendidikan penduduk per SLS"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Pendidikan Penduduk"
    ws.views.sheetView[0].showGridLines = True

    header_fill, header_font, total_fill, total_font, data_font, thin_border = get_excel_styles()
    headers = ["No.", "Nama SLS"] + [col[1] for col in PENDIDIKAN_COLUMNS] + ["Jumlah"]
    ws.append(headers)

    ws.row_dimensions[1].height = 28
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = thin_border

    rows_to_insert = SAMPLE_PENDIDIKAN_DATA if include_sample else []
    current_row = 2

    if rows_to_insert:
        for item in rows_to_insert:
            no = item[0]
            nama = item[1]
            vals = list(item[2:25])
            sum_formula = f"=SUM(C{current_row}:Y{current_row})"
            ws.append([no, nama] + vals + [sum_formula])

            ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
            for c_idx in range(3, len(headers) + 1):
                ws.cell(row=current_row, column=c_idx).alignment = Alignment(horizontal='center', vertical='center')

            for col in range(1, len(headers) + 1):
                c = ws.cell(row=current_row, column=col)
                c.font = data_font
                c.border = thin_border
            current_row += 1
    else:
        # Template kosong siap isi dengan 5 baris contoh RT
        for i in range(1, 6):
            sum_formula = f"=SUM(C{current_row}:Y{current_row})"
            ws.append([i, f"RT 00{i} RW 001"] + [0]*len(PENDIDIKAN_COLUMNS) + [sum_formula])
            ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
            for c_idx in range(3, len(headers) + 1):
                ws.cell(row=current_row, column=c_idx).alignment = Alignment(horizontal='center', vertical='center')
            for col in range(1, len(headers) + 1):
                c = ws.cell(row=current_row, column=col)
                c.font = data_font
                c.border = thin_border
            current_row += 1

    # Baris TOTAL (persis seperti gambar)
    total_row = current_row
    ws.row_dimensions[total_row].height = 24
    total_cells = ["Total", ""]
    for col_idx in range(3, len(headers) + 1):
        col_letter = get_column_letter(col_idx)
        total_cells.append(f"=SUM({col_letter}2:{col_letter}{total_row-1})")
    ws.append(total_cells)

    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=total_row, column=col_idx)
        cell.fill = total_fill
        cell.font = total_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    ws.column_dimensions['A'].width = 7
    ws.column_dimensions['B'].width = 18
    for col_idx in range(3, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 13

    mem = io.BytesIO()
    wb.save(mem)
    mem.seek(0)
    return mem


def generate_template_pendidikan_csv(include_sample=True):
    """Membuat template CSV data tingkat pendidikan per SLS"""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)

    headers = ["No.", "Nama SLS"] + [col[1] for col in PENDIDIKAN_COLUMNS] + ["Jumlah"]
    writer.writerow(headers)

    rows = SAMPLE_PENDIDIKAN_DATA if include_sample else []
    for item in rows:
        writer.writerow(list(item))

    if rows:
        tot_cells = ["Total", ""]
        for c in range(2, len(headers)):
            tot_cells.append(sum(r[c] for r in rows))
        writer.writerow(tot_cells)

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def export_pendidikan_excel(rows, tahun):
    """Ekspor data tingkat pendidikan per SLS tahun tertentu ke file Excel (.xlsx)"""
    wb = Workbook()
    ws = wb.active
    ws.title = f"Pendidikan_{tahun}"
    ws.views.sheetView[0].showGridLines = True

    header_fill, header_font, total_fill, total_font, data_font, thin_border = get_excel_styles()
    headers = ["No.", "Nama SLS"] + [col[1] for col in PENDIDIKAN_COLUMNS] + ["Jumlah"]
    ws.append(headers)

    ws.row_dimensions[1].height = 28
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = thin_border

    current_row = 2
    for r in rows:
        no = r.get('no_urut', current_row - 1)
        nama = r.get('nama_sls', '')
        vals = [r.get(col[0], 0) for col in PENDIDIKAN_COLUMNS]
        sum_formula = f"=SUM(C{current_row}:Y{current_row})"
        ws.append([no, nama] + vals + [sum_formula])

        ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
        for c_idx in range(3, len(headers) + 1):
            ws.cell(row=current_row, column=c_idx).alignment = Alignment(horizontal='center', vertical='center')

        for col in range(1, len(headers) + 1):
            c = ws.cell(row=current_row, column=col)
            c.font = data_font
            c.border = thin_border
        current_row += 1

    total_row = current_row
    ws.row_dimensions[total_row].height = 24
    total_cells = ["Total", ""]
    for col_idx in range(3, len(headers) + 1):
        col_letter = get_column_letter(col_idx)
        total_cells.append(f"=SUM({col_letter}2:{col_letter}{total_row-1})")
    ws.append(total_cells)

    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=total_row, column=col_idx)
        cell.fill = total_fill
        cell.font = total_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    ws.column_dimensions['A'].width = 7
    ws.column_dimensions['B'].width = 18
    for col_idx in range(3, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 13

    mem = io.BytesIO()
    wb.save(mem)
    mem.seek(0)
    return mem


def parse_uploaded_pendidikan_file(file_storage):
    """Mem-parsing file Excel/CSV data tingkat pendidikan per SLS"""
    filename = file_storage.filename.lower()
    raw_rows = []

    if filename.endswith('.csv'):
        try:
            content = file_storage.read().decode('utf-8-sig', errors='replace')
            reader = csv.reader(io.StringIO(content))
            for row in reader:
                raw_rows.append(row)
        except Exception as e:
            return None, f"Gagal membaca file CSV: {str(e)}"
    elif filename.endswith(('.xlsx', '.xls')):
        try:
            wb = load_workbook(filename=file_storage, data_only=True)
            ws = wb.active
            for row in ws.iter_rows(values_only=True):
                raw_rows.append(list(row))
        except Exception as e:
            return None, f"Gagal membaca file Excel: {str(e)}"
    else:
        return None, "Format file tidak didukung. Harap unggah file .xlsx atau .csv."

    clean_rows = []
    for r in raw_rows:
        if r and any(cell is not None and str(cell).strip() != '' for cell in r):
            clean_rows.append([str(c).strip() if c is not None else '' for c in r])

    if len(clean_rows) < 2:
        return None, "File spreadsheet tidak memuat data yang cukup."

    header_row = clean_rows[0]
    col_map = {}

    def norm_h(text):
        return re.sub(r'[^a-z0-9]', '', str(text).lower())

    for c_idx, h_text in enumerate(header_row):
        h_norm = norm_h(h_text)
        if h_norm in ['no', 'nourut', 'nomor']:
            col_map['no_urut'] = c_idx
        elif any(k in h_norm for k in ['namasls', 'sls', 'wilayah', 'rt', 'rtrw']):
            col_map['nama_sls'] = c_idx
        elif any(k in h_norm for k in ['tidakmemiliki', 'tidakijazah', 'tidaksekolah', 'tanpaijazah']):
            col_map['tidak_sekolah'] = c_idx
        elif h_norm == 'sd':
            col_map['sd'] = c_idx
        elif h_norm == 'mi':
            col_map['mi'] = c_idx
        elif 'paketa' in h_norm:
            col_map['paket_a'] = c_idx
        elif 'sdlb' in h_norm:
            col_map['sdlb'] = c_idx
        elif 'ula' in h_norm:
            col_map['spm_ula'] = c_idx
        elif h_norm == 'smp':
            col_map['smp'] = c_idx
        elif h_norm == 'mts':
            col_map['mts'] = c_idx
        elif 'smplb' in h_norm:
            col_map['smp_lb'] = c_idx
        elif 'paketb' in h_norm:
            col_map['paket_b'] = c_idx
        elif 'wustha' in h_norm:
            col_map['spm_wustha'] = c_idx
        elif h_norm == 'sma':
            col_map['sma'] = c_idx
        elif h_norm == 'smk':
            col_map['smk'] = c_idx
        elif h_norm == 'ma':
            col_map['ma'] = c_idx
        elif h_norm == 'mak':
            col_map['mak'] = c_idx
        elif 'smalb' in h_norm:
            col_map['sma_lb'] = c_idx
        elif 'paketc' in h_norm:
            col_map['paket_c'] = c_idx
        elif 'ulya' in h_norm:
            col_map['spm_ulya'] = c_idx
        elif any(k in h_norm for k in ['diploma', 'd1', 'd2', 'd3', 'didii', 'diii']):
            col_map['diploma'] = c_idx
        elif any(k in h_norm for k in ['divs1', 's1', 'sarjana']):
            col_map['s1'] = c_idx
        elif 'profesi' in h_norm:
            col_map['profesi'] = c_idx
        elif h_norm == 's2':
            col_map['s2'] = c_idx
        elif h_norm == 's3':
            col_map['s3'] = c_idx
        elif any(k in h_norm for k in ['jumlah', 'total']):
            col_map['jumlah'] = c_idx

    parsed_records = []
    for r_idx in range(1, len(clean_rows)):
        row = clean_rows[r_idx]
        sls_idx = col_map.get('nama_sls', 1)
        sls_str = row[sls_idx].strip() if sls_idx < len(row) else ''

        if not sls_str or sls_str.upper() in ['TOTAL', 'T O T A L', 'JUMLAH', 'REKAPITULASI']:
            continue

        no_idx = col_map.get('no_urut', 0)
        try:
            no_val = int(float(str(row[no_idx] or 0))) if no_idx < len(row) else len(parsed_records) + 1
        except:
            no_val = len(parsed_records) + 1

        rec = {
            'no_urut': no_val,
            'nama_sls': sls_str
        }

        row_sum = 0
        for col_key, _ in PENDIDIKAN_COLUMNS:
            c_i = col_map.get(col_key)
            val = 0
            if c_i is not None and c_i < len(row):
                try:
                    val = int(float(str(row[c_i] or 0)))
                except:
                    val = 0
            val = max(0, val)
            rec[col_key] = val
            row_sum += val

        rec['jumlah'] = row_sum
        parsed_records.append(rec)

    if not parsed_records:
        return None, "Tidak ada data baris pendidikan SLS yang valid ditemukan dalam file."

    return parsed_records, None


# ==============================================================================
# 5. DATA JUMLAH PENDUDUK BERDASARKAN STATUS PERKAWINAN PER SLS (RT/RW)
# ==============================================================================

SAMPLE_PERKAWINAN_DATA = [
    (1, 'RT 001 RW 001', 82, 85, 4, 14, 185),
    (2, 'RT 002 RW 001', 95, 122, 7, 13, 237),
    (3, 'RT 003 RW 001', 90, 128, 8, 18, 244),
    (4, 'RT 004 RW 001', 84, 95, 3, 15, 197),
    (5, 'RT 005 RW 001', 48, 67, 4, 2, 121),
    (6, 'RT 001 RW 002', 35, 66, 4, 10, 115),
    (7, 'RT 002 RW 002', 61, 76, 1, 10, 148),
    (8, 'RT 003 RW 002', 54, 74, 5, 14, 147),
    (9, 'RT 004 RW 002', 54, 89, 1, 11, 155),
    (10, 'RT 001 RW 003', 114, 152, 4, 12, 282),
    (11, 'RT 002 RW 003', 89, 119, 6, 15, 229),
    (12, 'RT 001 RW 004', 76, 127, 5, 24, 232),
    (13, 'RT 002 RW 004', 67, 101, 5, 16, 189),
    (14, 'RT 003 RW 004', 68, 131, 3, 14, 216),
    (15, 'RT 001 RW 005', 93, 122, 6, 19, 240),
    (16, 'RT 002 RW 005', 69, 94, 5, 16, 184),
    (17, 'RT 003 RW 005', 83, 124, 4, 14, 225),
    (18, 'RT 004 RW 005', 100, 133, 5, 15, 253),
    (19, 'RT 001 RW 006', 56, 88, 1, 7, 152),
    (20, 'RT 002 RW 006', 48, 75, 3, 13, 139),
    (21, 'RT 003 RW 006', 36, 49, 0, 7, 92),
    (22, 'RT 001 RW 007', 82, 100, 5, 11, 198),
    (23, 'RT 002 RW 007', 78, 88, 10, 15, 191),
    (24, 'RT 001 RW 008', 69, 98, 1, 9, 177),
    (25, 'RT 002 RW 008', 67, 92, 5, 7, 171),
    (26, 'RT 003 RW 008', 67, 101, 1, 10, 179)
]

def generate_template_perkawinan_excel(include_sample=True):
    """Membuat file Excel (.xlsx) template unggah statistik kependudukan status perkawinan per SLS"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Status Perkawinan"
    ws.views.sheetView[0].showGridLines = True

    header_fill, header_font, total_fill, total_font, data_font, thin_border = get_excel_styles()
    headers = ["No.", "Nama SLS", "Belum Kawin", "Kawin", "Cerai Hidup", "Cerai Mati", "Total"]
    ws.append(headers)

    ws.row_dimensions[1].height = 26
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    rows_to_insert = SAMPLE_PERKAWINAN_DATA if include_sample else []
    current_row = 2

    if rows_to_insert:
        for item in rows_to_insert:
            no, nama, belum_kawin, kawin, cerai_hidup, cerai_mati, _ = item
            ws.append([no, nama, belum_kawin, kawin, cerai_hidup, cerai_mati, f"=SUM(C{current_row}:F{current_row})"])
            
            ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
            for col in range(3, 8):
                ws.cell(row=current_row, column=col).alignment = Alignment(horizontal='center', vertical='center')

            for col in range(1, 8):
                c = ws.cell(row=current_row, column=col)
                c.font = data_font
                c.border = thin_border
            current_row += 1
    else:
        for i in range(1, 6):
            ws.append([i, f"RT 00{i} RW 001", 0, 0, 0, 0, f"=SUM(C{current_row}:F{current_row})"])
            ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
            for col in range(3, 8):
                ws.cell(row=current_row, column=col).alignment = Alignment(horizontal='center', vertical='center')
            for col in range(1, 8):
                c = ws.cell(row=current_row, column=col)
                c.font = data_font
                c.border = thin_border
            current_row += 1

    total_row = current_row
    ws.row_dimensions[total_row].height = 24
    ws.append(["T O T A L", "", f"=SUM(C2:C{total_row-1})", f"=SUM(D2:D{total_row-1})", f"=SUM(E2:E{total_row-1})", f"=SUM(F2:F{total_row-1})", f"=SUM(G2:G{total_row-1})"])
    
    for col_idx in range(1, 8):
        cell = ws.cell(row=total_row, column=col_idx)
        cell.fill = total_fill
        cell.font = total_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    col_widths = {1: 8, 2: 24, 3: 16, 4: 16, 5: 16, 6: 16, 7: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def generate_template_perkawinan_csv(include_sample=True):
    """Membuat file CSV template status perkawinan per SLS"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["No.", "Nama SLS", "Belum Kawin", "Kawin", "Cerai Hidup", "Cerai Mati", "Total"])
    if include_sample:
        for item in SAMPLE_PERKAWINAN_DATA:
            no, nama, bk, k, ch, cm, tot = item
            writer.writerow([no, nama, bk, k, ch, cm, tot])
    else:
        for i in range(1, 6):
            writer.writerow([i, f"RT 00{i} RW 001", 0, 0, 0, 0, 0])
    
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def export_perkawinan_excel(rows, tahun=2026):
    """Mengekspor data statistik perkawinan SLS ke file Excel resmi berformat tabel"""
    wb = Workbook()
    ws = wb.active
    ws.title = f"Perkawinan_{tahun}"
    ws.views.sheetView[0].showGridLines = True

    header_fill, header_font, total_fill, total_font, data_font, thin_border = get_excel_styles()
    headers = ["No.", "Nama SLS", "Belum Kawin", "Kawin", "Cerai Hidup", "Cerai Mati", "Total"]
    ws.append(headers)

    ws.row_dimensions[1].height = 26
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    current_row = 2
    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        bk_val = r['belum_kawin'] if isinstance(r, dict) else r[4]
        k_val = r['kawin'] if isinstance(r, dict) else r[5]
        ch_val = r['cerai_hidup'] if isinstance(r, dict) else r[6]
        cm_val = r['cerai_mati'] if isinstance(r, dict) else r[7]

        ws.append([no_val, sls_val, bk_val, k_val, ch_val, cm_val, f"=SUM(C{current_row}:F{current_row})"])
        
        ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
        for c in range(3, 8):
            ws.cell(row=current_row, column=c).alignment = Alignment(horizontal='center', vertical='center')

        for c in range(1, 8):
            cell = ws.cell(row=current_row, column=c)
            cell.font = data_font
            cell.border = thin_border
        current_row += 1

    total_row = current_row
    ws.row_dimensions[total_row].height = 24
    ws.append(["T O T A L", "", f"=SUM(C2:C{total_row-1})", f"=SUM(D2:D{total_row-1})", f"=SUM(E2:E{total_row-1})", f"=SUM(F2:F{total_row-1})", f"=SUM(G2:G{total_row-1})"])
    
    for col_idx in range(1, 8):
        cell = ws.cell(row=total_row, column=col_idx)
        cell.fill = total_fill
        cell.font = total_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    col_widths = {1: 8, 2: 24, 3: 16, 4: 16, 5: 16, 6: 16, 7: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    mem = io.BytesIO()
    wb.save(mem)
    mem.seek(0)
    return mem


def export_perkawinan_csv(rows, tahun=2026):
    """Mengekspor data statistik perkawinan SLS ke file CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["No.", "Nama SLS", "Belum Kawin", "Kawin", "Cerai Hidup", "Cerai Mati", "Total"])
    tot_bk, tot_k, tot_ch, tot_cm, tot_all = 0, 0, 0, 0, 0
    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        bk_val = r['belum_kawin'] if isinstance(r, dict) else r[4]
        k_val = r['kawin'] if isinstance(r, dict) else r[5]
        ch_val = r['cerai_hidup'] if isinstance(r, dict) else r[6]
        cm_val = r['cerai_mati'] if isinstance(r, dict) else r[7]
        row_tot = bk_val + k_val + ch_val + cm_val
        writer.writerow([no_val, sls_val, bk_val, k_val, ch_val, cm_val, row_tot])
        tot_bk += bk_val
        tot_k += k_val
        tot_ch += ch_val
        tot_cm += cm_val
        tot_all += row_tot
    writer.writerow(["TOTAL", "", tot_bk, tot_k, tot_ch, tot_cm, tot_all])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def parse_uploaded_perkawinan_file(file_storage):
    """Mem-parsing file Excel/CSV data status perkawinan per SLS"""
    filename = file_storage.filename.lower()
    raw_rows = []

    if filename.endswith('.csv'):
        try:
            content = file_storage.read().decode('utf-8-sig', errors='replace')
            reader = csv.reader(io.StringIO(content))
            for row in reader:
                raw_rows.append(row)
        except Exception as e:
            return None, f"Gagal membaca file CSV: {str(e)}"
    elif filename.endswith(('.xlsx', '.xls')):
        try:
            wb = load_workbook(filename=file_storage, data_only=True)
            ws = wb.active
            for row in ws.iter_rows(values_only=True):
                raw_rows.append(list(row))
        except Exception as e:
            return None, f"Gagal membaca file Excel: {str(e)}"
    else:
        return None, "Format file tidak didukung. Harap unggah file .xlsx atau .csv."

    clean_rows = []
    for r in raw_rows:
        if r and any(cell is not None and str(cell).strip() != '' for cell in r):
            clean_rows.append([str(c).strip() if c is not None else '' for c in r])

    if len(clean_rows) < 2:
        return None, "File spreadsheet tidak memuat data yang cukup."

    header_row = clean_rows[0]
    col_map = {}

    def norm_h(text):
        return re.sub(r'[^a-z0-9]', '', str(text).lower())

    for c_idx, h_text in enumerate(header_row):
        h_norm = norm_h(h_text)
        if h_norm in ['no', 'nourut', 'nomor']:
            col_map['no_urut'] = c_idx
        elif any(k in h_norm for k in ['namasls', 'sls', 'wilayah', 'rt', 'rtrw']):
            col_map['nama_sls'] = c_idx
        elif 'belum' in h_norm:
            col_map['belum_kawin'] = c_idx
        elif 'hidup' in h_norm:
            col_map['cerai_hidup'] = c_idx
        elif 'mati' in h_norm:
            col_map['cerai_mati'] = c_idx
        elif 'kawin' in h_norm or 'menikah' in h_norm:
            col_map['kawin'] = c_idx
        elif any(k in h_norm for k in ['total', 'jumlah']):
            col_map['total'] = c_idx

    parsed_records = []
    for r_idx in range(1, len(clean_rows)):
        row = clean_rows[r_idx]
        sls_idx = col_map.get('nama_sls', 1)
        sls_str = row[sls_idx].strip() if sls_idx < len(row) else ''

        if not sls_str or sls_str.upper() in ['TOTAL', 'T O T A L', 'JUMLAH', 'REKAPITULASI']:
            continue

        no_idx = col_map.get('no_urut', 0)
        try:
            no_val = int(float(str(row[no_idx] or 0))) if no_idx < len(row) else len(parsed_records) + 1
        except:
            no_val = len(parsed_records) + 1

        def get_int_cell(key, default_idx):
            idx = col_map.get(key, default_idx)
            if idx < len(row):
                try:
                    return max(0, int(float(str(row[idx] or 0))))
                except:
                    return 0
            return 0

        bk = get_int_cell('belum_kawin', 2)
        kw = get_int_cell('kawin', 3)
        ch = get_int_cell('cerai_hidup', 4)
        cm = get_int_cell('cerai_mati', 5)
        tot = bk + kw + ch + cm

        parsed_records.append({
            'no_urut': no_val,
            'nama_sls': sls_str,
            'belum_kawin': bk,
            'kawin': kw,
            'cerai_hidup': ch,
            'cerai_mati': cm,
            'total': tot
        })

    if not parsed_records:
        return None, "Tidak ada data baris status perkawinan yang valid ditemukan dalam file."

    return parsed_records, None


# ==============================================================================
# 6. DATA JUMLAH PENDUDUK BERSTATUS KAWIN BERDASARKAN STATUS PENCATATAN PERKAWINAN
# ==============================================================================

SAMPLE_PENCATATAN_NIKAH_DATA = [
    (1, 'RT 001 RW 001', 76, 10, 0, 86),
    (2, 'RT 002 RW 001', 100, 23, 0, 123),
    (3, 'RT 003 RW 001', 117, 11, 0, 128),
    (4, 'RT 004 RW 001', 96, 0, 0, 96),
    (5, 'RT 005 RW 001', 53, 14, 0, 67),
    (6, 'RT 001 RW 002', 66, 0, 0, 66),
    (7, 'RT 002 RW 002', 81, 1, 0, 82),
    (8, 'RT 003 RW 002', 75, 1, 0, 76),
    (9, 'RT 004 RW 002', 100, 0, 0, 100),
    (10, 'RT 001 RW 003', 137, 23, 0, 160),
    (11, 'RT 002 RW 003', 106, 23, 0, 129),
    (12, 'RT 001 RW 004', 129, 1, 0, 130),
    (13, 'RT 002 RW 004', 104, 0, 0, 104),
    (14, 'RT 003 RW 004', 137, 1, 1, 139),
    (15, 'RT 001 RW 005', 102, 21, 0, 123),
    (16, 'RT 002 RW 005', 70, 25, 0, 95),
    (17, 'RT 003 RW 005', 108, 16, 0, 124),
    (18, 'RT 004 RW 005', 111, 22, 0, 133),
    (19, 'RT 001 RW 006', 92, 1, 0, 93),
    (20, 'RT 002 RW 006', 75, 0, 0, 75),
    (21, 'RT 003 RW 006', 51, 1, 0, 52),
    (22, 'RT 001 RW 007', 94, 8, 0, 102),
    (23, 'RT 002 RW 007', 84, 6, 0, 90),
    (24, 'RT 001 RW 008', 72, 26, 0, 98),
    (25, 'RT 002 RW 008', 68, 24, 0, 92),
    (26, 'RT 003 RW 008', 72, 29, 0, 101)
]

def generate_template_pencatatan_nikah_excel(include_sample=True):
    """Membuat file Excel (.xlsx) template unggah status pencatatan perkawinan per SLS"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Pencatatan Perkawinan"
    ws.views.sheetView[0].showGridLines = True

    header_fill, header_font, total_fill, total_font, data_font, thin_border = get_excel_styles()
    headers = ["No.", "Nama SLS", "Kawin Tercatat", "Kawin Belum Tercatat", "Kawin Tidak Tercatat", "Total"]
    ws.append(headers)

    ws.row_dimensions[1].height = 26
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    rows_to_insert = SAMPLE_PENCATATAN_NIKAH_DATA if include_sample else []
    current_row = 2

    if rows_to_insert:
        for item in rows_to_insert:
            no, nama, kt, kbt, ktt, _ = item
            ws.append([no, nama, kt, kbt, ktt, f"=SUM(C{current_row}:E{current_row})"])
            
            ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
            for col in range(3, 7):
                ws.cell(row=current_row, column=col).alignment = Alignment(horizontal='center', vertical='center')

            for col in range(1, 7):
                c = ws.cell(row=current_row, column=col)
                c.font = data_font
                c.border = thin_border
            current_row += 1
    else:
        for i in range(1, 6):
            ws.append([i, f"RT 00{i} RW 001", 0, 0, 0, f"=SUM(C{current_row}:E{current_row})"])
            ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
            for col in range(3, 7):
                ws.cell(row=current_row, column=col).alignment = Alignment(horizontal='center', vertical='center')
            for col in range(1, 7):
                c = ws.cell(row=current_row, column=col)
                c.font = data_font
                c.border = thin_border
            current_row += 1

    total_row = current_row
    ws.row_dimensions[total_row].height = 24
    ws.append(["T O T A L", "", f"=SUM(C2:C{total_row-1})", f"=SUM(D2:D{total_row-1})", f"=SUM(E2:E{total_row-1})", f"=SUM(F2:F{total_row-1})"])
    
    for col_idx in range(1, 7):
        cell = ws.cell(row=total_row, column=col_idx)
        cell.fill = total_fill
        cell.font = total_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    col_widths = {1: 8, 2: 24, 3: 18, 4: 22, 5: 22, 6: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def generate_template_pencatatan_nikah_csv(include_sample=True):
    """Membuat file CSV template status pencatatan perkawinan per SLS"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["No.", "Nama SLS", "Kawin Tercatat", "Kawin Belum Tercatat", "Kawin Tidak Tercatat", "Total"])
    if include_sample:
        for item in SAMPLE_PENCATATAN_NIKAH_DATA:
            no, nama, kt, kbt, ktt, tot = item
            writer.writerow([no, nama, kt, kbt, ktt, tot])
    else:
        for i in range(1, 6):
            writer.writerow([i, f"RT 00{i} RW 001", 0, 0, 0, 0])
    
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def export_pencatatan_nikah_excel(rows, tahun=2026):
    """Mengekspor data status pencatatan perkawinan SLS ke file Excel resmi berformat tabel"""
    wb = Workbook()
    ws = wb.active
    ws.title = f"Pencatatan_Nikah_{tahun}"
    ws.views.sheetView[0].showGridLines = True

    header_fill, header_font, total_fill, total_font, data_font, thin_border = get_excel_styles()
    headers = ["No.", "Nama SLS", "Kawin Tercatat", "Kawin Belum Tercatat", "Kawin Tidak Tercatat", "Total"]
    ws.append(headers)

    ws.row_dimensions[1].height = 26
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    current_row = 2
    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        kt_val = r['kawin_tercatat'] if isinstance(r, dict) else r[4]
        kbt_val = r['kawin_belum_tercatat'] if isinstance(r, dict) else r[5]
        ktt_val = r['kawin_tidak_tercatat'] if isinstance(r, dict) else r[6]

        ws.append([no_val, sls_val, kt_val, kbt_val, ktt_val, f"=SUM(C{current_row}:E{current_row})"])
        
        ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
        for c in range(3, 7):
            ws.cell(row=current_row, column=c).alignment = Alignment(horizontal='center', vertical='center')

        for c in range(1, 7):
            cell = ws.cell(row=current_row, column=c)
            cell.font = data_font
            cell.border = thin_border
        current_row += 1

    total_row = current_row
    ws.row_dimensions[total_row].height = 24
    ws.append(["T O T A L", "", f"=SUM(C2:C{total_row-1})", f"=SUM(D2:D{total_row-1})", f"=SUM(E2:E{total_row-1})", f"=SUM(F2:F{total_row-1})"])
    
    for col_idx in range(1, 7):
        cell = ws.cell(row=total_row, column=col_idx)
        cell.fill = total_fill
        cell.font = total_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    col_widths = {1: 8, 2: 24, 3: 18, 4: 22, 5: 22, 6: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    mem = io.BytesIO()
    wb.save(mem)
    mem.seek(0)
    return mem


def export_pencatatan_nikah_csv(rows, tahun=2026):
    """Mengekspor data status pencatatan perkawinan SLS ke file CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["No.", "Nama SLS", "Kawin Tercatat", "Kawin Belum Tercatat", "Kawin Tidak Tercatat", "Total"])
    tot_kt, tot_kbt, tot_ktt, tot_all = 0, 0, 0, 0
    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        kt_val = r['kawin_tercatat'] if isinstance(r, dict) else r[4]
        kbt_val = r['kawin_belum_tercatat'] if isinstance(r, dict) else r[5]
        ktt_val = r['kawin_tidak_tercatat'] if isinstance(r, dict) else r[6]
        row_tot = kt_val + kbt_val + ktt_val
        writer.writerow([no_val, sls_val, kt_val, kbt_val, ktt_val, row_tot])
        tot_kt += kt_val
        tot_kbt += kbt_val
        tot_ktt += ktt_val
        tot_all += row_tot
    writer.writerow(["TOTAL", "", tot_kt, tot_kbt, tot_ktt, tot_all])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def parse_uploaded_pencatatan_nikah_file(file_storage):
    """Mem-parsing file Excel/CSV data status pencatatan perkawinan per SLS"""
    filename = file_storage.filename.lower()
    raw_rows = []

    if filename.endswith('.csv'):
        try:
            content = file_storage.read().decode('utf-8-sig', errors='replace')
            reader = csv.reader(io.StringIO(content))
            for row in reader:
                raw_rows.append(row)
        except Exception as e:
            return None, f"Gagal membaca file CSV: {str(e)}"
    elif filename.endswith(('.xlsx', '.xls')):
        try:
            wb = load_workbook(filename=file_storage, data_only=True)
            ws = wb.active
            for row in ws.iter_rows(values_only=True):
                raw_rows.append(list(row))
        except Exception as e:
            return None, f"Gagal membaca file Excel: {str(e)}"
    else:
        return None, "Format file tidak didukung. Harap unggah file .xlsx atau .csv."

    clean_rows = []
    for r in raw_rows:
        if r and any(cell is not None and str(cell).strip() != '' for cell in r):
            clean_rows.append([str(c).strip() if c is not None else '' for c in r])

    if len(clean_rows) < 2:
        return None, "File spreadsheet tidak memuat data yang cukup."

    header_row = clean_rows[0]
    col_map = {}

    def norm_h(text):
        return re.sub(r'[^a-z0-9]', '', str(text).lower())

    for c_idx, h_text in enumerate(header_row):
        h_norm = norm_h(h_text)
        if h_norm in ['no', 'nourut', 'nomor']:
            col_map['no_urut'] = c_idx
        elif any(k in h_norm for k in ['namasls', 'sls', 'wilayah', 'rt', 'rtrw']):
            col_map['nama_sls'] = c_idx
        elif 'belum' in h_norm and 'tercatat' in h_norm:
            col_map['kawin_belum_tercatat'] = c_idx
        elif 'tidak' in h_norm and 'tercatat' in h_norm:
            col_map['kawin_tidak_tercatat'] = c_idx
        elif 'tercatat' in h_norm:
            col_map['kawin_tercatat'] = c_idx
        elif any(k in h_norm for k in ['total', 'jumlah']):
            col_map['total'] = c_idx

    parsed_records = []
    for r_idx in range(1, len(clean_rows)):
        row = clean_rows[r_idx]
        sls_idx = col_map.get('nama_sls', 1)
        sls_str = row[sls_idx].strip() if sls_idx < len(row) else ''

        if not sls_str or sls_str.upper() in ['TOTAL', 'T O T A L', 'JUMLAH', 'REKAPITULASI']:
            continue

        no_idx = col_map.get('no_urut', 0)
        try:
            no_val = int(float(str(row[no_idx] or 0))) if no_idx < len(row) else len(parsed_records) + 1
        except:
            no_val = len(parsed_records) + 1

        def get_int_cell(key, default_idx):
            idx = col_map.get(key, default_idx)
            if idx < len(row):
                try:
                    return max(0, int(float(str(row[idx] or 0))))
                except:
                    return 0
            return 0

        kt = get_int_cell('kawin_tercatat', 2)
        kbt = get_int_cell('kawin_belum_tercatat', 3)
        ktt = get_int_cell('kawin_tidak_tercatat', 4)
        tot = kt + kbt + ktt

        parsed_records.append({
            'no_urut': no_val,
            'nama_sls': sls_str,
            'kawin_tercatat': kt,
            'kawin_belum_tercatat': kbt,
            'kawin_tidak_tercatat': ktt,
            'total': tot
        })

    if not parsed_records:
        return None, "Tidak ada data baris status pencatatan perkawinan yang valid ditemukan dalam file."

    return parsed_records, None


# ==============================================================================
# 7. DATA JUMLAH PENDUDUK MENURUT AGAMA DAN KEPERCAYAANNYA PER SLS (RT/RW)
# ==============================================================================

AGAMA_COLUMNS = [
    ('islam', 'Islam'),
    ('kristen', 'Kristen'),
    ('katholik', 'Katholik'),
    ('budha', 'Budha'),
    ('hindu', 'Hindu'),
    ('konghucu', 'Konghucu'),
    ('kepercayaan_lainnya', 'Kepercayaan Lainnya')
]

SAMPLE_AGAMA_DATA = [
    (1, 'RT 001 RW 001', 185, 0, 0, 0, 0, 0, 0, 185),
    (2, 'RT 002 RW 001', 237, 0, 0, 0, 0, 0, 0, 237),
    (3, 'RT 003 RW 001', 244, 0, 0, 0, 0, 0, 0, 244),
    (4, 'RT 004 RW 001', 197, 0, 0, 0, 0, 0, 0, 197),
    (5, 'RT 005 RW 001', 121, 0, 0, 0, 0, 0, 0, 121),
    (6, 'RT 001 RW 002', 115, 0, 0, 0, 0, 0, 0, 115),
    (7, 'RT 002 RW 002', 148, 0, 0, 0, 0, 0, 0, 148),
    (8, 'RT 003 RW 002', 147, 0, 0, 0, 0, 0, 0, 147),
    (9, 'RT 004 RW 002', 155, 0, 0, 0, 0, 0, 0, 155),
    (10, 'RT 001 RW 003', 282, 0, 0, 0, 0, 0, 0, 282),
    (11, 'RT 002 RW 003', 229, 0, 0, 0, 0, 0, 0, 229),
    (12, 'RT 001 RW 004', 232, 0, 0, 0, 0, 0, 0, 232),
    (13, 'RT 002 RW 004', 189, 0, 0, 0, 0, 0, 0, 189),
    (14, 'RT 003 RW 004', 216, 0, 0, 0, 0, 0, 0, 216),
    (15, 'RT 001 RW 005', 240, 0, 0, 0, 0, 0, 0, 240),
    (16, 'RT 002 RW 005', 184, 0, 0, 0, 0, 0, 0, 184),
    (17, 'RT 003 RW 005', 225, 0, 0, 0, 0, 0, 0, 225),
    (18, 'RT 004 RW 005', 253, 0, 0, 0, 0, 0, 0, 253),
    (19, 'RT 001 RW 006', 152, 0, 0, 0, 0, 0, 0, 152),
    (20, 'RT 002 RW 006', 139, 0, 0, 0, 0, 0, 0, 139),
    (21, 'RT 003 RW 006', 92, 0, 0, 0, 0, 0, 0, 92),
    (22, 'RT 001 RW 007', 198, 0, 0, 0, 0, 0, 0, 198),
    (23, 'RT 002 RW 007', 191, 0, 0, 0, 0, 0, 0, 191),
    (24, 'RT 001 RW 008', 177, 0, 0, 0, 0, 0, 0, 177),
    (25, 'RT 002 RW 008', 171, 0, 0, 0, 0, 0, 0, 171),
    (26, 'RT 003 RW 008', 179, 0, 0, 0, 0, 0, 0, 179)
]

def generate_template_agama_excel(include_sample=True):
    """Membuat file Excel (.xlsx) template unggah statistik agama dan kepercayaan per SLS"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Agama dan Kepercayaan"
    ws.views.sheetView[0].showGridLines = True

    header_fill, header_font, total_fill, total_font, data_font, thin_border = get_excel_styles()
    headers = ["No.", "Nama SLS", "Islam", "Kristen", "Katholik", "Budha", "Hindu", "Konghucu", "Kepercayaan Lainnya", "Total"]
    ws.append(headers)

    ws.row_dimensions[1].height = 26
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    rows_to_insert = SAMPLE_AGAMA_DATA if include_sample else []
    current_row = 2

    if rows_to_insert:
        for item in rows_to_insert:
            no, nama, isl, krs, kat, bud, hin, khg, kep, _ = item
            ws.append([no, nama, isl, krs, kat, bud, hin, khg, kep, f"=SUM(C{current_row}:I{current_row})"])
            
            ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
            for col in range(3, 11):
                ws.cell(row=current_row, column=col).alignment = Alignment(horizontal='center', vertical='center')

            for col in range(1, 11):
                c = ws.cell(row=current_row, column=col)
                c.font = data_font
                c.border = thin_border
            current_row += 1
    else:
        for i in range(1, 6):
            ws.append([i, f"RT 00{i} RW 001", 0, 0, 0, 0, 0, 0, 0, f"=SUM(C{current_row}:I{current_row})"])
            ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
            for col in range(3, 11):
                ws.cell(row=current_row, column=col).alignment = Alignment(horizontal='center', vertical='center')
            for col in range(1, 11):
                c = ws.cell(row=current_row, column=col)
                c.font = data_font
                c.border = thin_border
            current_row += 1

    total_row = current_row
    ws.row_dimensions[total_row].height = 24
    ws.append(["T O T A L", "", f"=SUM(C2:C{total_row-1})", f"=SUM(D2:D{total_row-1})", f"=SUM(E2:E{total_row-1})", f"=SUM(F2:F{total_row-1})", f"=SUM(G2:G{total_row-1})", f"=SUM(H2:H{total_row-1})", f"=SUM(I2:I{total_row-1})", f"=SUM(J2:J{total_row-1})"])
    
    for col_idx in range(1, 11):
        cell = ws.cell(row=total_row, column=col_idx)
        cell.fill = total_fill
        cell.font = total_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    col_widths = {1: 8, 2: 24, 3: 14, 4: 14, 5: 14, 6: 14, 7: 14, 8: 14, 9: 22, 10: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def generate_template_agama_csv(include_sample=True):
    """Membuat file CSV template agama dan kepercayaan per SLS"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["No.", "Nama SLS", "Islam", "Kristen", "Katholik", "Budha", "Hindu", "Konghucu", "Kepercayaan Lainnya", "Total"])
    if include_sample:
        for item in SAMPLE_AGAMA_DATA:
            no, nama, isl, krs, kat, bud, hin, khg, kep, tot = item
            writer.writerow([no, nama, isl, krs, kat, bud, hin, khg, kep, tot])
    else:
        for i in range(1, 6):
            writer.writerow([i, f"RT 00{i} RW 001", 0, 0, 0, 0, 0, 0, 0, 0])
    
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def export_agama_excel(rows, tahun=2026):
    """Mengekspor data statistik agama per SLS ke file Excel resmi berformat tabel"""
    wb = Workbook()
    ws = wb.active
    ws.title = f"Agama_{tahun}"
    ws.views.sheetView[0].showGridLines = True

    header_fill, header_font, total_fill, total_font, data_font, thin_border = get_excel_styles()
    headers = ["No.", "Nama SLS", "Islam", "Kristen", "Katholik", "Budha", "Hindu", "Konghucu", "Kepercayaan Lainnya", "Total"]
    ws.append(headers)

    ws.row_dimensions[1].height = 26
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    current_row = 2
    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        isl_val = r['islam'] if isinstance(r, dict) else r[4]
        krs_val = r['kristen'] if isinstance(r, dict) else r[5]
        kat_val = r['katholik'] if isinstance(r, dict) else r[6]
        bud_val = r['budha'] if isinstance(r, dict) else r[7]
        hin_val = r['hindu'] if isinstance(r, dict) else r[8]
        khg_val = r['konghucu'] if isinstance(r, dict) else r[9]
        kep_val = r['kepercayaan_lainnya'] if isinstance(r, dict) else r[10]

        ws.append([no_val, sls_val, isl_val, krs_val, kat_val, bud_val, hin_val, khg_val, kep_val, f"=SUM(C{current_row}:I{current_row})"])
        
        ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='left', vertical='center')
        for c in range(3, 11):
            ws.cell(row=current_row, column=c).alignment = Alignment(horizontal='center', vertical='center')

        for c in range(1, 11):
            cell = ws.cell(row=current_row, column=c)
            cell.font = data_font
            cell.border = thin_border
        current_row += 1

    total_row = current_row
    ws.row_dimensions[total_row].height = 24
    ws.append(["T O T A L", "", f"=SUM(C2:C{total_row-1})", f"=SUM(D2:D{total_row-1})", f"=SUM(E2:E{total_row-1})", f"=SUM(F2:F{total_row-1})", f"=SUM(G2:G{total_row-1})", f"=SUM(H2:H{total_row-1})", f"=SUM(I2:I{total_row-1})", f"=SUM(J2:J{total_row-1})"])
    
    for col_idx in range(1, 11):
        cell = ws.cell(row=total_row, column=col_idx)
        cell.fill = total_fill
        cell.font = total_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    col_widths = {1: 8, 2: 24, 3: 14, 4: 14, 5: 14, 6: 14, 7: 14, 8: 14, 9: 22, 10: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    mem = io.BytesIO()
    wb.save(mem)
    mem.seek(0)
    return mem


def export_agama_csv(rows, tahun=2026):
    """Mengekspor data statistik agama per SLS ke file CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["No.", "Nama SLS", "Islam", "Kristen", "Katholik", "Budha", "Hindu", "Konghucu", "Kepercayaan Lainnya", "Total"])
    tot_isl, tot_krs, tot_kat, tot_bud, tot_hin, tot_khg, tot_kep, tot_all = 0, 0, 0, 0, 0, 0, 0, 0
    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        isl_val = r['islam'] if isinstance(r, dict) else r[4]
        krs_val = r['kristen'] if isinstance(r, dict) else r[5]
        kat_val = r['katholik'] if isinstance(r, dict) else r[6]
        bud_val = r['budha'] if isinstance(r, dict) else r[7]
        hin_val = r['hindu'] if isinstance(r, dict) else r[8]
        khg_val = r['konghucu'] if isinstance(r, dict) else r[9]
        kep_val = r['kepercayaan_lainnya'] if isinstance(r, dict) else r[10]
        row_tot = isl_val + krs_val + kat_val + bud_val + hin_val + khg_val + kep_val
        writer.writerow([no_val, sls_val, isl_val, krs_val, kat_val, bud_val, hin_val, khg_val, kep_val, row_tot])
        tot_isl += isl_val
        tot_krs += krs_val
        tot_kat += kat_val
        tot_bud += bud_val
        tot_hin += hin_val
        tot_khg += khg_val
        tot_kep += kep_val
        tot_all += row_tot
    writer.writerow(["TOTAL", "", tot_isl, tot_krs, tot_kat, tot_bud, tot_hin, tot_khg, tot_kep, tot_all])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def parse_uploaded_agama_file(file_storage):
    """Mem-parsing file Excel/CSV data agama dan kepercayaan per SLS"""
    filename = file_storage.filename.lower()
    raw_rows = []

    if filename.endswith('.csv'):
        try:
            content = file_storage.read().decode('utf-8-sig', errors='replace')
            reader = csv.reader(io.StringIO(content))
            for row in reader:
                raw_rows.append(row)
        except Exception as e:
            return None, f"Gagal membaca file CSV: {str(e)}"
    elif filename.endswith(('.xlsx', '.xls')):
        try:
            wb = load_workbook(filename=file_storage, data_only=True)
            ws = wb.active
            for row in ws.iter_rows(values_only=True):
                raw_rows.append(list(row))
        except Exception as e:
            return None, f"Gagal membaca file Excel: {str(e)}"
    else:
        return None, "Format file tidak didukung. Harap unggah file .xlsx atau .csv."

    clean_rows = []
    for r in raw_rows:
        if r and any(cell is not None and str(cell).strip() != '' for cell in r):
            clean_rows.append([str(c).strip() if c is not None else '' for c in r])

    if len(clean_rows) < 2:
        return None, "File spreadsheet tidak memuat data yang cukup."

    header_row = clean_rows[0]
    col_map = {}

    def norm_h(text):
        return re.sub(r'[^a-z0-9]', '', str(text).lower())

    for c_idx, h_text in enumerate(header_row):
        h_norm = norm_h(h_text)
        if h_norm in ['no', 'nourut', 'nomor']:
            col_map['no_urut'] = c_idx
        elif any(k in h_norm for k in ['namasls', 'sls', 'wilayah', 'rt', 'rtrw']):
            col_map['nama_sls'] = c_idx
        elif 'islam' in h_norm or 'muslim' in h_norm:
            col_map['islam'] = c_idx
        elif 'katolik' in h_norm or 'katholik' in h_norm:
            col_map['katholik'] = c_idx
        elif 'kristen' in h_norm or 'protestan' in h_norm:
            col_map['kristen'] = c_idx
        elif 'budha' in h_norm or 'buddha' in h_norm:
            col_map['budha'] = c_idx
        elif 'hindu' in h_norm:
            col_map['hindu'] = c_idx
        elif 'konghucu' in h_norm or 'khonghucu' in h_norm:
            col_map['konghucu'] = c_idx
        elif any(k in h_norm for k in ['kepercayaan', 'lainnya', 'aliran']):
            col_map['kepercayaan_lainnya'] = c_idx
        elif any(k in h_norm for k in ['total', 'jumlah']):
            col_map['total'] = c_idx

    parsed_records = []
    for r_idx in range(1, len(clean_rows)):
        row = clean_rows[r_idx]
        sls_idx = col_map.get('nama_sls', 1)
        sls_str = row[sls_idx].strip() if sls_idx < len(row) else ''

        if not sls_str or sls_str.upper() in ['TOTAL', 'T O T A L', 'JUMLAH', 'REKAPITULASI']:
            continue

        no_idx = col_map.get('no_urut', 0)
        try:
            no_val = int(float(str(row[no_idx] or 0))) if no_idx < len(row) else len(parsed_records) + 1
        except:
            no_val = len(parsed_records) + 1

        def get_int_cell(key, default_idx):
            idx = col_map.get(key, default_idx)
            if idx < len(row):
                try:
                    return max(0, int(float(str(row[idx] or 0))))
                except:
                    return 0
            return 0

        isl = get_int_cell('islam', 2)
        krs = get_int_cell('kristen', 3)
        kat = get_int_cell('katholik', 4)
        bud = get_int_cell('budha', 5)
        hin = get_int_cell('hindu', 6)
        khg = get_int_cell('konghucu', 7)
        kep = get_int_cell('kepercayaan_lainnya', 8)
        tot = isl + krs + kat + bud + hin + khg + kep

        parsed_records.append({
            'no_urut': no_val,
            'nama_sls': sls_str,
            'islam': isl,
            'kristen': krs,
            'katholik': kat,
            'budha': bud,
            'hindu': hin,
            'konghucu': khg,
            'kepercayaan_lainnya': kep,
            'total': tot
        })

    if not parsed_records:
        return None, "Tidak ada data baris agama SLS yang valid ditemukan dalam file."

    return parsed_records, None


# ==============================================================================
# 10. HELPER BANTUAN SOSIAL (BANSOS) PER SLS (RT/RW)
# ==============================================================================

BANSOS_COLUMNS = [
    "No.", "Nama SLS", "PKH", "BPNT", "BOS", "BAPANAS",
    "STUNTING", "PBI JKN/ KIS", "BLT", "BLT DD", "Lainnya", "Total"
]

SAMPLE_BANSOS_DATA = [
    (1, "RT 001 RW 001", 9, 18, 0, 0, 0, 2, 0, 0, 4, 33),
    (2, "RT 002 RW 001", 1, 11, 0, 0, 0, 0, 1, 3, 4, 20),
    (3, "RT 003 RW 001", 7, 21, 0, 0, 0, 1, 1, 2, 2, 34),
    (4, "RT 004 RW 001", 15, 37, 1, 0, 0, 34, 0, 4, 0, 91),
    (5, "RT 005 RW 001", 3, 6, 0, 0, 0, 0, 0, 1, 2, 12),
    (6, "RT 001 RW 002", 3, 17, 0, 0, 0, 4, 0, 12, 14, 50),
    (7, "RT 002 RW 002", 8, 14, 0, 0, 0, 8, 1, 15, 1, 47),
    (8, "RT 003 RW 002", 4, 21, 0, 0, 0, 9, 0, 0, 1, 35),
    (9, "RT 004 RW 002", 6, 21, 0, 0, 0, 26, 0, 28, 13, 94),
    (10, "RT 001 RW 003", 8, 28, 0, 0, 0, 21, 0, 0, 0, 57),
    (11, "RT 002 RW 003", 2, 6, 0, 0, 0, 15, 0, 0, 0, 23),
    (12, "RT 001 RW 004", 12, 32, 0, 0, 0, 0, 0, 1, 1, 46),
    (13, "RT 002 RW 004", 8, 18, 0, 0, 0, 0, 0, 6, 0, 32),
    (14, "RT 003 RW 004", 4, 16, 0, 0, 0, 0, 0, 0, 0, 20),
    (15, "RT 001 RW 005", 9, 30, 0, 0, 0, 15, 0, 17, 0, 71),
    (16, "RT 002 RW 005", 6, 22, 0, 0, 0, 5, 1, 30, 3, 67),
    (17, "RT 003 RW 005", 14, 21, 0, 0, 0, 16, 7, 11, 4, 73),
    (18, "RT 004 RW 005", 15, 26, 0, 0, 0, 16, 3, 6, 5, 71),
    (19, "RT 001 RW 006", 7, 12, 0, 0, 0, 2, 0, 3, 3, 27),
    (20, "RT 002 RW 006", 4, 14, 0, 0, 0, 2, 0, 7, 9, 36),
    (21, "RT 003 RW 006", 7, 8, 0, 0, 0, 1, 0, 0, 0, 16),
    (22, "RT 001 RW 007", 7, 9, 0, 0, 0, 10, 0, 0, 0, 26),
    (23, "RT 002 RW 007", 7, 24, 0, 0, 0, 13, 1, 3, 0, 48),
    (24, "RT 001 RW 008", 6, 22, 0, 0, 0, 16, 0, 0, 0, 44),
    (25, "RT 002 RW 008", 3, 11, 0, 0, 0, 5, 0, 0, 0, 19),
    (26, "RT 003 RW 008", 7, 18, 0, 0, 0, 8, 0, 0, 0, 33)
]


def generate_template_bansos_excel(include_sample=True):
    """Menghasilkan file template Excel (.xlsx) data bantuan sosial per SLS"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Bantuan Sosial SLS"

    header_fill = PatternFill(start_color="E67E22", end_color="E67E22", fill_type="solid")
    total_header_fill = PatternFill(start_color="D35400", end_color="D35400", fill_type="solid")
    footer_fill = PatternFill(start_color="F39C12", end_color="F39C12", fill_type="solid")

    header_font = Font(name="Segoe UI", size=10, bold=True, color="000000")
    total_header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    data_font = Font(name="Segoe UI", size=10)
    footer_font = Font(name="Segoe UI", size=10, bold=True, color="000000")

    thin_border = Border(
        left=Side(style='thin', color='D0D7DE'),
        right=Side(style='thin', color='D0D7DE'),
        top=Side(style='thin', color='D0D7DE'),
        bottom=Side(style='thin', color='D0D7DE')
    )

    ws.append(BANSOS_COLUMNS)
    ws.row_dimensions[1].height = 26

    for col_idx in range(1, len(BANSOS_COLUMNS) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = total_header_fill if col_idx == 12 else header_fill
        cell.font = total_header_font if col_idx == 12 else header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    rows_to_write = SAMPLE_BANSOS_DATA if include_sample else [
        (i, f"RT {i:03d} RW 001", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for i in range(1, 27)
    ]

    current_row = 2
    for r in rows_to_write:
        no, nama, pkh, bpnt, bos, bap, stun, pbi, blt, bldd, lain, tot = r
        ws.append([no, nama, pkh, bpnt, bos, bap, stun, pbi, blt, bldd, lain, f"=SUM(C{current_row}:K{current_row})"])
        ws.row_dimensions[current_row].height = 20

        for col_idx in range(1, 13):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx == 1:
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif col_idx == 2:
                cell.alignment = Alignment(horizontal='left', vertical='center')
            elif col_idx == 12:
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.font = Font(name="Segoe UI", size=10, bold=True, color="8A3B00")
            else:
                cell.alignment = Alignment(horizontal='center', vertical='center')
        current_row += 1

    last_data_row = current_row - 1
    ws.append([
        "TOTAL", "",
        f"=SUM(C2:C{last_data_row})",
        f"=SUM(D2:D{last_data_row})",
        f"=SUM(E2:E{last_data_row})",
        f"=SUM(F2:F{last_data_row})",
        f"=SUM(G2:G{last_data_row})",
        f"=SUM(H2:H{last_data_row})",
        f"=SUM(I2:I{last_data_row})",
        f"=SUM(J2:J{last_data_row})",
        f"=SUM(K2:K{last_data_row})",
        f"=SUM(L2:L{last_data_row})"
    ])
    ws.row_dimensions[current_row].height = 24

    for col_idx in range(1, 13):
        cell = ws.cell(row=current_row, column=col_idx)
        cell.fill = footer_fill
        cell.font = footer_font
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='center', vertical='center')

    col_widths = {
        1: 8, 2: 20, 3: 10, 4: 10, 5: 10, 6: 12,
        7: 12, 8: 14, 9: 10, 10: 12, 11: 12, 12: 12
    }
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    mem = io.BytesIO()
    wb.save(mem)
    mem.seek(0)
    return mem


def generate_template_bansos_csv(include_sample=True):
    """Menghasilkan file template CSV (.csv) data bantuan sosial per SLS"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(BANSOS_COLUMNS)

    rows = SAMPLE_BANSOS_DATA if include_sample else [
        (i, f"RT {i:03d} RW 001", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for i in range(1, 27)
    ]
    for r in rows:
        writer.writerow(list(r))

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def export_bansos_excel(rows, tahun=2026):
    """Mengekspor data statistik bantuan sosial per SLS ke file Excel (.xlsx)"""
    wb = Workbook()
    ws = wb.active
    ws.title = f"Bansos SLS {tahun}"

    header_fill = PatternFill(start_color="E67E22", end_color="E67E22", fill_type="solid")
    total_header_fill = PatternFill(start_color="D35400", end_color="D35400", fill_type="solid")
    footer_fill = PatternFill(start_color="F39C12", end_color="F39C12", fill_type="solid")

    header_font = Font(name="Segoe UI", size=10, bold=True, color="000000")
    total_header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    data_font = Font(name="Segoe UI", size=10)
    footer_font = Font(name="Segoe UI", size=10, bold=True, color="000000")

    thin_border = Border(
        left=Side(style='thin', color='D0D7DE'),
        right=Side(style='thin', color='D0D7DE'),
        top=Side(style='thin', color='D0D7DE'),
        bottom=Side(style='thin', color='D0D7DE')
    )

    ws.append(BANSOS_COLUMNS)
    ws.row_dimensions[1].height = 26

    for col_idx in range(1, len(BANSOS_COLUMNS) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = total_header_fill if col_idx == 12 else header_fill
        cell.font = total_header_font if col_idx == 12 else header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    current_row = 2
    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        pkh_val = r['pkh'] if isinstance(r, dict) else r[4]
        bpnt_val = r['bpnt'] if isinstance(r, dict) else r[5]
        bos_val = r['bos'] if isinstance(r, dict) else r[6]
        bap_val = r['bapanas'] if isinstance(r, dict) else r[7]
        stun_val = r['stunting'] if isinstance(r, dict) else r[8]
        pbi_val = r['pbi_jkn'] if isinstance(r, dict) else r[9]
        blt_val = r['blt'] if isinstance(r, dict) else r[10]
        bldd_val = r['blt_dd'] if isinstance(r, dict) else r[11]
        lain_val = r['lainnya'] if isinstance(r, dict) else r[12]

        ws.append([
            no_val, sls_val, pkh_val, bpnt_val, bos_val, bap_val,
            stun_val, pbi_val, blt_val, bldd_val, lain_val,
            f"=SUM(C{current_row}:K{current_row})"
        ])
        ws.row_dimensions[current_row].height = 20

        for col_idx in range(1, 13):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx == 1:
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif col_idx == 2:
                cell.alignment = Alignment(horizontal='left', vertical='center')
            elif col_idx == 12:
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.font = Font(name="Segoe UI", size=10, bold=True, color="8A3B00")
            else:
                cell.alignment = Alignment(horizontal='center', vertical='center')
        current_row += 1

    last_data_row = current_row - 1
    if rows:
        ws.append([
            "TOTAL", "",
            f"=SUM(C2:C{last_data_row})",
            f"=SUM(D2:D{last_data_row})",
            f"=SUM(E2:E{last_data_row})",
            f"=SUM(F2:F{last_data_row})",
            f"=SUM(G2:G{last_data_row})",
            f"=SUM(H2:H{last_data_row})",
            f"=SUM(I2:I{last_data_row})",
            f"=SUM(J2:J{last_data_row})",
            f"=SUM(K2:K{last_data_row})",
            f"=SUM(L2:L{last_data_row})"
        ])
    else:
        ws.append(["TOTAL", "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    ws.row_dimensions[current_row].height = 24
    for col_idx in range(1, 13):
        cell = ws.cell(row=current_row, column=col_idx)
        cell.fill = footer_fill
        cell.font = footer_font
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='center', vertical='center')

    col_widths = {
        1: 8, 2: 20, 3: 10, 4: 10, 5: 10, 6: 12,
        7: 12, 8: 14, 9: 10, 10: 12, 11: 12, 12: 12
    }
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    mem = io.BytesIO()
    wb.save(mem)
    mem.seek(0)
    return mem


def export_bansos_csv(rows, tahun=2026):
    """Mengekspor data statistik bantuan sosial per SLS ke file CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(BANSOS_COLUMNS)

    tot_pkh, tot_bpnt, tot_bos, tot_bap = 0, 0, 0, 0
    tot_stun, tot_pbi, tot_blt, tot_bldd, tot_lain, tot_all = 0, 0, 0, 0, 0, 0

    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        pkh_val = r['pkh'] if isinstance(r, dict) else r[4]
        bpnt_val = r['bpnt'] if isinstance(r, dict) else r[5]
        bos_val = r['bos'] if isinstance(r, dict) else r[6]
        bap_val = r['bapanas'] if isinstance(r, dict) else r[7]
        stun_val = r['stunting'] if isinstance(r, dict) else r[8]
        pbi_val = r['pbi_jkn'] if isinstance(r, dict) else r[9]
        blt_val = r['blt'] if isinstance(r, dict) else r[10]
        bldd_val = r['blt_dd'] if isinstance(r, dict) else r[11]
        lain_val = r['lainnya'] if isinstance(r, dict) else r[12]
        row_tot = pkh_val + bpnt_val + bos_val + bap_val + stun_val + pbi_val + blt_val + bldd_val + lain_val

        writer.writerow([
            no_val, sls_val, pkh_val, bpnt_val, bos_val, bap_val,
            stun_val, pbi_val, blt_val, bldd_val, lain_val, row_tot
        ])

        tot_pkh += pkh_val
        tot_bpnt += bpnt_val
        tot_bos += bos_val
        tot_bap += bap_val
        tot_stun += stun_val
        tot_pbi += pbi_val
        tot_blt += blt_val
        tot_bldd += bldd_val
        tot_lain += lain_val
        tot_all += row_tot

    writer.writerow([
        "TOTAL", "", tot_pkh, tot_bpnt, tot_bos, tot_bap,
        tot_stun, tot_pbi, tot_blt, tot_bldd, tot_lain, tot_all
    ])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def parse_uploaded_bansos_file(file_storage):
    """Mem-parsing file Excel/CSV data bantuan sosial per SLS"""
    filename = file_storage.filename.lower()
    raw_rows = []

    if filename.endswith('.csv'):
        try:
            content = file_storage.read().decode('utf-8-sig', errors='replace')
            reader = csv.reader(io.StringIO(content))
            for row in reader:
                raw_rows.append(row)
        except Exception as e:
            return None, f"Gagal membaca file CSV: {str(e)}"
    elif filename.endswith(('.xlsx', '.xls')):
        try:
            wb = load_workbook(filename=file_storage, data_only=True)
            ws = wb.active
            for row in ws.iter_rows(values_only=True):
                raw_rows.append(list(row))
        except Exception as e:
            return None, f"Gagal membaca file Excel: {str(e)}"
    else:
        return None, "Format file tidak didukung. Harap unggah file .xlsx atau .csv."

    clean_rows = []
    for r in raw_rows:
        if r and any(cell is not None and str(cell).strip() != '' for cell in r):
            clean_rows.append([str(c).strip() if c is not None else '' for c in r])

    if len(clean_rows) < 2:
        return None, "File spreadsheet tidak memuat data yang cukup."

    header_row = clean_rows[0]
    col_map = {}

    def norm_h(text):
        return re.sub(r'[^a-z0-9]', '', str(text).lower())

    for c_idx, h_text in enumerate(header_row):
        h_norm = norm_h(h_text)
        if h_norm in ['no', 'nourut', 'nomor']:
            col_map['no_urut'] = c_idx
        elif any(k in h_norm for k in ['namasls', 'sls', 'wilayah', 'rt', 'rtrw']):
            col_map['nama_sls'] = c_idx
        elif 'pkh' in h_norm:
            col_map['pkh'] = c_idx
        elif 'bpnt' in h_norm or 'sembako' in h_norm:
            col_map['bpnt'] = c_idx
        elif 'bos' in h_norm:
            col_map['bos'] = c_idx
        elif 'bapanas' in h_norm or 'pangan' in h_norm or 'beras' in h_norm:
            col_map['bapanas'] = c_idx
        elif 'stunting' in h_norm:
            col_map['stunting'] = c_idx
        elif 'pbijkn' in h_norm or 'pbi' in h_norm or 'kis' in h_norm or 'bpjs' in h_norm:
            col_map['pbi_jkn'] = c_idx
        elif h_norm in ['bltdd', 'bltdanadesa']:
            col_map['blt_dd'] = c_idx
        elif h_norm == 'blt' or 'bltkemensos' in h_norm:
            col_map['blt'] = c_idx
        elif 'lain' in h_norm:
            col_map['lainnya'] = c_idx
        elif any(k in h_norm for k in ['total', 'jumlah']):
            col_map['total'] = c_idx

    parsed_records = []
    for r_idx in range(1, len(clean_rows)):
        row = clean_rows[r_idx]
        sls_idx = col_map.get('nama_sls', 1)
        sls_str = row[sls_idx].strip() if sls_idx < len(row) else ''

        if not sls_str or sls_str.upper() in ['TOTAL', 'T O T A L', 'JUMLAH', 'REKAPITULASI']:
            continue

        no_idx = col_map.get('no_urut', 0)
        try:
            no_val = int(float(str(row[no_idx] or 0))) if no_idx < len(row) else len(parsed_records) + 1
        except:
            no_val = len(parsed_records) + 1

        def get_int_cell(key, default_idx):
            idx = col_map.get(key, default_idx)
            if idx < len(row):
                try:
                    return max(0, int(float(str(row[idx] or 0))))
                except:
                    return 0
            return 0

        pkh = get_int_cell('pkh', 2)
        bpnt = get_int_cell('bpnt', 3)
        bos = get_int_cell('bos', 4)
        bap = get_int_cell('bapanas', 5)
        stun = get_int_cell('stunting', 6)
        pbi = get_int_cell('pbi_jkn', 7)
        blt = get_int_cell('blt', 8)
        bldd = get_int_cell('blt_dd', 9)
        lain = get_int_cell('lainnya', 10)
        tot = pkh + bpnt + bos + bap + stun + pbi + blt + bldd + lain

        parsed_records.append({
            'no_urut': no_val,
            'nama_sls': sls_str,
            'pkh': pkh,
            'bpnt': bpnt,
            'bos': bos,
            'bapanas': bap,
            'stunting': stun,
            'pbi_jkn': pbi,
            'blt': blt,
            'blt_dd': bldd,
            'lainnya': lain,
            'total': tot
        })

    if not parsed_records:
        return None, "Tidak ada data baris bantuan sosial SLS yang valid ditemukan dalam file."

    return parsed_records, None


# ==============================================================================
# 11. HELPER STATUS KEBERADAAN ORANG TUA ANAK (ANAK YATIM/PIATU) PER SLS (RT/RW)
# ==============================================================================

ANAK_COLUMNS = [
    "No.", "Nama SLS", "Anak Yatim", "Anak Piatu", "Yatim Piatu", "Orang Tua Lengkap", "Total Anak"
]

SAMPLE_SLS_LIST = [
    'RT 001 RW 001', 'RT 002 RW 001', 'RT 003 RW 001', 'RT 004 RW 001', 'RT 005 RW 001',
    'RT 001 RW 002', 'RT 002 RW 002', 'RT 003 RW 002', 'RT 004 RW 002',
    'RT 001 RW 003', 'RT 002 RW 003',
    'RT 001 RW 004', 'RT 002 RW 004', 'RT 003 RW 004',
    'RT 001 RW 005', 'RT 002 RW 005', 'RT 003 RW 005', 'RT 004 RW 005',
    'RT 001 RW 006', 'RT 002 RW 006', 'RT 003 RW 006',
    'RT 001 RW 007', 'RT 002 RW 007',
    'RT 001 RW 008', 'RT 002 RW 008', 'RT 003 RW 008'
]


def generate_template_anak_excel(include_sample=True):
    """Menghasilkan file template Excel (.xlsx) data status orang tua anak per SLS"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Status Anak SLS"

    header_fill = PatternFill(start_color="E67E22", end_color="E67E22", fill_type="solid")
    total_header_fill = PatternFill(start_color="D35400", end_color="D35400", fill_type="solid")
    footer_fill = PatternFill(start_color="F39C12", end_color="F39C12", fill_type="solid")

    header_font = Font(name="Segoe UI", size=10, bold=True, color="000000")
    total_header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    data_font = Font(name="Segoe UI", size=10)
    footer_font = Font(name="Segoe UI", size=10, bold=True, color="000000")

    thin_border = Border(
        left=Side(style='thin', color='D0D7DE'),
        right=Side(style='thin', color='D0D7DE'),
        top=Side(style='thin', color='D0D7DE'),
        bottom=Side(style='thin', color='D0D7DE')
    )

    ws.append(ANAK_COLUMNS)
    ws.row_dimensions[1].height = 26

    for col_idx in range(1, len(ANAK_COLUMNS) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = total_header_fill if col_idx == 7 else header_fill
        cell.font = total_header_font if col_idx == 7 else header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    current_row = 2
    for idx, sls in enumerate(SAMPLE_SLS_LIST, 1):
        ws.append([idx, sls, 0, 0, 0, 0, f"=SUM(C{current_row}:F{current_row})"])
        ws.row_dimensions[current_row].height = 20

        for col_idx in range(1, 8):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx == 1:
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif col_idx == 2:
                cell.alignment = Alignment(horizontal='left', vertical='center')
            elif col_idx == 7:
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.font = Font(name="Segoe UI", size=10, bold=True, color="8A3B00")
            else:
                cell.alignment = Alignment(horizontal='center', vertical='center')
        current_row += 1

    last_data_row = current_row - 1
    ws.append([
        "TOTAL", "",
        f"=SUM(C2:C{last_data_row})",
        f"=SUM(D2:D{last_data_row})",
        f"=SUM(E2:E{last_data_row})",
        f"=SUM(F2:F{last_data_row})",
        f"=SUM(G2:G{last_data_row})"
    ])
    ws.row_dimensions[current_row].height = 24

    for col_idx in range(1, 8):
        cell = ws.cell(row=current_row, column=col_idx)
        cell.fill = footer_fill
        cell.font = footer_font
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='center', vertical='center')

    note_row = current_row + 2
    ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=7)
    note_cell = ws.cell(row=note_row, column=1)
    note_cell.value = "* Keterangan: Istilah anak yatim, piatu, dan yatim piatu mencakup anak usia <= 15 tahun (0 - 15 tahun)."
    note_cell.font = Font(name="Segoe UI", size=9, italic=True, color="555555")

    col_widths = {1: 8, 2: 20, 3: 14, 4: 14, 5: 14, 6: 20, 7: 14}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    mem = io.BytesIO()
    wb.save(mem)
    mem.seek(0)
    return mem


def generate_template_anak_csv(include_sample=True):
    """Menghasilkan file template CSV (.csv) data status orang tua anak per SLS"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(ANAK_COLUMNS)

    for idx, sls in enumerate(SAMPLE_SLS_LIST, 1):
        writer.writerow([idx, sls, 0, 0, 0, 0, 0])

    writer.writerow([])
    writer.writerow(["* Keterangan: Istilah anak yatim, piatu, dan yatim piatu mencakup anak usia <= 15 tahun (0 - 15 tahun)."])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def export_anak_excel(rows, tahun=2026):
    """Mengekspor data statistik orang tua anak per SLS ke file Excel (.xlsx)"""
    wb = Workbook()
    ws = wb.active
    ws.title = f"Status Anak {tahun}"

    header_fill = PatternFill(start_color="E67E22", end_color="E67E22", fill_type="solid")
    total_header_fill = PatternFill(start_color="D35400", end_color="D35400", fill_type="solid")
    footer_fill = PatternFill(start_color="F39C12", end_color="F39C12", fill_type="solid")

    header_font = Font(name="Segoe UI", size=10, bold=True, color="000000")
    total_header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    data_font = Font(name="Segoe UI", size=10)
    footer_font = Font(name="Segoe UI", size=10, bold=True, color="000000")

    thin_border = Border(
        left=Side(style='thin', color='D0D7DE'),
        right=Side(style='thin', color='D0D7DE'),
        top=Side(style='thin', color='D0D7DE'),
        bottom=Side(style='thin', color='D0D7DE')
    )

    ws.append(ANAK_COLUMNS)
    ws.row_dimensions[1].height = 26

    for col_idx in range(1, len(ANAK_COLUMNS) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = total_header_fill if col_idx == 7 else header_fill
        cell.font = total_header_font if col_idx == 7 else header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    current_row = 2
    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        yt_val = r['anak_yatim'] if isinstance(r, dict) else r[4]
        pt_val = r['anak_piatu'] if isinstance(r, dict) else r[5]
        yp_val = r['yatim_piatu'] if isinstance(r, dict) else r[6]
        ot_val = r['orang_tua_lengkap'] if isinstance(r, dict) else r[7]

        ws.append([no_val, sls_val, yt_val, pt_val, yp_val, ot_val, f"=SUM(C{current_row}:F{current_row})"])
        ws.row_dimensions[current_row].height = 20

        for col_idx in range(1, 8):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx == 1:
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif col_idx == 2:
                cell.alignment = Alignment(horizontal='left', vertical='center')
            elif col_idx == 7:
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.font = Font(name="Segoe UI", size=10, bold=True, color="8A3B00")
            else:
                cell.alignment = Alignment(horizontal='center', vertical='center')
        current_row += 1

    last_data_row = current_row - 1
    if rows:
        ws.append([
            "TOTAL", "",
            f"=SUM(C2:C{last_data_row})",
            f"=SUM(D2:D{last_data_row})",
            f"=SUM(E2:E{last_data_row})",
            f"=SUM(F2:F{last_data_row})",
            f"=SUM(G2:G{last_data_row})"
        ])
    else:
        ws.append(["TOTAL", "", 0, 0, 0, 0, 0])

    ws.row_dimensions[current_row].height = 24
    for col_idx in range(1, 8):
        cell = ws.cell(row=current_row, column=col_idx)
        cell.fill = footer_fill
        cell.font = footer_font
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='center', vertical='center')

    note_row = current_row + 2
    ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=7)
    note_cell = ws.cell(row=note_row, column=1)
    note_cell.value = "* Keterangan: Istilah anak yatim, piatu, dan yatim piatu mencakup anak usia <= 15 tahun (0 - 15 tahun)."
    note_cell.font = Font(name="Segoe UI", size=9, italic=True, color="555555")

    col_widths = {1: 8, 2: 20, 3: 14, 4: 14, 5: 14, 6: 20, 7: 14}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    mem = io.BytesIO()
    wb.save(mem)
    mem.seek(0)
    return mem


def export_anak_csv(rows, tahun=2026):
    """Mengekspor data statistik orang tua anak per SLS ke file CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(ANAK_COLUMNS)

    tot_yt, tot_pt, tot_yp, tot_ot, tot_all = 0, 0, 0, 0, 0
    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        yt_val = r['anak_yatim'] if isinstance(r, dict) else r[4]
        pt_val = r['anak_piatu'] if isinstance(r, dict) else r[5]
        yp_val = r['yatim_piatu'] if isinstance(r, dict) else r[6]
        ot_val = r['orang_tua_lengkap'] if isinstance(r, dict) else r[7]
        row_tot = yt_val + pt_val + yp_val + ot_val

        writer.writerow([no_val, sls_val, yt_val, pt_val, yp_val, ot_val, row_tot])
        tot_yt += yt_val
        tot_pt += pt_val
        tot_yp += yp_val
        tot_ot += ot_val
        tot_all += row_tot

    writer.writerow(["TOTAL", "", tot_yt, tot_pt, tot_yp, tot_ot, tot_all])
    writer.writerow([])
    writer.writerow(["* Keterangan: Istilah anak yatim, piatu, dan yatim piatu mencakup anak usia <= 15 tahun (0 - 15 tahun)."])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def parse_uploaded_anak_file(file_storage):
    """Mem-parsing file Excel/CSV data status orang tua anak per SLS"""
    filename = file_storage.filename.lower()
    raw_rows = []

    if filename.endswith('.csv'):
        try:
            content = file_storage.read().decode('utf-8-sig', errors='replace')
            reader = csv.reader(io.StringIO(content))
            for row in reader:
                raw_rows.append(row)
        except Exception as e:
            return None, f"Gagal membaca file CSV: {str(e)}"
    elif filename.endswith(('.xlsx', '.xls')):
        try:
            wb = load_workbook(filename=file_storage, data_only=True)
            ws = wb.active
            for row in ws.iter_rows(values_only=True):
                raw_rows.append(list(row))
        except Exception as e:
            return None, f"Gagal membaca file Excel: {str(e)}"
    else:
        return None, "Format file tidak didukung. Harap unggah file .xlsx atau .csv."

    clean_rows = []
    for r in raw_rows:
        if r and any(cell is not None and str(cell).strip() != '' for cell in r):
            clean_rows.append([str(c).strip() if c is not None else '' for c in r])

    if len(clean_rows) < 2:
        return None, "File spreadsheet tidak memuat data yang cukup."

    header_row = clean_rows[0]
    col_map = {}

    def norm_h(text):
        return re.sub(r'[^a-z0-9]', '', str(text).lower())

    for c_idx, h_text in enumerate(header_row):
        h_norm = norm_h(h_text)
        if h_norm in ['no', 'nourut', 'nomor']:
            col_map['no_urut'] = c_idx
        elif any(k in h_norm for k in ['namasls', 'sls', 'wilayah', 'rt', 'rtrw']):
            col_map['nama_sls'] = c_idx
        elif 'yatimpiatu' in h_norm:
            col_map['yatim_piatu'] = c_idx
        elif 'nakapiatu' in h_norm or 'anakpiatu' in h_norm or h_norm == 'piatu':
            col_map['anak_piatu'] = c_idx
        elif 'anakyatim' in h_norm or h_norm == 'yatim':
            col_map['anak_yatim'] = c_idx
        elif 'lengkap' in h_norm or 'orangtua' in h_norm:
            col_map['orang_tua_lengkap'] = c_idx
        elif any(k in h_norm for k in ['total', 'jumlah']):
            col_map['total'] = c_idx

    parsed_records = []
    for r_idx in range(1, len(clean_rows)):
        row = clean_rows[r_idx]
        sls_idx = col_map.get('nama_sls', 1)
        sls_str = row[sls_idx].strip() if sls_idx < len(row) else ''
        first_cell = row[0].strip() if len(row) > 0 else ''

        if not sls_str or sls_str.upper() in ['TOTAL', 'T O T A L', 'JUMLAH', 'REKAPITULASI'] or sls_str.startswith('*') or sls_str.lower().startswith(('catatan', 'keterangan')):
            continue
        if first_cell.startswith('*') or first_cell.lower().startswith(('catatan', 'keterangan')):
            continue

        no_idx = col_map.get('no_urut', 0)
        try:
            no_val = int(float(str(row[no_idx] or 0))) if no_idx < len(row) else len(parsed_records) + 1
        except:
            no_val = len(parsed_records) + 1

        def get_int_cell(key, default_idx):
            idx = col_map.get(key, default_idx)
            if idx < len(row):
                try:
                    return max(0, int(float(str(row[idx] or 0))))
                except:
                    return 0
            return 0

        ay = get_int_cell('anak_yatim', 2)
        ap = get_int_cell('anak_piatu', 3)
        yp = get_int_cell('yatim_piatu', 4)
        ot = get_int_cell('orang_tua_lengkap', 5)
        tot = ay + ap + yp + ot

        parsed_records.append({
            'no_urut': no_val,
            'nama_sls': sls_str,
            'anak_yatim': ay,
            'anak_piatu': ap,
            'yatim_piatu': yp,
            'orang_tua_lengkap': ot,
            'total_anak': tot
        })

    if not parsed_records:
        return None, "Tidak ada data baris status anak SLS yang valid ditemukan dalam file."

    return parsed_records, None


# ==============================================================================
# 12. HELPER ANAK GIZI BURUK PER SLS (RT/RW)
# ==============================================================================

GIZI_BURUK_COLUMNS = ["No.", "Nama SLS", "Anak Gizi Buruk", "Jumlah Anak <=5 tahun", "Persentase"]


def generate_template_gizi_buruk_excel(include_sample=True):
    """Menghasilkan file template Excel (.xlsx) data anak gizi buruk per SLS"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Gizi Buruk SLS"

    header_fill = PatternFill(start_color="E67E22", end_color="E67E22", fill_type="solid")
    footer_fill = PatternFill(start_color="F39C12", end_color="F39C12", fill_type="solid")

    header_font = Font(name="Segoe UI", size=10, bold=True, color="000000")
    data_font = Font(name="Segoe UI", size=10)
    footer_font = Font(name="Segoe UI", size=10, bold=True, color="000000")

    thin_border = Border(
        left=Side(style='thin', color='D0D7DE'),
        right=Side(style='thin', color='D0D7DE'),
        top=Side(style='thin', color='D0D7DE'),
        bottom=Side(style='thin', color='D0D7DE')
    )

    ws.append(GIZI_BURUK_COLUMNS)
    ws.row_dimensions[1].height = 26

    for col_idx in range(1, len(GIZI_BURUK_COLUMNS) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    current_row = 2
    for idx, sls in enumerate(SAMPLE_SLS_LIST, 1):
        gb_val = 1 if include_sample else 0
        balita_val = 10 if include_sample else 0
        ws.append([idx, sls, gb_val, balita_val, f"=IF(D{current_row}>0, (C{current_row}/D{current_row})*100, 0)"])
        ws.row_dimensions[current_row].height = 20

        for col_idx in range(1, 6):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx == 1:
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif col_idx == 2:
                cell.alignment = Alignment(horizontal='left', vertical='center')
            elif col_idx == 5:
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.font = Font(name="Segoe UI", size=10, bold=True, color="000000")
            else:
                cell.alignment = Alignment(horizontal='center', vertical='center')
        current_row += 1

    last_data_row = current_row - 1
    ws.append([
        "TOTAL", "",
        f"=SUM(C2:C{last_data_row})",
        f"=SUM(D2:D{last_data_row})",
        f"=IF(D{current_row}>0, (C{current_row}/D{current_row})*100, 0)"
    ])
    ws.row_dimensions[current_row].height = 24

    for col_idx in range(1, 6):
        cell = ws.cell(row=current_row, column=col_idx)
        cell.fill = footer_fill
        cell.font = footer_font
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='center', vertical='center')

    note_row = current_row + 2
    ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=5)
    note_cell = ws.cell(row=note_row, column=1)
    note_cell.value = "* Keterangan: Pemantauan anak gizi buruk mencakup anak balita usia <= 5 tahun (0 - 5 tahun)."
    note_cell.font = Font(name="Segoe UI", size=9, italic=True, color="555555")

    col_widths = {1: 8, 2: 24, 3: 20, 4: 24, 5: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    mem = io.BytesIO()
    wb.save(mem)
    mem.seek(0)
    return mem


def generate_template_gizi_buruk_csv(include_sample=True):
    """Menghasilkan file template CSV (.csv) data anak gizi buruk per SLS"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(GIZI_BURUK_COLUMNS)

    for idx, sls in enumerate(SAMPLE_SLS_LIST, 1):
        gb_val = 1 if include_sample else 0
        balita_val = 10 if include_sample else 0
        persen_val = 10 if include_sample else 0
        writer.writerow([idx, sls, gb_val, balita_val, persen_val])

    if include_sample:
        writer.writerow(["TOTAL", "", 26, 260, 10])
    else:
        writer.writerow(["TOTAL", "", 0, 0, 0])

    writer.writerow([])
    writer.writerow(["* Keterangan: Pemantauan anak gizi buruk mencakup anak balita usia <= 5 tahun (0 - 5 tahun)."])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def export_gizi_buruk_excel(rows, tahun=2026):
    """Mengekspor data statistik anak gizi buruk per SLS ke file Excel (.xlsx)"""
    wb = Workbook()
    ws = wb.active
    ws.title = f"Gizi Buruk {tahun}"

    header_fill = PatternFill(start_color="E67E22", end_color="E67E22", fill_type="solid")
    footer_fill = PatternFill(start_color="F39C12", end_color="F39C12", fill_type="solid")

    header_font = Font(name="Segoe UI", size=10, bold=True, color="000000")
    data_font = Font(name="Segoe UI", size=10)
    footer_font = Font(name="Segoe UI", size=10, bold=True, color="000000")

    thin_border = Border(
        left=Side(style='thin', color='D0D7DE'),
        right=Side(style='thin', color='D0D7DE'),
        top=Side(style='thin', color='D0D7DE'),
        bottom=Side(style='thin', color='D0D7DE')
    )

    ws.append(GIZI_BURUK_COLUMNS)
    ws.row_dimensions[1].height = 26

    for col_idx in range(1, len(GIZI_BURUK_COLUMNS) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    current_row = 2
    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        gb_val = r['anak_gizi_buruk'] if isinstance(r, dict) else r[4]
        balita_val = r.get('jumlah_anak_balita', 0) if isinstance(r, dict) else (r[6] if len(r) > 6 else 0)

        ws.append([no_val, sls_val, gb_val, balita_val, f"=IF(D{current_row}>0, (C{current_row}/D{current_row})*100, 0)"])
        ws.row_dimensions[current_row].height = 20

        for col_idx in range(1, 6):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx == 1:
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif col_idx == 2:
                cell.alignment = Alignment(horizontal='left', vertical='center')
            elif col_idx == 5:
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.font = Font(name="Segoe UI", size=10, bold=True, color="000000")
            else:
                cell.alignment = Alignment(horizontal='center', vertical='center')
        current_row += 1

    last_data_row = current_row - 1
    if rows:
        ws.append([
            "TOTAL", "",
            f"=SUM(C2:C{last_data_row})",
            f"=SUM(D2:D{last_data_row})",
            f"=IF(D{current_row}>0, (C{current_row}/D{current_row})*100, 0)"
        ])
    else:
        ws.append(["TOTAL", "", 0, 0, 0])

    ws.row_dimensions[current_row].height = 24
    for col_idx in range(1, 6):
        cell = ws.cell(row=current_row, column=col_idx)
        cell.fill = footer_fill
        cell.font = footer_font
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='center', vertical='center')

    note_row = current_row + 2
    ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=5)
    note_cell = ws.cell(row=note_row, column=1)
    note_cell.value = "* Keterangan: Pemantauan anak gizi buruk mencakup anak balita usia <= 5 tahun (0 - 5 tahun)."
    note_cell.font = Font(name="Segoe UI", size=9, italic=True, color="555555")

    col_widths = {1: 8, 2: 24, 3: 20, 4: 24, 5: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    mem = io.BytesIO()
    wb.save(mem)
    mem.seek(0)
    return mem


def export_gizi_buruk_csv(rows, tahun=2026):
    """Mengekspor data statistik anak gizi buruk per SLS ke file CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(GIZI_BURUK_COLUMNS)

    tot_gb = 0
    tot_balita = 0
    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        gb_val = r['anak_gizi_buruk'] if isinstance(r, dict) else r[4]
        balita_val = r.get('jumlah_anak_balita', 0) if isinstance(r, dict) else (r[6] if len(r) > 6 else 0)
        persen_val = round((gb_val / balita_val * 100), 2) if balita_val > 0 else 0.0

        writer.writerow([no_val, sls_val, gb_val, balita_val, persen_val])
        tot_gb += gb_val
        tot_balita += balita_val

    tot_persen = round((tot_gb / tot_balita * 100), 2) if tot_balita > 0 else 0.0
    writer.writerow(["TOTAL", "", tot_gb, tot_balita, tot_persen])
    writer.writerow([])
    writer.writerow(["* Keterangan: Pemantauan anak gizi buruk mencakup anak balita usia <= 5 tahun (0 - 5 tahun)."])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def parse_uploaded_gizi_buruk_file(file_storage):
    """Mem-parsing file Excel/CSV data anak gizi buruk per SLS"""
    filename = file_storage.filename.lower()
    raw_rows = []

    if filename.endswith('.csv'):
        try:
            content = file_storage.read().decode('utf-8-sig', errors='replace')
            reader = csv.reader(io.StringIO(content))
            for row in reader:
                raw_rows.append(row)
        except Exception as e:
            return None, f"Gagal membaca file CSV: {str(e)}"
    elif filename.endswith(('.xlsx', '.xls')):
        try:
            wb = load_workbook(filename=file_storage, data_only=True)
            ws = wb.active
            for row in ws.iter_rows(values_only=True):
                raw_rows.append(list(row))
        except Exception as e:
            return None, f"Gagal membaca file Excel: {str(e)}"
    else:
        return None, "Format file tidak didukung. Harap unggah file .xlsx atau .csv."

    clean_rows = []
    for r in raw_rows:
        if r and any(cell is not None and str(cell).strip() != '' for cell in r):
            clean_rows.append([str(c).strip() if c is not None else '' for c in r])

    if len(clean_rows) < 2:
        return None, "File spreadsheet tidak memuat data yang cukup."

    header_row = clean_rows[0]
    col_map = {}

    def norm_h(text):
        return re.sub(r'[^a-z0-9]', '', str(text).lower())

    for c_idx, h_text in enumerate(header_row):
        h_norm = norm_h(h_text)
        if h_norm in ['no', 'nourut', 'nomor']:
            col_map['no_urut'] = c_idx
        elif any(k in h_norm for k in ['namasls', 'sls', 'wilayah', 'rt', 'rtrw']):
            col_map['nama_sls'] = c_idx
        elif any(k in h_norm for k in ['giziburuk', 'gizi', 'buruk']):
            col_map['anak_gizi_buruk'] = c_idx
        elif any(k in h_norm for k in ['jumlahanak', '5tahun', 'balita', 'anak5', '5thn']):
            col_map['jumlah_anak_balita'] = c_idx
        elif any(k in h_norm for k in ['persen', 'persentase', '%']):
            col_map['persentase'] = c_idx

    parsed_records = []
    for r_idx in range(1, len(clean_rows)):
        row = clean_rows[r_idx]
        sls_idx = col_map.get('nama_sls', 1)
        sls_str = row[sls_idx].strip() if sls_idx < len(row) else ''
        first_cell = row[0].strip() if len(row) > 0 else ''

        if not sls_str or sls_str.upper() in ['TOTAL', 'T O T A L', 'JUMLAH', 'REKAPITULASI'] or sls_str.startswith('*') or sls_str.lower().startswith(('catatan', 'keterangan')):
            continue
        if first_cell.startswith('*') or first_cell.lower().startswith(('catatan', 'keterangan')):
            continue

        no_idx = col_map.get('no_urut', 0)
        try:
            no_val = int(float(str(row[no_idx] or 0))) if no_idx < len(row) else len(parsed_records) + 1
        except:
            no_val = len(parsed_records) + 1

        gb_idx = col_map.get('anak_gizi_buruk', 2)
        try:
            gb_val = max(0, int(float(str(row[gb_idx] or 0)))) if gb_idx < len(row) else 0
        except:
            gb_val = 0

        balita_idx = col_map.get('jumlah_anak_balita', 3)
        try:
            balita_val = max(0, int(float(str(row[balita_idx] or 0)))) if balita_idx < len(row) else 0
        except:
            balita_val = 0

        persen_idx = col_map.get('persentase', 4)
        try:
            if persen_idx < len(row) and str(row[persen_idx]).strip() != '':
                raw_p = str(row[persen_idx]).replace('%', '').strip()
                persen_val = round(float(raw_p), 2)
            else:
                persen_val = round((gb_val / balita_val * 100), 2) if balita_val > 0 else 0.0
        except:
            persen_val = round((gb_val / balita_val * 100), 2) if balita_val > 0 else 0.0

        parsed_records.append({
            'no_urut': no_val,
            'nama_sls': sls_str,
            'anak_gizi_buruk': gb_val,
            'jumlah_anak_balita': balita_val,
            'persentase': persen_val
        })

    if not parsed_records:
        return None, "Tidak ada data baris gizi buruk SLS yang valid ditemukan dalam file."

    return parsed_records, None


# ==============================================================================
# 13. HELPER ANAK STUNTING PER SLS (RT/RW)
# ==============================================================================

STUNTING_COLUMNS = ["No.", "Nama SLS", "Anak Stunting", "Jumlah Anak <=5 tahun", "Persentase"]


def generate_template_stunting_excel(include_sample=True):
    """Menghasilkan file template Excel (.xlsx) data anak stunting per SLS"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Stunting SLS"

    header_fill = PatternFill(start_color="E67E22", end_color="E67E22", fill_type="solid")
    footer_fill = PatternFill(start_color="F39C12", end_color="F39C12", fill_type="solid")

    header_font = Font(name="Segoe UI", size=10, bold=True, color="000000")
    data_font = Font(name="Segoe UI", size=10)
    footer_font = Font(name="Segoe UI", size=10, bold=True, color="000000")

    thin_border = Border(
        left=Side(style='thin', color='D0D7DE'),
        right=Side(style='thin', color='D0D7DE'),
        top=Side(style='thin', color='D0D7DE'),
        bottom=Side(style='thin', color='D0D7DE')
    )

    ws.append(STUNTING_COLUMNS)
    ws.row_dimensions[1].height = 26

    for col_idx in range(1, len(STUNTING_COLUMNS) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    current_row = 2
    for idx, sls in enumerate(SAMPLE_SLS_LIST, 1):
        st_val = 1 if include_sample else 0
        balita_val = 10 if include_sample else 0
        ws.append([idx, sls, st_val, balita_val, f"=IF(D{current_row}>0, (C{current_row}/D{current_row})*100, 0)"])
        ws.row_dimensions[current_row].height = 20

        for col_idx in range(1, 6):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx == 1:
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif col_idx == 2:
                cell.alignment = Alignment(horizontal='left', vertical='center')
            elif col_idx == 5:
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.font = Font(name="Segoe UI", size=10, bold=True, color="000000")
            else:
                cell.alignment = Alignment(horizontal='center', vertical='center')
        current_row += 1

    last_data_row = current_row - 1
    ws.append([
        "TOTAL", "",
        f"=SUM(C2:C{last_data_row})",
        f"=SUM(D2:D{last_data_row})",
        f"=IF(D{current_row}>0, (C{current_row}/D{current_row})*100, 0)"
    ])
    ws.row_dimensions[current_row].height = 24

    for col_idx in range(1, 6):
        cell = ws.cell(row=current_row, column=col_idx)
        cell.fill = footer_fill
        cell.font = footer_font
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='center', vertical='center')

    note_row = current_row + 2
    ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=5)
    note_cell = ws.cell(row=note_row, column=1)
    note_cell.value = "* Keterangan: Pemantauan anak stunting mencakup anak balita usia <= 5 tahun (0 - 5 tahun)."
    note_cell.font = Font(name="Segoe UI", size=9, italic=True, color="555555")

    col_widths = {1: 8, 2: 24, 3: 20, 4: 24, 5: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    mem = io.BytesIO()
    wb.save(mem)
    mem.seek(0)
    return mem


def generate_template_stunting_csv(include_sample=True):
    """Menghasilkan file template CSV (.csv) data anak stunting per SLS"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(STUNTING_COLUMNS)

    for idx, sls in enumerate(SAMPLE_SLS_LIST, 1):
        st_val = 1 if include_sample else 0
        balita_val = 10 if include_sample else 0
        persen_val = 10 if include_sample else 0
        writer.writerow([idx, sls, st_val, balita_val, persen_val])

    if include_sample:
        writer.writerow(["TOTAL", "", 26, 260, 10])
    else:
        writer.writerow(["TOTAL", "", 0, 0, 0])

    writer.writerow([])
    writer.writerow(["* Keterangan: Pemantauan anak stunting mencakup anak balita usia <= 5 tahun (0 - 5 tahun)."])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def export_stunting_excel(rows, tahun=2026):
    """Mengekspor data statistik anak stunting per SLS ke file Excel (.xlsx)"""
    wb = Workbook()
    ws = wb.active
    ws.title = f"Stunting {tahun}"

    header_fill = PatternFill(start_color="E67E22", end_color="E67E22", fill_type="solid")
    footer_fill = PatternFill(start_color="F39C12", end_color="F39C12", fill_type="solid")

    header_font = Font(name="Segoe UI", size=10, bold=True, color="000000")
    data_font = Font(name="Segoe UI", size=10)
    footer_font = Font(name="Segoe UI", size=10, bold=True, color="000000")

    thin_border = Border(
        left=Side(style='thin', color='D0D7DE'),
        right=Side(style='thin', color='D0D7DE'),
        top=Side(style='thin', color='D0D7DE'),
        bottom=Side(style='thin', color='D0D7DE')
    )

    ws.append(STUNTING_COLUMNS)
    ws.row_dimensions[1].height = 26

    for col_idx in range(1, len(STUNTING_COLUMNS) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    current_row = 2
    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        st_val = r['anak_stunting'] if isinstance(r, dict) else r[4]
        balita_val = r.get('jumlah_anak_balita', 0) if isinstance(r, dict) else (r[6] if len(r) > 6 else 0)

        ws.append([no_val, sls_val, st_val, balita_val, f"=IF(D{current_row}>0, (C{current_row}/D{current_row})*100, 0)"])
        ws.row_dimensions[current_row].height = 20

        for col_idx in range(1, 6):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx == 1:
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif col_idx == 2:
                cell.alignment = Alignment(horizontal='left', vertical='center')
            elif col_idx == 5:
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.font = Font(name="Segoe UI", size=10, bold=True, color="000000")
            else:
                cell.alignment = Alignment(horizontal='center', vertical='center')
        current_row += 1

    last_data_row = current_row - 1
    if rows:
        ws.append([
            "TOTAL", "",
            f"=SUM(C2:C{last_data_row})",
            f"=SUM(D2:D{last_data_row})",
            f"=IF(D{current_row}>0, (C{current_row}/D{current_row})*100, 0)"
        ])
    else:
        ws.append(["TOTAL", "", 0, 0, 0])

    ws.row_dimensions[current_row].height = 24
    for col_idx in range(1, 6):
        cell = ws.cell(row=current_row, column=col_idx)
        cell.fill = footer_fill
        cell.font = footer_font
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='center', vertical='center')

    note_row = current_row + 2
    ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=5)
    note_cell = ws.cell(row=note_row, column=1)
    note_cell.value = "* Keterangan: Pemantauan anak stunting mencakup anak balita usia <= 5 tahun (0 - 5 tahun)."
    note_cell.font = Font(name="Segoe UI", size=9, italic=True, color="555555")

    col_widths = {1: 8, 2: 24, 3: 20, 4: 24, 5: 16}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    mem = io.BytesIO()
    wb.save(mem)
    mem.seek(0)
    return mem


def export_stunting_csv(rows, tahun=2026):
    """Mengekspor data statistik anak stunting per SLS ke file CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(STUNTING_COLUMNS)

    tot_st = 0
    tot_balita = 0
    for r in rows:
        no_val = r['no_urut'] if isinstance(r, dict) else r[2]
        sls_val = r['nama_sls'] if isinstance(r, dict) else r[3]
        st_val = r['anak_stunting'] if isinstance(r, dict) else r[4]
        balita_val = r.get('jumlah_anak_balita', 0) if isinstance(r, dict) else (r[6] if len(r) > 6 else 0)
        persen_val = round((st_val / balita_val * 100), 2) if balita_val > 0 else 0.0

        writer.writerow([no_val, sls_val, st_val, balita_val, persen_val])
        tot_st += st_val
        tot_balita += balita_val

    tot_persen = round((tot_st / tot_balita * 100), 2) if tot_balita > 0 else 0.0
    writer.writerow(["TOTAL", "", tot_st, tot_balita, tot_persen])
    writer.writerow([])
    writer.writerow(["* Keterangan: Pemantauan anak stunting mencakup anak balita usia <= 5 tahun (0 - 5 tahun)."])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    return mem


def parse_uploaded_stunting_file(file_storage):
    """Mem-parsing file Excel/CSV data anak stunting per SLS"""
    filename = file_storage.filename.lower()
    raw_rows = []

    if filename.endswith('.csv'):
        try:
            content = file_storage.read().decode('utf-8-sig', errors='replace')
            reader = csv.reader(io.StringIO(content))
            for row in reader:
                raw_rows.append(row)
        except Exception as e:
            return None, f"Gagal membaca file CSV: {str(e)}"
    elif filename.endswith(('.xlsx', '.xls')):
        try:
            wb = load_workbook(filename=file_storage, data_only=True)
            ws = wb.active
            for row in ws.iter_rows(values_only=True):
                raw_rows.append(list(row))
        except Exception as e:
            return None, f"Gagal membaca file Excel: {str(e)}"
    else:
        return None, "Format file tidak didukung. Harap unggah file .xlsx atau .csv."

    clean_rows = []
    for r in raw_rows:
        if r and any(cell is not None and str(cell).strip() != '' for cell in r):
            clean_rows.append([str(c).strip() if c is not None else '' for c in r])

    if len(clean_rows) < 2:
        return None, "File spreadsheet tidak memuat data yang cukup."

    header_row = clean_rows[0]
    col_map = {}

    def norm_h(text):
        return re.sub(r'[^a-z0-9]', '', str(text).lower())

    for c_idx, h_text in enumerate(header_row):
        h_norm = norm_h(h_text)
        if h_norm in ['no', 'nourut', 'nomor']:
            col_map['no_urut'] = c_idx
        elif any(k in h_norm for k in ['namasls', 'sls', 'wilayah', 'rt', 'rtrw']):
            col_map['nama_sls'] = c_idx
        elif 'stunting' in h_norm:
            col_map['anak_stunting'] = c_idx
        elif any(k in h_norm for k in ['jumlahanak', '5tahun', 'balita', 'anak5', '5thn']):
            col_map['jumlah_anak_balita'] = c_idx
        elif any(k in h_norm for k in ['persen', 'persentase', '%']):
            col_map['persentase'] = c_idx

    parsed_records = []
    for r_idx in range(1, len(clean_rows)):
        row = clean_rows[r_idx]
        sls_idx = col_map.get('nama_sls', 1)
        sls_str = row[sls_idx].strip() if sls_idx < len(row) else ''
        first_cell = row[0].strip() if len(row) > 0 else ''

        if not sls_str or sls_str.upper() in ['TOTAL', 'T O T A L', 'JUMLAH', 'REKAPITULASI'] or sls_str.startswith('*') or sls_str.lower().startswith(('catatan', 'keterangan')):
            continue
        if first_cell.startswith('*') or first_cell.lower().startswith(('catatan', 'keterangan')):
            continue

        no_idx = col_map.get('no_urut', 0)
        try:
            no_val = int(float(str(row[no_idx] or 0))) if no_idx < len(row) else len(parsed_records) + 1
        except:
            no_val = len(parsed_records) + 1

        st_idx = col_map.get('anak_stunting', 2)
        try:
            st_val = max(0, int(float(str(row[st_idx] or 0)))) if st_idx < len(row) else 0
        except:
            st_val = 0

        balita_idx = col_map.get('jumlah_anak_balita', 3)
        try:
            balita_val = max(0, int(float(str(row[balita_idx] or 0)))) if balita_idx < len(row) else 0
        except:
            balita_val = 0

        persen_idx = col_map.get('persentase', 4)
        try:
            if persen_idx < len(row) and str(row[persen_idx]).strip() != '':
                raw_p = str(row[persen_idx]).replace('%', '').strip()
                persen_val = round(float(raw_p), 2)
            else:
                persen_val = round((st_val / balita_val * 100), 2) if balita_val > 0 else 0.0
        except:
            persen_val = round((st_val / balita_val * 100), 2) if balita_val > 0 else 0.0

        parsed_records.append({
            'no_urut': no_val,
            'nama_sls': sls_str,
            'anak_stunting': st_val,
            'jumlah_anak_balita': balita_val,
            'persentase': persen_val
        })

    if not parsed_records:
        return None, "Tidak ada data baris stunting SLS yang valid ditemukan dalam file."

    return parsed_records, None






