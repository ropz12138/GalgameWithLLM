#!/usr/bin/env python3
"""
数据库修复脚本
解决表创建和初始化问题
"""
import sys
import os

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, "src"))

from utils.database import engine, Base, SessionLocal
from models.user_model import User
from services.auth_service import AuthService
from models.user_model import UserCreate


def check_tables_exist():
    """检查表是否存在"""
    print("🔍 检查数据库表...")
    try:
        # 检查users表是否存在
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """))
            exists = result.scalar()
            if exists:
                print("✅ users表已存在")
                return True
            else:
                print("❌ users表不存在")
                return False
    except Exception as e:
        print(f"❌ 检查表失败: {e}")
        return False


def create_tables():
    """创建数据库表"""
    print("🗄️ 创建数据库表...")
    try:
        # 删除所有表（如果存在）
        Base.metadata.drop_all(bind=engine)
        print("🗑️ 已删除旧表")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
        return True
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        return False


def test_user_operations():
    """测试用户操作"""
    print("👤 测试用户操作...")
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
        print("✅ 用户创建测试成功")
        print(f"  👤 用户ID: {result['user']['id']}")
        print(f"  👤 用户名: {result['user']['username']}")
        
        # 查询用户
        user = db.query(User).filter(User.username == "test_user").first()
        if user:
            print("✅ 用户查询测试成功")
        else:
            print("❌ 用户查询测试失败")
        
        # 删除测试用户
        db.delete(user)
        db.commit()
        print("✅ 用户删除测试成功")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ 用户操作测试失败: {e}")
        return False


def main():
    """主修复函数"""
    print("=" * 60)
    print("🔧 数据库修复工具")
    print("=" * 60)
    
    # 导入text函数
    from sqlalchemy import text
    
    # 检查表是否存在
    if check_tables_exist():
        print("📋 表已存在，跳过创建")
    else:
        # 创建表
        if not create_tables():
            print("❌ 表创建失败")
            return
    
    # 测试用户操作
    if not test_user_operations():
        print("❌ 用户操作测试失败")
        return
    
    print("\n" + "=" * 60)
    print("✅ 数据库修复完成！")
    print("=" * 60)
    print("🎉 现在可以正常启动系统了")
    print("  运行: ./start_simple.sh")


if __name__ == "__main__":
    main() 