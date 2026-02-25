@echo off
chcp 65001 >nul
title Coduck Wars - Tunnel Launcher

set CONDA=C:\Users\playdata2\miniconda3\condabin\conda.bat
set LT=C:\Users\playdata2\miniconda3\envs\gemini_env\lt.cmd
set NPX=C:\Users\playdata2\miniconda3\envs\gemini_env\npx.cmd
set PROJ=C:\Users\playdata2\Desktop\SKN20-FINAL_5TEAM\SKN20-FINAL-5TEAM

echo ============================================
echo   CODUCK WARS - TUNNEL MODE
echo ============================================

echo [1/4] Backend Server...
start "Backend" cmd /k "call %CONDA% activate final_project && cd /d %PROJ%\backend && set DJANGO_SETTINGS_MODULE=config.settings && python -m uvicorn config.asgi:application --host 0.0.0.0 --port 8000"
ping 127.0.0.1 -n 6 >nul

echo [2/4] Backend Tunnel...
start "BackendTunnel" cmd /k ""%LT%" --port 8000 --subdomain coduck-backend"
ping 127.0.0.1 -n 3 >nul

echo [3/4] Frontend Server...
start "Frontend" cmd /k "cd /d %PROJ%\frontend && "%NPX%" vite --mode tunnel --host 0.0.0.0"
ping 127.0.0.1 -n 4 >nul

echo [4/4] Frontend Tunnel...
start "FrontendTunnel" cmd /k ""%LT%" --port 5173 --subdomain coduck-frontend"

echo.
echo ============================================
echo   DONE! URL: https://coduck-frontend.loca.lt
echo ============================================
pause
