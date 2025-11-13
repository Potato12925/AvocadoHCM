# app/routes/expense_routes.py
from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from app.models.expenses import ExpenseItem, DeleteRowsRequest, UpdateRowsRequest
from app.services.expense_services import (
    list_expenses_raw,
    create_expense_row,
    delete_rows_by_indices,
    update_rows_bulk
)

router = APIRouter(prefix="/expenses", tags=["Chi tiêu"])

@router.get("/", summary="Lấy danh sách chi tiêu")
def get_expenses():
    try:
        return list_expenses_raw()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", summary="Tạo chi tiêu mới")
def create_expense(item: ExpenseItem):
    try:
        return create_expense_row(item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi ghi Google Sheets: {e}")

@router.post("/rows/delete", summary="Xóa nhiều dòng theo danh sách index (1-based)")
def delete_rows(req: DeleteRowsRequest):
    try:
        return delete_rows_by_indices(req)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa Google Sheets: {e}")

@router.patch("/rows/update", summary="Cập nhật nhiều dòng (gửi dữ liệu trong body)")
def update_rows(req: UpdateRowsRequest):
    try:
        return update_rows_bulk(req)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật Google Sheets: {e}")
