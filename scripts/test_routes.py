import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app as application

class WebsiteDesaTest(unittest.TestCase):
    def setUp(self):
        application.app.config['TESTING'] = True
        self.client = application.app.test_client()

    def test_01_public_routes(self):
        public_urls = [
            '/',
            '/peta',
            '/publikasi',
            '/admin/login',
            '/api/pengaduan/kategori',
            '/api/statistik-kunjungan'
        ]
        for url in public_urls:
            with self.subTest(url=url):
                res = self.client.get(url)
                self.assertIn(res.status_code, [200, 302], f"Error accessing {url}: {res.status_code}")
                print(f"OK [Public GET]: {url} -> {res.status_code}")

    def test_02_admin_auth_and_management(self):
        # 1. Unauthenticated admin access should redirect to login
        res = self.client.get('/admin')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/admin/login', res.headers.get('Location', ''))
        print("OK: Unauthenticated access blocked and redirected to login")

        # 2. Login as Super Admin
        res = self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Dashboard', res.data)
        print("OK: Super Admin login succeeded")

        # 3. Check admin routes while authenticated
        admin_urls = [
            '/admin',
            '/admin/aparatur',
            '/admin/berita',
            '/admin/pengaduan',
            '/admin/surat',
            '/admin/umkm',
            '/admin/wisata',
            '/admin/users',
            '/admin/backup',
            '/admin/keamanan'
        ]
        for url in admin_urls:
            with self.subTest(url=url):
                res = self.client.get(url)
                self.assertEqual(res.status_code, 200, f"Failed accessing admin page {url}: {res.status_code}")
                print(f"OK [Admin GET]: {url} -> {res.status_code}")

        # 4. Logout
        res = self.client.get('/admin/logout', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        print("OK: Admin logout succeeded")

if __name__ == '__main__':
    unittest.main()
