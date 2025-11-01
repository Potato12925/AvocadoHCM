from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib
import pkgutil
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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
