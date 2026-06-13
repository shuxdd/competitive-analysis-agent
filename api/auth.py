"""
认证鉴权模块
==========

提供 JWT token 创建/验证、密码哈希、获取当前用户依赖。
"""

import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from api.database import UserORM, get_session

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

ALGORITHM = "HS256"
HASH_ALGO = "sha256"
HASH_ITERATIONS = 260000
SALT_LENGTH = 16


def hash_password(password: str) -> str:
    """
    哈希密码（pbkdf2_hmac_sha256）。
    返回格式: algorithm$iterations$salt$hash
    """
    salt = secrets.token_hex(SALT_LENGTH)
    pwd_hash = hashlib.pbkdf2_hmac(HASH_ALGO, password.encode(), salt.encode(), HASH_ITERATIONS)
    return f"{HASH_ALGO}${HASH_ITERATIONS}${salt}${pwd_hash.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4:
            return False
        algo, iterations, salt, stored_hash = parts
        pwd_hash = hashlib.pbkdf2_hmac(algo, plain_password.encode(), salt.encode(), int(iterations))
        return pwd_hash.hex() == stored_hash
    except (ValueError, IndexError):
        return False


def create_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT token"""
    expire = datetime.now() + (expires_delta or timedelta(hours=settings.jwt_expire_hours))
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[str]:
    """验证 JWT token，返回 user_id"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> Optional[UserORM]:
    """
    从请求头提取当前用户。
    未提供 token 时返回 None（向后兼容），
    提供无效 token 时直接拒绝。
    """
    if credentials is None:
        return None

    user_id = verify_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的 token",
        )

    result = await session.execute(select(UserORM).where(UserORM.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )
    return user


async def require_user(
    user: Optional[UserORM] = Depends(get_current_user),
) -> UserORM:
    """强制要求登录"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
        )
    return user
