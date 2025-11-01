import time
import secrets

def gen_product_id() -> str:
    """
    Sinh mã productID duy nhất cho mỗi lô hàng.
    Dựa trên thời gian (ms) + chuỗi ngẫu nhiên → gần như không trùng.
    """
    timestamp = int(time.time() * 1000)  # thời gian hiện tại (ms)
    random_part = secrets.token_hex(3).upper()  # 6 ký tự ngẫu nhiên
    return f"P{timestamp}{random_part}"
