@echo off
title Ourson Hunter — Serveur Web Local
echo ========================================================
echo   DEMARRAGE DU SERVEUR OURSON HUNTER GLOBAL
echo ========================================================
echo.
echo Ouverture automatique de http://localhost:8080 ...
start "" "http://localhost:8080"
python "%~dp0scripts\serveur_local.py"
pause
