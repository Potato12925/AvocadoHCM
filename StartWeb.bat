@echo off
title 🚀 FastAPI + Vue Startup
color 0A

echo ====== START BACKEND ======
cd backend
call venv\Scripts\activate

:: chỉ watch thư mục app để không bị chậm
start "FASTAPI BACKEND" cmd /k "color 0B && echo === FastAPI backend === && uvicorn app.main:app --reload --reload-dir app"

cd ..

echo ====== START FRONTEND ======
cd frontend
start "VUE FRONTEND" cmd /k "color 0E && echo === Vue frontend === && npm run dev"
cd ..

echo ✅ Done
pause
