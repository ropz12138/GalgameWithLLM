"""
数据库配置
"""
import json
import os
from typing import Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 读取配置文件
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "config.json")

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return {}

def get_database_url() -> str:
    """获取数据库连接URL"""
    config = load_config()
    db_config = config.get("db", {})
    
    return f"postgresql://{db_config.get('user', 'charlie')}:{db_config.get('password', '123456')}@{db_config.get('host', 'localhost')}:{db_config.get('port', 5432)}/{db_config.get('database', 'role_play')}"

# 加载配置
config = load_config()
db_config = config.get("db", {})

# 数据库连接配置
DATABASE_URL = get_database_url()

print(f"🔗 数据库连接URL: {DATABASE_URL.replace(db_config.get('password', ''), '***')}")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False  # 设置为True可以看到SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建ORM基类
Base = declarative_base()

def get_db():
    """获取数据库会话（用于FastAPI依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_session():
    """获取数据库会话（用于服务层直接调用）"""
    return SessionLocal()

def get_engine():
    """获取数据库引擎"""
    return engine

def test_connection():
    """测试数据库连接"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ 数据库连接测试成功")
            return True
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False 