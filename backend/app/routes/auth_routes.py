from fastapi import APIRouter, Response, Request, HTTPException, status
from pydantic import BaseModel
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.models.sheets import Sheets

router = APIRouter(prefix="/auth", tags=["Xác thực"])

class LoginRequest(BaseModel):
    password: str

COOKIE_NAME = "avocado_auth_token"
COOKIE_VALUE = "authenticated_user_abc"
MAX_AGE = 90 * 24 * 60 * 60  # 90 ngày

ph = PasswordHasher()

@router.post("/login", summary="Đăng nhập")
def login(req: LoginRequest, response: Response):
    try:
        ws = Sheets.ws("Authentication")
        hashed_password = ws.acell("A1").value
        
        if not hashed_password:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không tìm thấy cấu hình mật khẩu"
            )
            
        ph.verify(hashed_password, req.password)
        
        response.set_cookie(
            key=COOKIE_NAME,
            value=COOKIE_VALUE,
            max_age=MAX_AGE,
            httponly=True,
            samesite="lax",
            path="/"
        )
        return {"message": "Đăng nhập thành công"}
    except VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mật khẩu không đúng"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xác thực: {str(e)}"
        )

@router.post("/logout", summary="Đăng xuất")
def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/", httponly=True, samesite="lax")
    return {"message": "Đã đăng xuất"}

@router.get("/check", summary="Kiểm tra trạng thái đăng nhập")
def check_auth(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if token == COOKIE_VALUE:
        return {"authenticated": True}
    return {"authenticated": False}
