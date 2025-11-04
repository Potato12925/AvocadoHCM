from fastapi import APIRouter, HTTPException
from app.models.sheets import Sheets
from pydantic import BaseModel
from typing import Optional, Any, Dict

router = APIRouter(prefix="/orders", tags=["Đơn hàng"])

class OrderItem(BaseModel):
    orderID: str
    customer_name: str
    order_code: str
    package_date: str
    total_cost: float
    note: Optional[str] = ""

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
