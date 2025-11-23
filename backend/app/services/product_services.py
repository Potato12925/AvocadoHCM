import locale
from typing import Any, Dict, List, Optional, Tuple

from app.models.sheets import Sheets
from app.models.imports import DeleteRowsRequest, UpdateRowsRequest

# Chuẩn cột cho sheet Products (A..F)
COLS = [
    "barcode", "hãng", "tên", "phân loại", "đã đăng", "số lượng"
]


_COLLATE_LOCALE: Optional[str] = None


def _normalize_text(val: Any) -> str:
    return str(val if val is not None else "").strip().lower()


def _ensure_vi_locale() -> None:
    """
    Đặt locale so sánh chuỗi ưu tiên tiếng Việt nếu có sẵn, fallback về locale hiện tại.
    """
    global _COLLATE_LOCALE
    if _COLLATE_LOCALE is not None:
        return
    for loc in ("vi_VN.UTF-8", "vi_VN.utf8", "vi_VN", "vi"):
        try:
            locale.setlocale(locale.LC_COLLATE, loc)
            _COLLATE_LOCALE = loc
            return
        except locale.Error:
            continue
    # Giữ nguyên locale hiện tại nếu không thiết lập được tiếng Việt
    _COLLATE_LOCALE = locale.setlocale(locale.LC_COLLATE)


def _collation_key(val: Any) -> str:
    """
    Trả về khóa so sánh có hỗ trợ chữ tiếng Việt (nếu locale khả dụng).
    """
    _ensure_vi_locale()
    return locale.strxfrm(_normalize_text(val))


def _normalize_header_key(key: str) -> str:
    return (key or "").strip().lower()


def _find_column_index(header: List[str], candidates: List[str]) -> Optional[int]:
    lookup = {_normalize_header_key(h): idx for idx, h in enumerate(header)}
    for candidate in candidates:
        idx = lookup.get(_normalize_header_key(candidate))
        if idx is not None:
            return idx
    return None


def _product_sort_key(row: List[str], idx_brand: Optional[int], idx_name: Optional[int],
                      idx_category: Optional[int]) -> Tuple[str, str, str]:
    def pick(idx: Optional[int]) -> str:
        if idx is None or idx < 0 or idx >= len(row):
            return ""
        return _collation_key(row[idx])
    return (pick(idx_brand), pick(idx_name), pick(idx_category))


def _determine_insert_position_for_product(header: List[str], data: List[List[str]],
                                           new_row: List[str]) -> int:
    if not header:
        # Sheet chưa có header -> thêm ở dòng đầu (1-based).
        return 1

    idx_brand = _find_column_index(header, ["hãng", "hang", "brand"])
    idx_name = _find_column_index(header, ["tên", "ten", "name"])
    idx_category = _find_column_index(header, ["phân loại", "phan loai", "loại", "loai", "category"])
    new_key = _product_sort_key(new_row, idx_brand, idx_name, idx_category)

    insert_at = len(data) + 2  # Mặc định thêm cuối sau header
    for idx, row in enumerate(data, start=2):
        if _product_sort_key(row, idx_brand, idx_name, idx_category) > new_key:
            insert_at = idx
            break
    return insert_at


def _parse_int(val: Any) -> int:
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    try:
        s = str(val).strip()
        if not s:
            return 0
        s = s.replace(",", "")
        return int(float(s))
    except Exception:
        return 0


def _column_letter(idx: int) -> str:
    """Chuyển chỉ số cột (1-based) sang chữ, hỗ trợ > 26 cột."""
    if idx <= 0:
        return "A"
    letters = ""
    while idx > 0:
        idx, rem = divmod(idx - 1, 26)
        letters = chr(65 + rem) + letters
    return letters or "A"


def _aggregate_stock_from_imports() -> Dict[str, int]:
    """Cộng dồn available_qty theo barcode từ sheet Imports."""
    ws_imports = Sheets.imports()
    values = ws_imports.get_all_values()
    if not values or len(values) <= 1:
        return {}

    stock: Dict[str, int] = {}
    for row in values[1:]:
        if not row:
            continue
        barcode = str(row[1]).strip() if len(row) > 1 else ""
        if not barcode:
            continue
        available = row[11] if len(row) > 11 else ""
        qty = max(0, _parse_int(available))
        stock[barcode] = stock.get(barcode, 0) + qty
    return stock


def _get_header_and_values(ws) -> Tuple[List[str], List[List[str]]]:
    values = ws.get_all_values()
    header = values[0] if values else []
    data = values[1:] if len(values) > 1 else []
    return header, data


