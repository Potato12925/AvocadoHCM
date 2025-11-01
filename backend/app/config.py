import os
from dotenv import load_dotenv

# --- Nạp biến môi trường ---
load_dotenv()

# --- Đọc biến từ file .env ---
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON", "credentials.json")
TZ = os.getenv("TZ", "Asia/Ho_Chi_Minh")

# --- Kiểm tra giá trị ---
if not SPREADSHEET_ID:
    raise ValueError("⚠️ Thiếu SPREADSHEET_ID trong file .env")

print("✅ Đã nạp biến môi trường:")
print("SPREADSHEET_ID:", SPREADSHEET_ID)
print("SERVICE_ACCOUNT_JSON:", SERVICE_ACCOUNT_JSON)
print("TZ:", TZ)
