from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.models.imports import DeleteRowsRequest, UpdateRowsRequest
from app.services.product_services import (
    list_products_raw,
    list_products_view,
    create_product_row,
    delete_product_rows_by_indices,
    update_product_rows_bulk,
)

router = APIRouter(prefix="/products", tags=["Sản phẩm"])


@router.get("/", summary="Lấy danh sách sản phẩm (barcode, brand, name, category, đã đăng)")
def get_products():
    try:
        return list_products_view()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", summary="Tạo sản phẩm mới (ghi theo header)")
def create_product(item: Dict[str, Any]):
    try:
        return create_product_row(item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi ghi Google Sheets: {e}")


@router.post("/rows/delete", summary="Xóa nhiều dòng theo danh sách index (1-based)")
def delete_rows(req: DeleteRowsRequest):
    try:
        return delete_product_rows_by_indices(req)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa Google Sheets: {e}")


@router.patch("/rows/update", summary="Cập nhật nhiều dòng (gửi dữ liệu trong body)")
def update_rows(req: UpdateRowsRequest):
    try:
        return update_product_rows_bulk(req)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật Google Sheets: {e}")
