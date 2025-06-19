"""
数据库工具 - 数据库连接和会话管理
"""
import json
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 获取配置文件路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(SRC_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "config.json")


def load_database_config():
    """加载数据库配置"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('db', {})
    except Exception as e:
        print(f"加载数据库配置失败: {e}")
        # 返回默认配置
        return {
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "password",
            "database": "galgame_db"
        }


def get_database_url():
    """获取数据库URL"""
    config = load_database_config()
    
    # 构建PostgreSQL连接URL
    db_url = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    
    return db_url


def create_database_engine():
    """创建数据库引擎"""
    db_url = get_database_url()
    
    try:
        # 创建PostgreSQL引擎
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False  # 设置为True可以看到SQL语句
        )
        return engine
    except Exception as e:
        print(f"创建数据库引擎失败: {e}")
        # 如果PostgreSQL连接失败，使用SQLite作为备用
        print("使用SQLite作为备用数据库")
        return create_engine(
            "sqlite:///./galgame.db",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )


# 创建数据库引擎
engine = create_database_engine()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库"""
    try:
        # 导入所有模型以确保它们被注册
        from models.user_model import User
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库初始化成功")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")


def check_database_connection():
    """检查数据库连接"""
    try:
        db = SessionLocal()
        # 使用text()函数包装SQL语句，解决SQLAlchemy版本兼容性问题
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ 数据库连接正常")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False 