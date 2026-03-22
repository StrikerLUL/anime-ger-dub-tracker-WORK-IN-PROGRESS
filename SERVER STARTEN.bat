@echo off
chcp 65001 > nul
title Anime Synchro Tracker - Server
echo ============================================================
echo   ANIME SYNCHRO TRACKER - Automatischer Datenserver
echo ============================================================
echo.
echo  Was passiert jetzt:
echo  1. Python-Pakete werden geprueft (flask, playwright)
echo  2. Chromium-Browser wird im Hintergrund gestartet
echo  3. anisearch.de wird nach deutschen Syncros durchsucht
echo  4. Dein Browser oeffnet sich automatisch auf dem Tracker
echo.
echo  Server laeuft auf: http://localhost:5000
echo  Daten-API:         http://localhost:5000/api/anime-data
echo  Manuell refreshen: http://localhost:5000/api/refresh
echo.
echo  Zum Beenden: CTRL+C druecken
echo ============================================================
echo.

REM Kurz warten, dann Browser öffnen (Server braucht ~2 Sekunden zum Starten)
start "" /B cmd /C "timeout /t 4 /nobreak > nul && start http://localhost:5000"

python scrape_anisearch_fixed.py

echo.
echo Server wurde beendet.
pause
