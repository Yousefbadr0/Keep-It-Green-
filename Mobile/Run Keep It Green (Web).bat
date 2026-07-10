@echo off
title Keep It Green - Web
echo ============================================
echo   Keep It Green - launching in Edge...
echo   (leave this window open while testing)
echo   Press Q in this window to stop the app.
echo ============================================
echo.
set "PATH=D:\flutter\bin;%PATH%"
set "CHROME_EXECUTABLE=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
cd /d "%~dp0"
rem let Flutter pick a free port automatically (avoids "port in use" errors)
flutter run -d edge
echo.
echo App stopped. You can close this window.
pause
