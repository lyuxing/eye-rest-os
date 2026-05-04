from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    SuccessResponse
)
from ..models.db_models import User, UserPreferences
from ..services.auth_service import AuthService, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    auth_service = AuthService(db)

    try:
        user = auth_service.register(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.display_name
        )

        # 生成token
        from ..services.auth_service import create_access_token
        token = create_access_token(user.id, user.email)

        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                onboarding_completed=user.onboarding_completed,
                created_at=user.created_at,
                last_login=user.last_login
            )
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    auth_service = AuthService(db)

    try:
        user, token = auth_service.login(
            email=credentials.email,
            password=credentials.password
        )

        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                onboarding_completed=user.onboarding_completed,
                created_at=user.created_at,
                last_login=user.last_login
            )
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        onboarding_completed=current_user.onboarding_completed,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.post("/logout", response_model=SuccessResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出（客户端删除token即可）"""
    return SuccessResponse(message="Logged out successfully")


@router.get("/check-email")
async def check_email(email: str, db: Session = Depends(get_db)):
    """检查邮箱是否已注册"""
    user = db.query(User).filter(User.email == email).first()
    return {"exists": user is not None}
