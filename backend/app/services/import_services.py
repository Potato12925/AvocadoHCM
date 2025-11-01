# app/services/import_service.py
import datetime
from typing import Any, Dict, List

from app.models.sheets import Sheets
from app.utils.id_generator import gen_product_id
from app.models.imports import ImportItem, DeleteRowsRequest, UpdateRowsRequest

# ===================== Helpers & Constants =====================

# Tên cột trong sheet Imports (A..M)
COLS = [
    "productID", "barcode", "brand", "name", "category",
    "qty_in", "unit_cost", "break_even_price", "import_date",
    "note", "qty_sold", "available_qty", "created_at"
]

def _normalize_date_vn(s: str) -> str:
    """
    Chuẩn hoá ngày về dạng DD/MM/YYYY.
    Hỗ trợ:
    - 'YYYY-MM-DD'
    - 'YYYY/MM/DD'
    - 'DD/MM/YYYY'
    Không parse được -> trả lại chuỗi gốc.
    """
    try:
        if not s:
            return ""
        s = s.strip()
        if "-" in s:
            dt = datetime.datetime.strptime(s, "%Y-%m-%d").date()
            return dt.strftime("%d/%m/%Y")
        if "/" in s:
            parts = s.split("/")
            if len(parts) == 3 and len(parts[0]) == 4:
                # YYYY/MM/DD
                dt = datetime.datetime.strptime(s, "%Y/%m/%d").date()
                return dt.strftime("%d/%m/%Y")
            # DD/MM/YYYY
            dt = datetime.datetime.strptime(s, "%d/%m/%Y").date()
            return dt.strftime("%d/%m/%Y")
    except Exception:
        pass
    return s

def _coerce_int(v: Any) -> int:
    try:
        return int(float(v))
    except Exception:
        return 0

def _coerce_float(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0

def _row_to_dict(row: List[str]) -> Dict[str, Any]:
    row = row + [""] * (len(COLS) - len(row))
    out = {COLS[i]: row[i] for i in range(len(COLS))}
    # ép kiểu số cho các cột numeric
    for k in ["qty_in", "qty_sold", "available_qty"]:
        if out.get(k, "") != "":
            out[k] = _coerce_int(out[k])
    for k in ["unit_cost", "break_even_price"]:
        if out.get(k, "") != "":
            out[k] = _coerce_float(out[k])
    return out

def _dict_to_row(d: Dict[str, Any]) -> List[str]:
    vals: List[str] = []
    for k in COLS:
        v = d.get(k, "")
        if v is None:
            v = ""
        vals.append(str(v))
    return vals

# ===================== Services =====================

# ---------- READ ----------
def list_imports_raw() -> Dict[str, Any]:
    ws = Sheets.imports()
    values = ws.get_all_values()
    header = values[0] if values else []
    data = values[1:] if len(values) > 1 else []
    return {"header": header, "count": len(data), "data": data}

# ---------- CREATE ----------
def create_import_row(item: ImportItem) -> Dict[str, Any]:
    ws = Sheets.imports()
    product_id = gen_product_id()

    # Ngày nhập (VN): ưu tiên normalize input; rỗng -> hôm nay
    if item.import_date:
        import_date = _normalize_date_vn(item.import_date)
    else:
        import_date = datetime.date.today().strftime("%d/%m/%Y")

    created_at = item.created_at or ""
    qty_sold = 0
    available_qty = item.qty_in - qty_sold

    row = [
        product_id,                 # A
        item.barcode,               # B
        item.brand,                 # C
        item.name,                  # D
        item.category,              # E
        str(item.qty_in),           # F
        f"{item.unit_cost}",        # G
        f"{item.break_even_price or 0}",  # H
        import_date,                # I
        item.note or "",            # J
        str(qty_sold),              # K
        str(available_qty),         # L
        created_at                  # M
    ]

    ws.append_row(row, value_input_option="USER_ENTERED")
    return {
        "message": "✅ Đã thêm lô hàng mới",
        "productID": product_id,
        "available_qty": available_qty
    }

# ---------- UPDATE (many rows from body) ----------
def update_rows_bulk(req: UpdateRowsRequest) -> Dict[str, Any]:
    ws = Sheets.imports()
    values = ws.get_all_values()
    total_rows = len(values)

    if not req.updates:
        raise ValueError("Danh sách cập nhật trống.")

    updated_rows: List[int] = []
    skipped: List[int] = []
    errors: List[Dict[str, Any]] = []

    for item in req.updates:
        r = item.row
        if r <= 1 or r > total_rows:
            skipped.append(r)
            continue

        try:
            current = _row_to_dict(values[r - 1])
            data = dict(item.data)

            # Chuẩn hoá ngày
            if "import_date" in data and data["import_date"]:
                data["import_date"] = _normalize_date_vn(str(data["import_date"]))

            # Ép kiểu số
            if "qty_in" in data and data["qty_in"] is not None:
                data["qty_in"] = _coerce_int(data["qty_in"])
            if "qty_sold" in data and data["qty_sold"] is not None:
                data["qty_sold"] = _coerce_int(data["qty_sold"])
            if "available_qty" in data and data["available_qty"] is not None:
                data["available_qty"] = _coerce_int(data["available_qty"])
            if "unit_cost" in data and data["unit_cost"] is not None:
                data["unit_cost"] = _coerce_float(data["unit_cost"])
            if "break_even_price" in data and data["break_even_price"] is not None:
                data["break_even_price"] = _coerce_float(data["break_even_price"])

            # Tự tính available_qty nếu không gửi mà có thay đổi qty_in/qty_sold
            if ("available_qty" not in data) and ("qty_in" in data or "qty_sold" in data):
                qi = _coerce_int(data.get("qty_in", current.get("qty_in", 0)))
                qs = _coerce_int(data.get("qty_sold", current.get("qty_sold", 0)))
                data["available_qty"] = max(0, qi - qs)

            updated = {**current, **data}
            ws.update(f"A{r}:M{r}", [_dict_to_row(updated)], value_input_option="USER_ENTERED")
            updated_rows.append(r)

        except Exception as e:
            errors.append({"row": r, "error": str(e)})

    return {
        "updated_rows": updated_rows,
        "skipped": skipped,
        "errors": errors,
        "message": f"✅ Đã cập nhật {len(updated_rows)} dòng, bỏ qua {len(skipped)}, lỗi {len(errors)}."
    }
# ---------- DELETE (many rows) ----------
def delete_rows_by_indices(req: DeleteRowsRequest) -> Dict[str, Any]:
    ws = Sheets.imports()
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

    return {
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
