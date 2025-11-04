from fastapi import APIRouter, HTTPException
from app.models.sheets import Sheets
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/sold", tags=["Đã bán"])

class SoldItem(BaseModel):
    orderID: str
    productID: str
    barcode: str
    brand: str
    name: str
    category: str
    qty_sold: int
    unit_cost: float
    total_cost: float

@router.get("/")
def get_sold():
    return {"message": "Danh sách sản phẩm đã bán"}

@router.post("/get")
def get_sold_items():
    try:
        ws = Sheets.sold()
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
def create_sold_item(item: SoldItem):
    try:
        ws = Sheets.sold()
        row = [
            item.orderID,
            item.productID,
            item.barcode,
            item.brand,
            item.name,
            item.category,
            str(item.qty_sold),
            str(item.unit_cost),
            str(item.total_cost)
        ]
        ws.append_row(row, value_input_option="USER_ENTERED")
        return {
            "message": "✅ Đã ghi sản phẩm đã bán",
            "orderID": item.orderID
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
