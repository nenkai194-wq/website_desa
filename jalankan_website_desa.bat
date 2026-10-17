@echo off
title WEBSITE RESMI DESA KERSIK - KUTAI KARTANEGARA
color 0A
echo ========================================================
echo        PORTAL WEBSITE PROFIL DESA KERSIK
echo        Kec. Marang Kayu, Kab. Kutai Kartanegara
echo ========================================================
echo.
echo Menjalankan server website desa di http://localhost:8080 ...
echo.
echo - Website Publik: http://localhost:8080
echo - Panel Admin CMS: http://localhost:8080/admin (User: admin / Pass: admin123)
echo.
start http://localhost:8080
python app.py
pause
