@echo off
title Allow Keep It Green through the firewall
rem Right-click this file and choose "Run as administrator".
net session >nul 2>&1
if %errorlevel% neq 0 (
  echo This needs administrator rights.
  echo Right-click the file and choose "Run as administrator".
  echo.
  pause
  exit /b 1
)
netsh advfirewall firewall delete rule name="KeepItGreen 5217" >nul 2>&1
netsh advfirewall firewall add rule name="KeepItGreen 5217" dir=in action=allow protocol=TCP localport=5217
echo.
echo Done. Your phone can now reach the backend on port 5217.
pause
