@echo off
title Keep It Green - Backend (LAN)
cd /d "%~dp0"
echo ===============================================================
echo   Keep It Green - backend
echo   Listening on ALL network interfaces, port 5217.
echo   Your phone (same Wi-Fi) reaches it at:  http://192.168.1.27:5217
echo   Leave this window open while using the app.
echo ===============================================================
echo.
dotnet run --urls http://0.0.0.0:5217
pause
