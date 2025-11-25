from fastapi import APIRouter, HTTPException
from app.models.sheets import Sheets
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/orders", tags=["Đơn hàng"])

class OrderItem(BaseModel):
    orderID: str
    customer_name: str
    order_code: str
    package_date: str
    total_cost: float
    note: Optional[str] = ""


class UpdateRowsRequest(BaseModel):
    updates: list


class DeleteRowsRequest(BaseModel):
    rows: List[int]

@router.get("/")
def get_orders():
    return {"message": "Danh sách đơn hàng"}

@router.post("/get")
def get_orders_list():
    try:
        ws = Sheets.orders()
        values = ws.get_all_values()

        # Bỏ dòng tiêu đề (dòng đầu tiên)
        data = values[1:] if len(values) > 1 else []

        return {
            "count": len(data),
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def create_order(item: OrderItem):
    try:
        ws = Sheets.orders()
        # Chặn trùng orderID hoặc order_code đã tồn tại
        existing = ws.get_all_values()
        data = existing[1:] if len(existing) > 1 else []
        for row in data:
            if len(row) >= 1 and row[0] == item.orderID:
                raise HTTPException(status_code=400, detail="OrderID đã tồn tại")
            if len(row) >= 3 and row[2] and item.order_code and row[2] == item.order_code:
                raise HTTPException(status_code=400, detail="Mã đơn hàng đã được dùng")

        row = [
            item.orderID,
            item.customer_name,
            item.order_code,
            item.package_date,
            str(item.total_cost),
            item.note or ""
        ]
        ws.append_row(row, value_input_option="USER_ENTERED")
        return {
            "message": "✅ Đã tạo đơn hàng",
            "orderID": item.orderID
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/rows/update")
def update_rows(req: UpdateRowsRequest):
    """
    Cập nhật nhiều dòng trong sheet Orders.
    Body: { updates: [{ row: int (1-based), data: { colName: value, ... } }, ...] }
    """
    try:
        ws = Sheets.orders()
        for upd in req.updates:
            row_idx = upd.get("row")
            data = upd.get("data", {})
            if not row_idx or not isinstance(data, dict):
                continue
            # map các key trùng header: orderID, customer_name, order_code, package_date, total_cost, note
            headers = ws.row_values(1)
            for key, val in data.items():
                if key in headers:
                    col_idx = headers.index(key) + 1
                    ws.update_cell(row_idx, col_idx, val)
        return {"message": "✅ Đã cập nhật Orders", "count": len(req.updates)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rows/delete")
def delete_rows(req: DeleteRowsRequest):
    """
    Xóa nhiều dòng trong sheet Orders theo index (1-based).
    """
    try:
        ws = Sheets.orders()
        for row_idx in sorted(req.rows or [], reverse=True):
            ws.delete_rows(row_idx)
        return {"message": "✅ Đã xoá Orders", "count": len(req.rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
