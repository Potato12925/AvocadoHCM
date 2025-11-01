from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ImportItem(BaseModel):
    barcode: str = Field(..., description="Mã vạch sản phẩm (chuỗi)")
    brand: str
    name: str
    category: str
    qty_in: int = Field(gt=0, description="Số lượng nhập > 0")
    unit_cost: float = Field(ge=0, description="Giá vốn/đơn vị")
    break_even_price: Optional[float] = 0
    import_date: Optional[str] = Field(
        default=None,
        description="Ngày nhập (VN) 'DD/MM/YYYY' hoặc ISO 'YYYY-MM-DD'; rỗng -> hôm nay (VN)"
    )
    note: Optional[str] = ""
    created_at: Optional[str] = Field(
        default=None,
        description="Thời gian tạo lô (client cung cấp, ví dụ '2025-11-02 15:30:00')"
    )

class DeleteRowsRequest(BaseModel):
    rows: List[int] = Field(..., description="Danh sách số dòng (1-based) cần xóa")

class UpdateRowItem(BaseModel):
    row: int = Field(..., description="Số dòng (1-based) cần cập nhật")
    data: Dict[str, Any] = Field(..., description="Dữ liệu cần cập nhật cho dòng này (key theo COLS)")

class UpdateRowsRequest(BaseModel):
    updates: List[UpdateRowItem] = Field(..., description="Danh sách cập nhật nhiều dòng")
