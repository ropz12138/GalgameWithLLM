"""
认证路由 - 定义认证相关的API端点
"""
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from controllers.auth_controller import AuthController
from utils.database import get_db
from utils.auth import get_current_user

# 创建路由器
auth_router = APIRouter(prefix="/auth", tags=["认证"])

# 创建控制器实例
auth_controller = AuthController()


# 请求模型
class UserRegisterRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    email: str = Field(None, description="邮箱（可选）")
    phone: str = Field(None, description="电话（可选）")


class UserLoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


# API端点
@auth_router.post("/register")
async def register(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册
    
    Args:
        user_data: 用户注册数据
        db: 数据库会话
        
    Returns:
        注册结果
    """
    return await auth_controller.register(user_data, db)


@auth_router.post("/login")
async def login(user_data: UserLoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    Args:
        user_data: 用户登录数据
        db: 数据库会话
        
    Returns:
        登录结果
    """
    return await auth_controller.login(user_data, db)


@auth_router.get("/me")
async def get_current_user_info(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        当前用户信息
    """
    return await auth_controller.get_user_info(current_user, db)


@auth_router.get("/validate-username")
async def validate_username(
    username: str = Query(..., description="要验证的用户名"),
    db: Session = Depends(get_db)
):
    """
    验证用户名是否可用
    
    Args:
        username: 用户名
        db: 数据库会话
        
    Returns:
        验证结果
    """
    return await auth_controller.validate_username(username, db)


@auth_router.get("/")
async def auth_root():
    """认证模块根端点"""
    return {
        "message": "认证模块",
        "endpoints": {
            "register": "/auth/register - 用户注册",
            "login": "/auth/login - 用户登录",
            "me": "/auth/me - 获取当前用户信息",
            "validate_username": "/auth/validate-username - 验证用户名"
        }
    } 