#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表和初始数据
"""
import sys
import os

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, "src"))

from utils.database import init_db, check_database_connection, engine, Base
from models.user_model import User, UserCreate
from services.auth_service import AuthService
from utils.database import SessionLocal


def create_sample_user():
    """创建示例用户"""
    try:
        db = SessionLocal()
        auth_service = AuthService()
        
        # 检查是否已存在示例用户
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("✅ 示例用户已存在")
            return
        
        # 创建示例用户
        user_data = UserCreate(
            username="admin",
            password="admin123",
            email="admin@example.com",
            phone="13800138000"
        )
        
        result = auth_service.register_user(db, user_data)
        print("✅ 示例用户创建成功:")
        print(f"  👤 用户名: {result['user']['username']}")
        print(f"  📧 邮箱: {result['user']['email']}")
        print(f"  📱 电话: {result['user']['phone']}")
        
    except Exception as e:
        print(f"❌ 创建示例用户失败: {e}")
    finally:
        db.close()


def ensure_tables_exist():
    """确保数据库表存在"""
    print("🔍 检查数据库表...")
    try:
        # 强制创建所有表
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ 数据库表检查/创建完成")
        return True
    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🗄️ 数据库初始化工具")
    print("=" * 60)
    
    # 检查数据库连接
    print("🔍 检查数据库连接...")
    if not check_database_connection():
        print("❌ 数据库连接失败，请检查配置")
        return
    
    # 确保表存在
    if not ensure_tables_exist():
        print("❌ 表创建失败")
        return
    
    # 创建示例用户
    print("👤 创建示例用户...")
    create_sample_user()
    
    print("=" * 60)
    print("✅ 数据库初始化完成")
    print("=" * 60)
    print("📝 示例用户信息:")
    print("  👤 用户名: admin")
    print("  🔑 密码: admin123")
    print("  📧 邮箱: admin@example.com")
    print("")
    print("🔐 认证端点:")
    print("  - 注册: POST http://localhost:8001/auth/register")
    print("  - 登录: POST http://localhost:8001/auth/login")
    print("  - 用户信息: GET http://localhost:8001/auth/me")
    print("=" * 60)


if __name__ == "__main__":
    main() 