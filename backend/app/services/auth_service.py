import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.db_models import User

# 配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "eyerest-os-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24 * 7  # 7天有效期

# Bearer token认证
security = HTTPBearer()


def hash_password(password: str) -> str:
    """哈希密码"""
    # bcrypt限制密码长度为72字节
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user_id: int, email: str) -> str:
    """创建JWT token"""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """解码JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户（依赖注入）"""
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取当前用户（可选，不强制认证）"""
    if credentials is None:
        return None

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        return None

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    return user


class AuthService:
    """认证服务"""

    def __init__(self, db: Session):
        self.db = db

    def register(self, email: str, password: str, display_name: Optional[str] = None) -> User:
        """注册新用户"""
        # 检查邮箱是否已存在
        existing = self.db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError("Email already registered")

        # 创建用户
        user = User(
            email=email,
            password_hash=hash_password(password),
            display_name=display_name or email.split("@")[0]
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # 创建默认偏好
        from ..models.db_models import UserPreferences
        prefs = UserPreferences(user_id=user.id)
        self.db.add(prefs)
        self.db.commit()

        return user

    def login(self, email: str, password: str) -> tuple[User, str]:
        """用户登录"""
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            raise ValueError("User not found")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid password")

        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        self.db.commit()

        # 生成token
        token = create_access_token(user.id, user.email)

        return user, token

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()