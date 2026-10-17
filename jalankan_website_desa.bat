@echo off
title WEBSITE RESMI DESA - SISTEM INFORMASI & CMS
color 0A
echo ===================================================================
echo             PORTAL LAYANAN & WEBSITE RESMI DESA
echo             Dilengkapi Arsitektur Keamanan Siber Terpadu
echo ===================================================================
echo.
echo [ALAMAT AKSES WEBSITE]:
echo  - Frontend Publik (Komputer ini) : http://localhost:8080
echo  - Frontend Publik (Jaringan LAN) : http://192.168.2.105:8080
echo.
echo  - Backend CMS Admin (Lokal)      : http://localhost:8080/admin
echo  - Backend CMS Admin (LAN/WiFi)   : http://192.168.2.105:8080/admin
echo.
echo [KREDENSIAL LOGIN PANEL ADMIN]:
echo  - Super Admin : Username: admin    ^| Password: admin123
echo  - Staf/Admin  : Username: operator ^| Password: operator123
echo.
echo [STATUS KEAMANAN]:
echo  - Anti-CSRF Protection      : AKTIF
echo  - Anti-Brute Force / Rate   : AKTIF
echo  - HTTP Security Headers CSP : AKTIF
echo  - Proteksi Upload & Injeksi : AKTIF
echo ===================================================================
echo.
start http://localhost:8080
python app.py
pause
