"""
数据库ORM模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from .config import Base

class User(Base):
    """用户表模型"""
    __tablename__ = "users"
    
    # 主键，自增序列
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 用户名，非空，唯一
    username = Column(String(50), nullable=False, unique=True, index=True)
    
    # 邮箱，可空，唯一
    email = Column(String(100), nullable=True, unique=True, index=True)
    
    # 手机号，可空，唯一
    phone = Column(String(20), nullable=True, unique=True, index=True)
    
    # 密码哈希，非空
    hashed_password = Column(String(255), nullable=False)
    
    # 是否激活，默认True
    is_active = Column(Boolean, default=True)
    
    # 创建时间，默认当前时间
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # 更新时间，可空
    updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关联关系
    stories = relationship("Story", back_populates="creator")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Story(Base):
    """故事表模型"""
    __tablename__ = "stories"
    
    # 主键，自增序列
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 故事名称，非空
    name = Column(String(100), nullable=False)
    
    # 故事描述，可空
    description = Column(Text, nullable=True)
    
    # 创建者用户ID，外键
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 游戏配置JSON，包含用户名、初始位置、初始时间等
    game_config = Column(JSON, nullable=True)
    
    # 是否激活，默认True
    is_active = Column(Boolean, default=True)
    
    # 创建时间，默认当前时间
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # 更新时间，可空
    updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关联关系
    creator = relationship("User", back_populates="stories")
    locations = relationship("Location", back_populates="story", cascade="all, delete-orphan")
    npcs = relationship("NPC", back_populates="story", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Story(id={self.id}, name='{self.name}', creator_id={self.creator_id})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "creator_id": self.creator_id,
            "game_config": self.game_config,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Location(Base):
    """地图位置表模型"""
    __tablename__ = "locations"
    
    # 主键，自增序列
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 故事ID，外键
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False, index=True)
    
    # 位置键名，在同一故事内唯一
    key = Column(String(50), nullable=False, index=True)
    
    # 位置中文名称，非空
    name = Column(String(100), nullable=False)
    
    # 位置英文名称，可空
    en_name = Column(String(100), nullable=True)
    
    # 位置描述，可空
    description = Column(Text, nullable=True)
    
    # 连接的位置列表，JSON格式存储
    connections = Column(JSON, nullable=True, default=list)
    
    # 创建时间，默认当前时间
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # 更新时间，可空
    updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关联关系
    story = relationship("Story", back_populates="locations")
    
    # 表约束：同一故事内位置键名唯一
    __table_args__ = (
        UniqueConstraint('story_id', 'key', name='uq_location_story_key'),
        Index('idx_location_story_key', 'story_id', 'key'),
    )
    
    def __repr__(self):
        return f"<Location(id={self.id}, story_id={self.story_id}, key='{self.key}', name='{self.name}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "story_id": self.story_id,
            "key": self.key,
            "name": self.name,
            "en_name": self.en_name,
            "description": self.description,
            "connections": self.connections or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class NPC(Base):
    """NPC角色表模型"""
    __tablename__ = "npcs"
    
    # 主键，自增序列
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 故事ID，外键
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False, index=True)
    
    # NPC名称，非空
    name = Column(String(100), nullable=False)
    
    # NPC性格描述，可空
    personality = Column(Text, nullable=True)
    
    # NPC背景描述，可空
    background = Column(Text, nullable=True)
    
    # NPC当前心情，可空
    mood = Column(String(50), nullable=True, default="平静")
    
    # NPC人物关系，JSON格式存储
    relations = Column(JSON, nullable=True, default=dict)
    
    # NPC日程安排，JSON格式存储
    schedule = Column(JSON, nullable=True, default=list)
    
    # 创建时间，默认当前时间
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # 更新时间，可空
    updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关联关系
    story = relationship("Story", back_populates="npcs")
    
    # 表约束：同一故事内NPC名称唯一
    __table_args__ = (
        UniqueConstraint('story_id', 'name', name='uq_npc_story_name'),
        Index('idx_npc_story_name', 'story_id', 'name'),
    )
    
    def __repr__(self):
        return f"<NPC(id={self.id}, story_id={self.story_id}, name='{self.name}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "story_id": self.story_id,
            "name": self.name,
            "personality": self.personality,
            "background": self.background,
            "mood": self.mood,
            "relations": self.relations or {},
            "schedule": self.schedule or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        } 