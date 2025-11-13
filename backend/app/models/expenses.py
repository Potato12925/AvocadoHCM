from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ExpenseItem(BaseModel):
    date: str = Field(..., description="Ngày chi tiêu (VN) 'DD/MM/YYYY' hoặc ISO 'YYYY-MM-DD'")
    description: str = Field(..., description="Nội dung chi tiêu")
    amount: float = Field(gt=0, description="Số tiền > 0")
    note: Optional[str] = ""
    payer: str = Field(..., description="Người trả")

class DeleteRowsRequest(BaseModel):
    rows: List[int] = Field(..., description="Danh sách số dòng (1-based) cần xóa")

class UpdateRowItem(BaseModel):
    row: int = Field(..., description="Số dòng (1-based) cần cập nhật")
    data: Dict[str, Any] = Field(..., description="Dữ liệu cần cập nhật cho dòng này (key theo COLS)")

class UpdateRowsRequest(BaseModel):
    updates: List[UpdateRowItem] = Field(..., description="Danh sách cập nhật nhiều dòng")
