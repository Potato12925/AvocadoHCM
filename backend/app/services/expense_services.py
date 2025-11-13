import datetime
from typing import Any, Dict, List

from app.models.sheets import Sheets
from app.models.expenses import ExpenseItem, DeleteRowsRequest, UpdateRowsRequest

# Tên cột trong sheet Expenses (A..E)
COLS = [
    "date", "description", "amount", "note", "payer"
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

def _coerce_float(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0

def _row_to_dict(row: List[str]) -> Dict[str, Any]:
    row = row + [""] * (len(COLS) - len(row))
    out = {COLS[i]: row[i] for i in range(len(COLS))}
    # ép kiểu số cho cột amount
    if out.get("amount", "") != "":
        out["amount"] = _coerce_float(out["amount"])
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
def list_expenses_raw() -> Dict[str, Any]:
    ws = Sheets.expenses()
    values = ws.get_all_values()
    header = values[0] if values else []
    data = values[1:] if len(values) > 1 else []
    return {"header": header, "count": len(data), "data": data}

# ---------- CREATE ----------
def create_expense_row(item: ExpenseItem) -> Dict[str, Any]:
    ws = Sheets.expenses()

    # Ngày chi tiêu (VN): ưu tiên normalize input; rỗng -> hôm nay
    if item.date:
        date = _normalize_date_vn(item.date)
    else:
        date = datetime.date.today().strftime("%d/%m/%Y")

    row = [
        date,                       # A
        item.description,           # B
        f"{item.amount}",          # C
        item.note or "",           # D
        item.payer,                # E
    ]

    ws.append_row(row, value_input_option="USER_ENTERED")
    return {
        "message": "✅ Đã thêm chi tiêu mới",
        "date": date,
        "description": item.description
    }

# ---------- UPDATE (many rows from body) ----------
def update_rows_bulk(req: UpdateRowsRequest) -> Dict[str, Any]:
    ws = Sheets.expenses()
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
            if "date" in data and data["date"]:
                data["date"] = _normalize_date_vn(str(data["date"]))

            # Ép kiểu số
            if "amount" in data and data["amount"] is not None:
                data["amount"] = _coerce_float(data["amount"])

            updated = {**current, **data}
            ws.update(f"A{r}:E{r}", [_dict_to_row(updated)], value_input_option="USER_ENTERED")
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
    ws = Sheets.expenses()
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
