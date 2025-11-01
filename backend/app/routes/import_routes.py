# app/routes/import_routes.py
from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from app.models.imports import ImportItem, DeleteRowsRequest, UpdateRowsRequest
from app.services.import_services import (
    list_imports_raw,
    create_import_row,
    delete_rows_by_indices,
    update_rows_bulk
)

router = APIRouter(prefix="/imports", tags=["Nhập hàng"])

@router.get("/", summary="Lấy danh sách lô nhập (raw)")
def get_imports():
    try:
        return list_imports_raw()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", summary="Tạo lô nhập hàng mới (tính luôn tồn kho)")
def create_import(item: ImportItem):
    try:
        return create_import_row(item)
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
