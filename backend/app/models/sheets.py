"""
app/models/sheets.py
Giữ kết nối Google Sheets dùng chung cho toàn bộ ứng dụng.
- Kết nối 1 lần (lazy init), tái sử dụng client/sheet/worksheet.
- Cache worksheet theo tên.
- Có retry nhẹ khi gọi API bị chập chờn.
"""

from typing import Dict, Optional
import time

import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError

from app.config import SPREADSHEET_ID, SERVICE_ACCOUNT_JSON

# Phạm vi quyền cho Google Sheets
_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Biến toàn cục cho kết nối/caching
_client: Optional[gspread.Client] = None
_sheet: Optional[gspread.Spreadsheet] = None
_ws_cache: Dict[str, gspread.Worksheet] = {}

# ========== Core ==========

def _connect_if_needed():
    """Tạo client + mở sheet nếu chưa có."""
    global _client, _sheet
    if _client is None:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_JSON, scopes=_SCOPES)
        _client = gspread.authorize(creds)
    if _sheet is None:
        _sheet = _client.open_by_key(SPREADSHEET_ID)

def _with_retry(func, *args, retries: int = 3, delay: float = 0.5, **kwargs):
    """Retry đơn giản cho các lệnh Sheets hay bị lỗi tạm thời."""
    last_err = None
    for _ in range(retries):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            last_err = e
            time.sleep(delay)
    # Hết retry vẫn lỗi -> ném tiếp
    if last_err:
        raise last_err

def _get_ws(name: str) -> gspread.Worksheet:
    """Lấy worksheet theo tên, có cache."""
    _connect_if_needed()
    if name not in _ws_cache:
        _ws_cache[name] = _with_retry(_sheet.worksheet, name)
    return _ws_cache[name]

# ========== API tiện dụng để import dùng ngay ==========

class Sheets:
    """Facade lớp tĩnh: gọi trực tiếp mà không phải quan tâm kết nối."""
    @staticmethod
    def client() -> gspread.Client:
        _connect_if_needed()
        return _client  # type: ignore

    @staticmethod
    def spreadsheet() -> gspread.Spreadsheet:
        _connect_if_needed()
        return _sheet  # type: ignore

    @staticmethod
    def ws(name: str) -> gspread.Worksheet:
        return _get_ws(name)

    # Getter nhanh cho các sheet chuẩn của bạn:
    @staticmethod
    def imports() -> gspread.Worksheet:
        return _get_ws("Imports")

    @staticmethod
    def products() -> gspread.Worksheet:
        return _get_ws("Products")

    @staticmethod
    def orders() -> gspread.Worksheet:
        return _get_ws("Orders")

    @staticmethod
    def sold() -> gspread.Worksheet:
        return _get_ws("Sold")

    @staticmethod
    def ping() -> dict:
        """Kiểm tra kết nối nhanh: trả tên file + tên sheet đầu + số sheet."""
        _connect_if_needed()
        sheets = _with_retry(_sheet.worksheets)  # type: ignore
        return {
            "spreadsheet_title": _sheet.title,  # type: ignore
            "sheet_count": len(sheets),
            "first_sheet": sheets[0].title if sheets else None,
        }
