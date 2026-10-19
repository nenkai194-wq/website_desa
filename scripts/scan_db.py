import sqlite3

conn = sqlite3.connect('desa.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall() if not r[0].startswith('sqlite_')]

keywords = ['kersik', 'marang kayu', 'kutai', 'makassar', 'selat', 'pesisir', 'tambak', 'nelayan', 'pantai', 'empang', 'proklim']

print("=== SCANNING DESA.DB FOR NON-PAPAYAN ARTIFACTS ===")
for table in tables:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = cursor.fetchall()
    text_cols = [c[1] for c in cols if 'CHAR' in c[2].upper() or 'TEXT' in c[2].upper() or 'CLOB' in c[2].upper() or c[2] == '']
    num_cols = [c[1] for c in cols if 'REAL' in c[2].upper() or 'INT' in c[2].upper() or 'FLOAT' in c[2].upper()]
    
    # Check text columns
    for col in text_cols:
        for kw in keywords:
            try:
                cursor.execute(f"SELECT id, {col} FROM {table} WHERE LOWER({col}) LIKE ?", (f"%{kw}%",))
                rows = cursor.fetchall()
                if rows:
                    print(f"[{table}.{col}] Keyword '{kw}': {len(rows)} rows")
                    for r in rows:
                        val_str = str(r[1])[:100].replace('\n', ' ')
                        print(f"   ID {r[0]}: {val_str}")
            except Exception as e:
                pass

    # Check coordinates in Kalimantan (lng > 115)
    for col in num_cols:
        if 'lng' in col.lower() or 'longitude' in col.lower():
            try:
                cursor.execute(f"SELECT id, {col} FROM {table} WHERE {col} > 115")
                rows = cursor.fetchall()
                if rows:
                    print(f"[{table}.{col}] Longitude in Kalimantan (>115): {rows}")
            except Exception:
                pass

print("=== SCAN FINISHED ===")
