from typing import Any, Dict, List, Tuple

from app.models.sheets import Sheets
from app.models.imports import DeleteRowsRequest, UpdateRowsRequest

# Chuẩn cột cho sheet Products (A..E)
COLS = [
    "barcode", "hãng", "tên", "phân loại", "đã đăng"
]


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
    return out


def _dict_to_row_product(d: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for k in COLS:
        v = d.get(k, "")
        if k == "đã đăng":
            v = _normalize_published(v)
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
    Trả danh sách sản phẩm chỉ với các cột:
    - barcode, brand, name, category, đã đăng

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

    out_rows: List[List[str]] = []
    for r in data:
        # đảm bảo độ dài đủ
        row = r + [""] * (max(idx_barcode, idx_brand, idx_name, idx_category, (idx_published or -1)) + 1 - len(r))
        barcode = row[idx_barcode] if idx_barcode is not None else ""
        brand = row[idx_brand] if idx_brand is not None else ""
        name = row[idx_name] if idx_name is not None else ""
        category = row[idx_category] if idx_category is not None else ""
        published_raw = row[idx_published] if idx_published is not None else ""
        published = _normalize_published(published_raw)
        out_rows.append([barcode, brand, name, category, published])

    return {"header": COLS, "count": len(out_rows), "data": out_rows}


def create_product_row(item: Dict[str, Any]) -> Dict[str, Any]:
    ws = Sheets.products()
    header, _ = _get_header_and_values(ws)
    row = _dict_to_row(item, header)
    ws.append_row(row, value_input_option="USER_ENTERED")
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

            # Build end column letter dynamically (supports up to 26 cols)
            end_col_letter = chr(64 + max(1, len(header)))
            ws.update(f"A{r}:{end_col_letter}{r}", [_dict_to_row(updated, header)], value_input_option="USER_ENTERED")
            updated_rows.append(r)
        except Exception as e:
            errors.append({"row": r, "error": str(e)})

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
