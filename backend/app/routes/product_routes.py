from fastapi import APIRouter, HTTPException
from app.models.sheets import Sheets
router = APIRouter(prefix="/products", tags=["Sản phẩm"])

@router.get("/")
def get_orders():
    return {"message": "Danh sách sản phẩm"}

@router.post("/get")
def get_products():
    try:
        ws = Sheets.products()  # lấy worksheet 'Products'
        values = ws.get_all_values()

        # Bỏ dòng tiêu đề (dòng đầu tiên)
        data = values[1:] if len(values) > 1 else []

        return {
            "count": len(data),
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