def _row_to_dict(row: List[str], cols: List[str]) -> Dict[str, Any]:
    row = row + [""] * (len(cols) - len(row))
    return {cols[i]: row[i] for i in range(len(cols))}


def _dict_to_row(d: Dict[str, Any], cols: List[str]) -> List[str]:
    out: List[str] = []
    for k in cols:
        v = d.get(k, "")
        if v is None:
            v = ""
        out.append(str(v))
    return out


# Helpers cố định theo COLS của Products
def _row_to_dict_product(row: List[str]) -> Dict[str, Any]:
    row = row + [""] * (len(COLS) - len(row))
    out = {COLS[i]: row[i] for i in range(len(COLS))}
    out["đã đăng"] = _normalize_published(out.get("đã đăng", ""))
    qty_raw = out.get("số lượng", "")
    out["số lượng"] = str(_parse_int(qty_raw)) if qty_raw not in ("", None) else "0"
    return out


def _dict_to_row_product(d: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for k in COLS:
        v = d.get(k, "")
        if k == "đã đăng":
            v = _normalize_published(v)
        elif k == "số lượng":
            v = str(_parse_int(v))
        if v is None:
            v = ""
        out.append(str(v))
    return out


def list_products_raw() -> Dict[str, Any]:
    ws = Sheets.products()
    header, data = _get_header_and_values(ws)
    return {"header": header, "count": len(data), "data": data}


def _normalize_published(val: Any) -> str:
    """Chuẩn hóa cờ 'đã đăng' về '1' hoặc rỗng."""
    if val is None:
        return ""
    s = str(val).strip().lower()
    if s in ("1", "true", "yes", "y", "đã đăng", "da dang", "published"):
        return "1"
    return "1" if s and s not in ("0", "false", "no", "n", "") else ""


def list_products_view() -> Dict[str, Any]:
    """
    Trả danh sách sản phẩm với các cột:
    - barcode, brand, name, category, đã đăng, số lượng

    'đã đăng' lấy từ cột có tên gần nghĩa ('published', 'đã đăng', 'is_published') nếu tồn tại;
    nếu không có cột, để rỗng. Giá trị chuẩn hóa: '1' hoặc ''.
    """
    ws = Sheets.products()
    header, data = _get_header_and_values(ws)

    # Ánh xạ tên cột -> index (không phân biệt hoa thường, bỏ khoảng trắng)
    def norm(h: str) -> str:
        return (h or "").strip().lower()

    idx = {norm(h): i for i, h in enumerate(header)}
    idx_barcode = idx.get("barcode", 0)
    # Hỗ trợ cả tiếng Việt và tiếng Anh cho các cột
    idx_brand = idx.get("hãng", idx.get("brand", 1))
    idx_name = idx.get("tên", idx.get("name", 2))
    idx_category = idx.get("phân loại", idx.get("category", 3))

    # Tìm cột 'published' nếu có
    idx_published = None
    for key in ("published", "is_published", "đã đăng", "da dang", "dang"):
        if key in idx:
            idx_published = idx[key]
            break

    idx_quantity = None
    for key in ("số lượng", "so luong", "tồn kho", "ton kho", "quantity", "qty"):
        if key in idx:
            idx_quantity = idx[key]
            break

    max_idx = max(
        [i for i in [idx_barcode, idx_brand, idx_name, idx_category, idx_published, idx_quantity] if i is not None]
        or [0]
    )

    out_rows: List[List[str]] = []
    for r in data:
        # đảm bảo độ dài đủ
        row = r + [""] * (max_idx + 1 - len(r))
        barcode = row[idx_barcode] if idx_barcode is not None else ""
        brand = row[idx_brand] if idx_brand is not None else ""
        name = row[idx_name] if idx_name is not None else ""
        category = row[idx_category] if idx_category is not None else ""
        published_raw = row[idx_published] if idx_published is not None else ""
        published = _normalize_published(published_raw)
        quantity_raw = row[idx_quantity] if idx_quantity is not None else ""
        quantity = str(_parse_int(quantity_raw)) if quantity_raw not in ("", None) else "0"
        out_rows.append([barcode, brand, name, category, published, quantity])

    return {"header": COLS, "count": len(out_rows), "data": out_rows}


def create_product_row(item: Dict[str, Any]) -> Dict[str, Any]:
    ws = Sheets.products()
    values = ws.get_all_values()
    header = values[0] if values else list(COLS)
    data = values[1:] if len(values) > 1 else []

    row = _dict_to_row(item, header)
    if not values:
        ws.append_row(row, value_input_option="USER_ENTERED")
    else:
        insert_at = _determine_insert_position_for_product(header, data, row)
        ws.insert_row(row, index=insert_at, value_input_option="USER_ENTERED")

    sync_product_quantities()
    return {"message": "✅ Đã thêm sản phẩm", "row_values": row}


def update_product_rows_bulk(req: UpdateRowsRequest) -> Dict[str, Any]:
    ws = Sheets.products()
    values = ws.get_all_values()
    total_rows = len(values)

    if not req.updates:
        raise ValueError("Danh sách cập nhật trống.")

    header = values[0] if values else []
    updated_rows: List[int] = []
    skipped: List[int] = []
    errors: List[Dict[str, Any]] = []

    for item in req.updates:
        r = item.row
        if r <= 1 or r > total_rows:
            skipped.append(r)
            continue

        try:
            current = _row_to_dict(values[r - 1], header)
            data = dict(item.data)
            updated = {**current, **data}

            end_col_letter = _column_letter(max(1, len(header)))
            ws.update(f"A{r}:{end_col_letter}{r}", [_dict_to_row(updated, header)], value_input_option="USER_ENTERED")
            updated_rows.append(r)
        except Exception as e:
            errors.append({"row": r, "error": str(e)})

    if updated_rows:
        sync_product_quantities()

    return {
        "updated_rows": updated_rows,
        "skipped": skipped,
        "errors": errors,
        "message": f"✅ Đã cập nhật {len(updated_rows)} dòng, bỏ qua {len(skipped)}, lỗi {len(errors)}."
    }


def delete_product_rows_by_indices(req: DeleteRowsRequest) -> Dict[str, Any]:
    ws = Sheets.products()
    total_rows = len(ws.get_all_values())

    unique_rows = sorted({r for r in req.rows if isinstance(r, int) and r > 0}, reverse=True)
    if not unique_rows:
        raise ValueError("Danh sách dòng cần xóa trống hoặc không hợp lệ.")

    invalid: List[int] = []
    protected: List[int] = []
    will_delete: List[int] = []

    for r in unique_rows:
        if r == 1:
            protected.append(r)
        elif r > total_rows:
            invalid.append(r)
        else:
            will_delete.append(r)

    deleted: List[int] = []
    for r in will_delete:
        ws.delete_rows(r)
        deleted.append(r)

    result = {
        "summary": {
            "total_rows_in_sheet": total_rows,
            "requested": req.rows,
            "normalized_desc": unique_rows
        },
        "deleted_rows": deleted,
        "skipped_protected_header": protected,
        "invalid_rows": invalid,
        "message": f"Đã xóa {len(deleted)} dòng. Bỏ qua {len(protected)} dòng tiêu đề và {len(invalid)} dòng không hợp lệ."
    }
    return result


def sync_product_quantities() -> Dict[str, Any]:
    """
    Cập nhật cột 'số lượng' trên sheet Products dựa trên tổng available_qty từ Imports.
    """
    ws = Sheets.products()
    header, data = _get_header_and_values(ws)
    if not header or not data:
        return {"updated_rows": 0, "message": "Không có sản phẩm để đồng bộ."}

    def norm(h: str) -> str:
        return (h or "").strip().lower()

    idx = {norm(h): i for i, h in enumerate(header)}
    idx_barcode = idx.get("barcode", 0)
    idx_quantity = None
    for key in ("số lượng", "so luong", "tồn kho", "ton kho", "quantity", "qty"):
        if key in idx:
            idx_quantity = idx[key]
            break

    if idx_quantity is None:
        return {"updated_rows": 0, "message": "Không tìm thấy cột 'số lượng' trong sheet Products."}

    stock_map = _aggregate_stock_from_imports()
    max_idx = max(idx_barcode or 0, idx_quantity or 0)

    values_to_write: List[List[str]] = []
    for r in data:
        row = r + [""] * (max_idx + 1 - len(r))
        barcode = str(row[idx_barcode]).strip() if idx_barcode is not None and idx_barcode < len(row) else ""
        qty = stock_map.get(barcode, 0) if barcode else 0
        values_to_write.append([str(qty)])

    start_row = 2
    end_row = start_row + len(values_to_write) - 1
    col_letter = _column_letter(idx_quantity + 1)
    ws.update(f"{col_letter}{start_row}:{col_letter}{end_row}", values_to_write, value_input_option="USER_ENTERED")
    return {"updated_rows": len(values_to_write), "message": f"Đã đồng bộ tồn kho cho {len(values_to_write)} sản phẩm."}
