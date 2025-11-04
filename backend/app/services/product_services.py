from typing import Any, Dict, List

from app.models.sheets import Sheets
from app.models.imports import DeleteRowsRequest, UpdateRowsRequest


def _get_header_and_values(ws) -> (List[str], List[List[str]]):
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


def list_products_raw() -> Dict[str, Any]:
    ws = Sheets.products()
    header, data = _get_header_and_values(ws)
    return {"header": header, "count": len(data), "data": data}


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

