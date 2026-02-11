from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import importlib
import pkgutil
import os
from app import routes  # import thư mục routes
from app.models.sheets import Sheets

app = FastAPI(
    title="AvocadoHCM Backend API",
    description="API quản lý nhập hàng, tồn kho và đơn hàng - kết nối Google Sheets",
    version="1.0.0"
)

# --- Cho phép frontend Vue gọi ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Tự động load toàn bộ router trong thư mục app/routes ---
def register_all_routers(app: FastAPI):
    package = routes
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package.__name__}.{module_name}")
        if hasattr(module, "router"):
            app.include_router(module.router)
            print(f"✅ Đã đăng ký router: {module_name}")

register_all_routers(app)

# --- Serve frontend static files ---
frontend_dist_path = os.path.join(os.path.dirname(__file__), '../../frontend/dist')
if os.path.exists(frontend_dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_path, 'assets')), name="assets")

# --- Route kiểm tra nhanh ---
@app.get("/")
def home():
    return {"message": "🚀 AvocadoHCM API đang chạy!"}


@app.get("/health/sheets")
def health_check():
    try:
        info = Sheets.ping()
        return {"status": "ok", "google_sheets": info}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# --- Serve index.html for SPA routing (only for non-API routes) ---
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Don't serve SPA for API endpoints
    if full_path.startswith(('products/', 'imports/', 'orders/', 'sold/', 'expenses/', 'externals/', 'health/')):
        return {"error": "Not found"}

    index_path = os.path.join(frontend_dist_path, 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not built. Run: cd frontend && npm run build"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
