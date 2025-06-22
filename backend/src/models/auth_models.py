"""
认证相关的数据模型
"""
from pydantic import BaseModel, validator
from typing import Optional

class UserRegister(BaseModel):
    """用户注册模型"""
    username: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None
    
    @validator('username')
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError('用户名长度至少3个字符')
        if len(v) > 50:
            raise ValueError('用户名长度不能超过50个字符')
        return v
    
    @validator('password')
    def password_must_be_valid(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少6个字符')
        return v

class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str

class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    """Token数据模型"""
    username: Optional[str] = None 