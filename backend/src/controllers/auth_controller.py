"""
认证控制器 - 处理认证相关的HTTP请求
"""
from typing import Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session

from services.auth_service import AuthService
from models.user_model import UserCreate, UserLogin, User
from utils.auth import get_current_active_user


class AuthController:
    """认证控制器类"""
    
    def __init__(self):
        self.auth_service = AuthService()
    
    async def register(self, user_data: UserCreate, db: Session) -> Dict[str, Any]:
        """
        用户注册
        
        Args:
            user_data: 用户注册数据
            db: 数据库会话
            
        Returns:
            注册结果
        """
        try:
            print(f"\n🔍 [AuthController] 收到注册请求:")
            print(f"  👤 用户名: {user_data.username}")
            print(f"  📧 邮箱: {user_data.email}")
            print(f"  📱 电话: {user_data.phone}")
            
            result = self.auth_service.register_user(db, user_data)
            
            print(f"✅ [AuthController] 注册成功:")
            print(f"  🆔 用户ID: {result['user']['id']}")
            
            return result
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ [AuthController] 注册失败: {e}")
            raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")
    
    async def login(self, user_data: UserLogin, db: Session) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            user_data: 用户登录数据
            db: 数据库会话
            
        Returns:
            登录结果
        """
        try:
            print(f"\n🔍 [AuthController] 收到登录请求:")
            print(f"  👤 用户名: {user_data.username}")
            
            result = self.auth_service.login_user(db, user_data)
            
            print(f"✅ [AuthController] 登录成功:")
            print(f"  🆔 用户ID: {result['user']['id']}")
            print(f"  🔑 令牌类型: {result['token_type']}")
            
            return result
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ [AuthController] 登录失败: {e}")
            raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")
    
    async def get_user_info(self, current_user: User, db: Session) -> Dict[str, Any]:
        """
        获取当前用户信息
        
        Args:
            current_user: 当前用户
            db: 数据库会话
            
        Returns:
            用户信息
        """
        try:
            print(f"\n🔍 [AuthController] 获取用户信息:")
            print(f"  👤 用户名: {current_user.username}")
            
            result = self.auth_service.get_user_info(db, current_user)
            
            print(f"✅ [AuthController] 获取用户信息成功")
            
            return result
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ [AuthController] 获取用户信息失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")
    
    async def validate_username(self, username: str, db: Session) -> Dict[str, Any]:
        """
        验证用户名是否可用
        
        Args:
            username: 用户名
            db: 数据库会话
            
        Returns:
            验证结果
        """
        try:
            print(f"\n🔍 [AuthController] 验证用户名:")
            print(f"  👤 用户名: {username}")
            
            result = self.auth_service.validate_username(db, username)
            
            print(f"✅ [AuthController] 用户名验证完成:")
            print(f"  ✅ 可用性: {result['available']}")
            
            return result
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ [AuthController] 验证用户名失败: {e}")
            raise HTTPException(status_code=500, detail=f"验证用户名失败: {str(e)}") 