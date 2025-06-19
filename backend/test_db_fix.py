#!/usr/bin/env python3
"""
数据库连接测试脚本
用于测试修复后的数据库连接
"""
import sys
import os

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, "src"))

from utils.database import check_database_connection, init_db
from models.user_model import User, UserCreate
from services.auth_service import AuthService
from utils.database import SessionLocal


def test_database_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("🧪 数据库连接测试")
    print("=" * 60)
    
    # 测试连接
    print("🔍 测试数据库连接...")
    if check_database_connection():
        print("✅ 数据库连接测试通过")
        return True
    else:
        print("❌ 数据库连接测试失败")
        return False


def test_database_initialization():
    """测试数据库初始化"""
    print("\n🗄️ 测试数据库初始化...")
    try:
        init_db()
        print("✅ 数据库初始化测试通过")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化测试失败: {e}")
        return False


def test_user_creation():
    """测试用户创建"""
    print("\n👤 测试用户创建...")
    try:
        db = SessionLocal()
        auth_service = AuthService()
        
        # 创建测试用户
        user_data = UserCreate(
            username="test_user",
            password="test123456",
            email="test@example.com",
            phone="13800138000"
        )
        
        result = auth_service.register_user(db, user_data)
        print("✅ 用户创建测试通过")
        print(f"  👤 用户ID: {result['user']['id']}")
        print(f"  👤 用户名: {result['user']['username']}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ 用户创建测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🎮 LLM文字游戏 - 数据库修复测试")
    print("=" * 60)
    
    # 测试数据库连接
    if not test_database_connection():
        print("\n❌ 数据库连接测试失败，请检查配置")
        return
    
    # 测试数据库初始化
    if not test_database_initialization():
        print("\n❌ 数据库初始化测试失败")
        return
    
    # 测试用户创建
    if not test_user_creation():
        print("\n❌ 用户创建测试失败")
        return
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！数据库修复成功")
    print("=" * 60)
    print("🎉 现在可以正常启动系统了")
    print("  运行: ./start_full_system.sh")


if __name__ == "__main__":
    main() 