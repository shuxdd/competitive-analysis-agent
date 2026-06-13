"""
认证路由
========

用户注册和登录接口。
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import UserORM, get_session
from api.schemas import RegisterRequest, LoginRequest
from api.auth import hash_password, verify_password, create_token, require_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register")
async def register(req: RegisterRequest, session: AsyncSession = Depends(get_session)):
    """用户注册"""
    # 检查用户名是否已存在
    result = await session.execute(select(UserORM).where(UserORM.username == req.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="用户名已存在")

    user = UserORM(
        username=req.username,
        password_hash=hash_password(req.password),
        display_name=req.display_name or req.username,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_token(user.id)
    logger.info(f"用户注册: {user.username} (id={user.id})")
    return {
        "code": 200,
        "data": {
            "token": token,
            "user": {"id": user.id, "username": user.username, "display_name": user.display_name},
        },
        "message": "注册成功",
    }


@router.post("/login")
async def login(req: LoginRequest, session: AsyncSession = Depends(get_session)):
    """用户登录"""
    result = await session.execute(select(UserORM).where(UserORM.username == req.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_token(user.id)
    logger.info(f"用户登录: {user.username}")
    return {
        "code": 200,
        "data": {
            "token": token,
            "user": {"id": user.id, "username": user.username, "display_name": user.display_name},
        },
        "message": "登录成功",
    }


@router.get("/me")
async def get_me(user: UserORM = Depends(require_user)):
    """获取当前用户信息"""
    return {
        "code": 200,
        "data": {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
        },
        "message": "success",
    }
