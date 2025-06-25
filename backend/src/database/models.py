"""
数据库ORM模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, UniqueConstraint, Index, CheckConstraint
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


class MessageType(Base):
    """消息类型表模型"""
    __tablename__ = "message_types"
    
    # 主键
    id = Column(Integer, primary_key=True)
    
    # 类型名称，唯一
    type_name = Column(String(30), nullable=False, unique=True)
    
    # 描述
    description = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<MessageType(id={self.id}, type_name='{self.type_name}')>"


class EntityType(Base):
    """实体类型表模型"""
    __tablename__ = "entity_types"
    
    # 主键
    id = Column(Integer, primary_key=True)
    
    # 类型名称，唯一
    type_name = Column(String(30), nullable=False, unique=True)
    
    # 描述
    description = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<EntityType(id={self.id}, type_name='{self.type_name}')>"


class Entity(Base):
    """通用实体表模型"""
    __tablename__ = "entities"
    
    # 主键，自增序列
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 实体类型ID，外键
    entity_type = Column(Integer, ForeignKey("entity_types.id"), nullable=False)
    
    # 故事ID，外键（某些实体属于特定故事）
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=True)
    
    # 实体名称，非空
    name = Column(String(100), nullable=False)
    
    # 程序中使用的键名
    key_name = Column(String(100), nullable=True, index=True)
    
    # 实体描述
    description = Column(Text, nullable=True)
    
    # 元数据，JSON格式
    entity_metadata = Column(JSON, default=dict)
    
    # 创建时间
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # 表约束：同一故事内的key_name唯一
    __table_args__ = (
        UniqueConstraint('story_id', 'key_name', name='uq_entity_story_key'),
        Index('idx_entity_story_key', 'story_id', 'key_name'),
        Index('idx_entity_type', 'entity_type'),
    )
    
    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}', key_name='{self.key_name}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "story_id": self.story_id,
            "name": self.name,
            "key_name": self.key_name,
            "description": self.description,
            "metadata": self.entity_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Message(Base):
    """用户交互消息表模型"""
    __tablename__ = "messages"
    
    # 主键，自增序列
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 用户和故事关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)  # 游戏会话ID
    
    # 消息分类（int型）
    message_type = Column(Integer, nullable=False, index=True)  # 1-6对应不同类型
    sub_type = Column(String(50), nullable=True, index=True)    # 细分类型
    
    # 消息内容
    content = Column(Text, nullable=False)                      # 主要消息内容
    structured_data = Column(JSON, nullable=True)               # 结构化数据（可选）
    
    # 关联信息（int型）
    related_entity = Column(Integer, ForeignKey("entities.id"), nullable=True, index=True)  # 相关实体ID
    
    # 游戏上下文
    location = Column(Integer, ForeignKey("entities.id"), nullable=True, index=True)  # 位置ID
    game_time = Column(DateTime(timezone=True), nullable=True)  # 游戏内时间
    
    # 元数据
    message_metadata = Column(JSON, default=dict)                       # 额外的元数据信息
    
    # 时间戳
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    # 表约束和索引
    __table_args__ = (
        # 复合索引优化查询性能
        Index('idx_messages_user_story_session', 'user_id', 'story_id', 'session_id'),
        Index('idx_messages_type_subtype', 'message_type', 'sub_type'),
        Index('idx_messages_user_type_time', 'user_id', 'message_type', 'created_at'),
        Index('idx_messages_session_time', 'session_id', 'game_time'),
        Index('idx_messages_game_time', 'game_time'),
        # 检查约束
        CheckConstraint('message_type BETWEEN 1 AND 6'),  # 限制message_type范围
    )
    
    def __repr__(self):
        return f"<Message(id={self.id}, user_id={self.user_id}, message_type={self.message_type}, content='{self.content[:50]}...')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "story_id": self.story_id,
            "session_id": self.session_id,
            "message_type": self.message_type,
            "sub_type": self.sub_type,
            "content": self.content,
            "structured_data": self.structured_data,
            "related_entity": self.related_entity,
            "location": self.location,
            "game_time": self.game_time.isoformat() if self.game_time else None,
            "metadata": self.message_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        } 