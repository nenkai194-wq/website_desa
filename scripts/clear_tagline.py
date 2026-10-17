import sqlite3
conn = sqlite3.connect('desa.db')
cursor = conn.cursor()
cursor.execute("UPDATE profil_desa SET tagline_website = '', subtagline_website = '' WHERE id = 1")
conn.commit()
cursor.execute("SELECT id, nama_desa, judul_website, tagline_website, subtagline_website FROM profil_desa")
print(cursor.fetchone())
conn.close()
