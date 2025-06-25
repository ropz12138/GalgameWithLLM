"""
用户认证服务
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select

from ..database.models import User
from ..database.config import get_database_url
from ..models.auth_models import UserRegister, UserLogin, UserResponse, TokenData

logger = logging.getLogger(__name__)

class AuthService:
    """用户认证服务"""
    
    # JWT配置
    SECRET_KEY = "your-secret-key-here-change-in-production"  # 生产环境需要修改
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.engine = create_engine(get_database_url())
        self.security = HTTPBearer()
    
    def _get_db_session(self) -> Session:
        """获取数据库会话"""
        return Session(self.engine)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """创建访问令牌"""
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
            
            logger.info(f"🔑 [AuthService] 访问令牌创建成功 - 用户: {data.get('sub')}, 过期时间: {expire}")
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"❌ [AuthService] 创建访问令牌失败 - 数据: {data}, 错误: {str(e)}")
            raise e
    
    def verify_token(self, token: str) -> Optional[str]:
        """验证令牌并返回用户名"""
        try:
            # 记录token验证开始（不记录完整token内容，只记录前后几位）
            token_preview = f"{token[:10]}...{token[-10:]}" if len(token) > 20 else "***"
            logger.info(f"🔍 [AuthService] 开始验证令牌 - Token预览: {token_preview}")
            
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            
            if username is None:
                logger.warning(f"⚠️ [AuthService] 令牌验证失败 - 缺少用户名信息")
                return None
            
            # 检查token是否过期
            exp = payload.get("exp")
            if exp:
                expire_time = datetime.fromtimestamp(exp)
                logger.info(f"✅ [AuthService] 令牌验证成功 - 用户: {username}, 过期时间: {expire_time}")
            else:
                logger.info(f"✅ [AuthService] 令牌验证成功 - 用户: {username}, 无过期时间")
                
            return username
            
        except jwt.ExpiredSignatureError:
            logger.warning(f"⚠️ [AuthService] 令牌已过期 - Token预览: {token_preview}")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"⚠️ [AuthService] 无效令牌 - Token预览: {token_preview}, 错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ [AuthService] 令牌验证异常 - Token预览: {token_preview}, 错误: {str(e)}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            with self._get_db_session() as session:
                stmt = select(User).where(User.username == username)
                result = session.execute(stmt)
                user = result.scalar_one_or_none()
                return user
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def register_user(self, user_data: UserRegister) -> Optional[User]:
        """注册用户"""
        try:
            # 检查用户名是否已存在
            existing_user = self.get_user_by_username(user_data.username)
            if existing_user:
                raise ValueError("用户名已存在")
            
            # 创建新用户
            with self._get_db_session() as session:
                hashed_password = self.get_password_hash(user_data.password)
                new_user = User(
                    username=user_data.username,
                    hashed_password=hashed_password,
                    email=user_data.email,
                    phone=user_data.phone,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                session.add(new_user)
                session.commit()
                session.refresh(new_user)
                
                logger.info(f"用户注册成功: {user_data.username}")
                return new_user
                
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            raise e
    
    def login_user(self, login_data: UserLogin) -> Optional[dict]:
        """用户登录"""
        try:
            # 验证用户
            user = self.authenticate_user(login_data.username, login_data.password)
            if not user:
                return None
            
            # 创建访问令牌
            access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )
            
            # 转换用户数据
            user_response = UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                phone=user.phone,
                is_active=user.is_active,
                created_at=user.created_at.isoformat()
            )
            
            logger.info(f"用户登录成功: {user.username}")
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_response
            }
            
        except Exception as e:
            logger.error(f"用户登录失败: {e}")
            return None
    
    def create_admin_user(self):
        """创建管理员用户"""
        try:
            # 检查是否已存在admin用户
            admin_user = self.get_user_by_username("admin")
            if admin_user:
                logger.info("管理员用户已存在")
                return
            
            # 创建admin用户
            admin_data = UserRegister(
                username="admin",
                password="admin123",
                email="admin@example.com"
            )
            
            self.register_user(admin_data)
            logger.info("管理员用户创建成功: admin/admin123")
            
        except Exception as e:
            logger.error(f"创建管理员用户失败: {e}")
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> Dict[str, Any]:
        """获取当前用户（用于FastAPI依赖注入）"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # 记录认证开始
            token_preview = f"{credentials.credentials[:10]}...{credentials.credentials[-10:]}" if len(credentials.credentials) > 20 else "***"
            logger.info(f"🔐 [AuthService] 开始用户认证 - Token预览: {token_preview}")
            
            # 验证token
            username = self.verify_token(credentials.credentials)
            if username is None:
                logger.warning(f"⚠️ [AuthService] 用户认证失败 - Token验证失败")
                raise credentials_exception
            
            # 获取用户信息
            user = self.get_user_by_username(username)
            if user is None:
                logger.warning(f"⚠️ [AuthService] 用户认证失败 - 用户不存在: {username}")
                raise credentials_exception
            
            if not user.is_active:
                logger.warning(f"⚠️ [AuthService] 用户认证失败 - 用户已被禁用: {username}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="用户已被禁用"
                )
            
            # 返回用户字典
            user_info = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "is_active": user.is_active
            }
            
            logger.info(f"✅ [AuthService] 用户认证成功 - 用户ID: {user.id}, 用户名: {username}")
            return user_info
            
        except HTTPException:
            # 重新抛出HTTP异常
            raise
        except JWTError as e:
            logger.error(f"❌ [AuthService] JWT错误 - 错误: {str(e)}")
            raise credentials_exception
        except Exception as e:
            logger.error(f"❌ [AuthService] 用户认证异常 - 错误: {str(e)}", exc_info=True)
            raise credentials_exception

# 全局认证服务实例
auth_service = AuthService() 