"""
认证服务 - 处理用户认证相关的业务逻辑
"""
from datetime import timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user_model import User, UserCreate, UserLogin, UserResponse, Token
from utils.auth import (
    authenticate_user, 
    create_access_token, 
    get_user_by_username,
    get_user_by_email,
    get_user_by_phone,
    create_user
)


class AuthService:
    """认证服务类"""
    
    def __init__(self):
        pass
    
    def register_user(self, db: Session, user_data: UserCreate) -> Dict[str, Any]:
        """
        注册新用户
        
        Args:
            db: 数据库会话
            user_data: 用户注册数据
            
        Returns:
            注册结果
        """
        try:
            # 检查用户名是否已存在
            if get_user_by_username(db, user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已存在"
                )
            
            # 检查邮箱是否已存在（如果提供了邮箱）
            if user_data.email and get_user_by_email(db, user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被注册"
                )
            
            # 检查电话是否已存在（如果提供了电话）
            if user_data.phone and get_user_by_phone(db, user_data.phone):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="电话号码已被注册"
                )
            
            # 验证密码强度
            if len(user_data.password) < 6:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="密码长度至少6位"
                )
            
            # 创建用户
            user = create_user(db, user_data)
            
            return {
                "success": True,
                "message": "用户注册成功",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                    "created_at": user.created_at
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"注册失败: {str(e)}"
            )
    
    def login_user(self, db: Session, user_data: UserLogin) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            db: 数据库会话
            user_data: 用户登录数据
            
        Returns:
            登录结果
        """
        try:
            # 验证用户
            user = authenticate_user(db, user_data.username, user_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户名或密码错误"
                )
            
            # 检查用户是否被禁用
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户已被禁用"
                )
            
            # 创建访问令牌
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(
                data={"sub": user.username}, 
                expires_delta=access_token_expires
            )
            
            return {
                "success": True,
                "message": "登录成功",
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                    "created_at": user.created_at
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"登录失败: {str(e)}"
            )
    
    def get_user_info(self, db: Session, user: User) -> Dict[str, Any]:
        """
        获取用户信息
        
        Args:
            db: 数据库会话
            user: 当前用户
            
        Returns:
            用户信息
        """
        try:
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取用户信息失败: {str(e)}"
            )
    
    def validate_username(self, db: Session, username: str) -> Dict[str, Any]:
        """
        验证用户名是否可用
        
        Args:
            db: 数据库会话
            username: 用户名
            
        Returns:
            验证结果
        """
        try:
            user = get_user_by_username(db, username)
            available = user is None
            
            return {
                "success": True,
                "username": username,
                "available": available,
                "message": "用户名可用" if available else "用户名已存在"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"验证用户名失败: {str(e)}"
            ) 