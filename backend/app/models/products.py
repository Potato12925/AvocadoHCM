from pydantic import BaseModel, Field
from typing import Optional


class ProductItem(BaseModel):
    """
    Mô tả một sản phẩm trong sheet Products.
    - Các field đặt tên tiếng Anh để code dễ dùng.
    - Khi ghi ra sheet sẽ map theo cột tiếng Việt: 'barcode', 'hãng', 'tên', 'phân loại', 'đã đăng'.
    - 'published' chuẩn hoá thành '1' hoặc rỗng khi lưu.
    """

    barcode: str = Field(..., description="Mã vạch sản phẩm")
    brand: str = Field(..., description="Hãng/Thương hiệu")
    name: str = Field(..., description="Tên sản phẩm")
    category: str = Field(..., description="Phân loại/Danh mục")
    published: Optional[str] = Field(
        default="",
        description="Đã đăng: '1' hoặc rỗng",
    )

    class Config:
        # Cho phép populate bằng tên field (brand) hoặc alias nếu cần dùng trong tương lai
        allow_population_by_field_name = True

