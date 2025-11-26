@echo off
chcp 65001 >nul
title FastAPI + Vue Runner
color 0A

echo ============================
echo ===== START BACKEND ========
echo ============================

pushd backend
call venv\Scripts\activate
start "FASTAPI BACKEND" cmd /k "color 0B && echo FastAPI backend started && uvicorn app.main:app --reload --reload-dir app"
popd

echo ============================
echo ===== START FRONTEND =======
echo ============================

pushd frontend
start "VUE FRONTEND" cmd /k "color 0E && echo Vue frontend started && npm run dev -- --host 0.0.0.0 --port 5173"
popd

echo.
echo ====== EVERYTHING STARTED ======
echo 🚀 BACKEND + FRONTEND Now Running!
pause
