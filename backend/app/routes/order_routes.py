from fastapi import APIRouter, HTTPException
from app.models.sheets import Sheets

router = APIRouter(prefix="/orders", tags=["Đơn hàng"])

@router.get("/")
def get_orders():
    return {"message": "Danh sách đơn hàng"}

@router.post("/get")
def get_orders():
    try:
        ws = Sheets.orders()  # lấy worksheet 'Products'
        values = ws.get_all_values()

        # Bỏ dòng tiêu đề (dòng đầu tiên)
        data = values[1:] if len(values) > 1 else []

        return {
            "count": len(data),
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
