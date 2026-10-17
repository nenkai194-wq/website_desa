import os
import sys
import unittest
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app as application

class SecurityEngineTest(unittest.TestCase):
    def setUp(self):
        application.app.config['TESTING'] = True
        self.client = application.app.test_client()

    def test_01_security_headers_present(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get('X-Frame-Options'), 'SAMEORIGIN')
        self.assertEqual(res.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(res.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')
        self.assertIn('Content-Security-Policy', res.headers)
        print("PASS: Security headers present on public response")

    def test_02_admin_cache_control_headers(self):
        # Login first
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})
        res = self.client.get('/admin')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get('Cache-Control'), 'no-store, no-cache, must-revalidate, max-age=0')
        self.assertEqual(res.headers.get('Pragma'), 'no-cache')
        print("PASS: Anti-data leakage cache control headers present on /admin")

    def test_03_csrf_cross_site_rejection(self):
        # Simulating cross-site form submission attack
        res = self.client.post(
            '/admin/login',
            data={'username': 'admin', 'password': 'admin123'},
            headers={'Sec-Fetch-Site': 'cross-site'}
        )
        self.assertEqual(res.status_code, 403)
        print("PASS: Sec-Fetch-Site cross-site CSRF attempt successfully blocked (403)")

        # Simulating external Origin attack
        res = self.client.post(
            '/admin/login',
            data={'username': 'admin', 'password': 'admin123'},
            headers={'Origin': 'https://evil-hacker-site.com'}
        )
        self.assertEqual(res.status_code, 403)
        print("PASS: Cross-origin external Origin CSRF attempt successfully blocked (403)")

    def test_04_rate_limiting_public_form(self):
        # Exceeding 12 requests on /api/feedback/kirim
        blocked = False
        for i in range(15):
            res = self.client.post('/api/feedback/kirim', json={'bintang': 5, 'komentar': f'Test {i}'})
            if res.status_code == 429:
                blocked = True
                break
        self.assertTrue(blocked, "Rate limiter did not block excessive submissions")
        print("PASS: Public form submission spam rate limiter working (429 Too Many Requests)")

if __name__ == '__main__':
    unittest.main()
