import os
import sys
import unittest
import io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app
from database import get_db

class TestUMKMAlamatWisataPattern(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_api_ajukan_umkm_with_lokasi(self):
        # Testing warga pengajuan UMKM with lokasi
        data = {
            'nama': 'Madu Asli Hutan Desa',
            'produsen': 'Kelompok Tani Lestari',
            'nik_pemilik': '3206012345670001',
            'harga': '85000',
            'satuan': 'Botol 500ml',
            'deskripsi': 'Madu murni dari hutan desa dengan kualitas premium.',
            'kontak_wa': '081234567899',
            'lokasi': 'RT 002 RW 003 Dusun Ranca Sari, Desa Papayan',
            'latitude': '-7.47000',
            'longitude': '108.20691'
        }
        res = self.client.post('/api/umkm/ajukan', data=data)
        self.assertEqual(res.status_code, 200)
        res_json = res.get_json()
        self.assertTrue(res_json.get('success'))

        # Check in DB
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nama, produsen, lokasi, alamat, latitude, longitude, status FROM umkm WHERE nama = ?", ('Madu Asli Hutan Desa',))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row['lokasi'], 'RT 002 RW 003 Dusun Ranca Sari, Desa Papayan')
        self.assertEqual(row['alamat'], 'RT 002 RW 003 Dusun Ranca Sari, Desa Papayan')
        self.assertAlmostEqual(row['latitude'], -7.47000, places=4)
        self.assertAlmostEqual(row['longitude'], 108.20691, places=4)
        self.assertEqual(row['status'], 'Menunggu Approval')
        print("[TEST 01 PASSED] Public ajukan UMKM with lokasi successfully saved!")

    def test_02_admin_tambah_umkm_with_lokasi(self):
        # Simulate admin session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'

        data = {
            'nama': 'Keripik Tempe Renyah Desa',
            'produsen': 'Ibu Ani Papayan',
            'harga': '15000',
            'satuan': 'Bungkus 200g',
            'deskripsi': 'Keripik tempe gurih rempah alami.',
            'kontak_wa': '082199887766',
            'lokasi': 'RT 001 RW 008 Dusun Munjul, Desa Papayan',
            'latitude': '-7.47584',
            'longitude': '108.20638'
        }
        res = self.client.post('/admin/umkm/tambah', data=data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Check DB
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama, lokasi, alamat, latitude, longitude, status FROM umkm WHERE nama = ?", ('Keripik Tempe Renyah Desa',))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row['lokasi'], 'RT 001 RW 008 Dusun Munjul, Desa Papayan')
        self.assertEqual(row['alamat'], 'RT 001 RW 008 Dusun Munjul, Desa Papayan')
        self.assertAlmostEqual(row['latitude'], -7.47584, places=4)
        self.assertAlmostEqual(row['longitude'], 108.20638, places=4)
        print("[TEST 02 PASSED] Admin tambah UMKM with lokasi successfully saved!")

        # Now test edit
        item_id = row['id']
        edit_data = {
            'nama': 'Keripik Tempe Renyah Desa (Pedas Manis)',
            'produsen': 'Ibu Ani Papayan Berkah',
            'harga': '18000',
            'satuan': 'Bungkus 250g',
            'deskripsi': 'Keripik tempe pedas manis gurih.',
            'kontak_wa': '082199887766',
            'lokasi': 'RT 003 RW 008 Dusun Munjul, Desa Papayan',
            'latitude': '-7.47935',
            'longitude': '108.20787'
        }
        res_edit = self.client.post(f'/admin/umkm/{item_id}/edit', data=edit_data, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nama, lokasi, alamat, latitude, longitude FROM umkm WHERE id = ?", (item_id,))
        updated_row = cursor.fetchone()
        conn.close()

        self.assertEqual(updated_row['nama'], 'Keripik Tempe Renyah Desa (Pedas Manis)')
        self.assertEqual(updated_row['lokasi'], 'RT 003 RW 008 Dusun Munjul, Desa Papayan')
        self.assertEqual(updated_row['alamat'], 'RT 003 RW 008 Dusun Munjul, Desa Papayan')
        self.assertAlmostEqual(updated_row['latitude'], -7.47935, places=4)
        self.assertAlmostEqual(updated_row['longitude'], 108.20787, places=4)
        print("[TEST 03 PASSED] Admin edit UMKM with lokasi successfully updated!")

if __name__ == '__main__':
    unittest.main()
