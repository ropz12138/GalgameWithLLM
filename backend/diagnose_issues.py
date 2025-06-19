#!/usr/bin/env python3
"""
问题诊断脚本
分析数据库和系统问题
"""
import sys
import os

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, "src"))

from sqlalchemy import text
from utils.database import engine, Base, SessionLocal
from models.user_model import User


def diagnose_database():
    """诊断数据库问题"""
    print("=" * 60)
    print("🔍 数据库问题诊断")
    print("=" * 60)
    
    # 1. 检查数据库连接
    print("1. 🔌 检查数据库连接...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("   ✅ 数据库连接正常")
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")
        return False
    
    # 2. 检查表是否存在
    print("2. 📋 检查数据库表...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name = 'users';
            """))
            tables = result.fetchall()
            if tables:
                print("   ✅ users表存在")
            else:
                print("   ❌ users表不存在")
                return False
    except Exception as e:
        print(f"   ❌ 检查表失败: {e}")
        return False
    
    # 3. 检查表结构
    print("3. 🏗️ 检查表结构...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position;
            """))
            columns = result.fetchall()
            print(f"   📊 表有 {len(columns)} 个字段:")
            for col in columns:
                print(f"      - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
    except Exception as e:
        print(f"   ❌ 检查表结构失败: {e}")
        return False
    
    # 4. 测试SQLAlchemy ORM
    print("4. 🐍 测试SQLAlchemy ORM...")
    try:
        db = SessionLocal()
        users = db.query(User).all()
        print(f"   ✅ ORM查询成功，当前有 {len(users)} 个用户")
        db.close()
    except Exception as e:
        print(f"   ❌ ORM查询失败: {e}")
        return False
    
    return True


def diagnose_models():
    """诊断模型问题"""
    print("\n" + "=" * 60)
    print("🏗️ 模型问题诊断")
    print("=" * 60)
    
    # 1. 检查Base类
    print("1. 🔧 检查Base类...")
    try:
        print(f"   📊 Base类: {Base}")
        print(f"   📊 Base.metadata: {Base.metadata}")
        print(f"   📊 注册的表: {list(Base.metadata.tables.keys())}")
    except Exception as e:
        print(f"   ❌ 检查Base类失败: {e}")
        return False
    
    # 2. 检查User模型
    print("2. 👤 检查User模型...")
    try:
        print(f"   📊 User.__tablename__: {User.__tablename__}")
        print(f"   📊 User.__table__: {User.__table__}")
        print(f"   📊 User.__table__.columns: {list(User.__table__.columns.keys())}")
    except Exception as e:
        print(f"   ❌ 检查User模型失败: {e}")
        return False
    
    return True


def diagnose_imports():
    """诊断导入问题"""
    print("\n" + "=" * 60)
    print("📦 导入问题诊断")
    print("=" * 60)
    
    # 检查关键模块导入
    modules_to_check = [
        ("sqlalchemy", "SQLAlchemy"),
        ("passlib", "PassLib"),
        ("jose", "PyJWT"),
        ("fastapi", "FastAPI"),
        ("pydantic", "Pydantic")
    ]
    
    for module_name, display_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"   ✅ {display_name} 导入成功")
        except ImportError as e:
            print(f"   ❌ {display_name} 导入失败: {e}")
    
    return True


def main():
    """主诊断函数"""
    print("🎮 LLM文字游戏 - 问题诊断工具")
    print("=" * 60)
    
    # 诊断数据库
    db_ok = diagnose_database()
    
    # 诊断模型
    models_ok = diagnose_models()
    
    # 诊断导入
    imports_ok = diagnose_imports()
    
    print("\n" + "=" * 60)
    print("📊 诊断结果总结")
    print("=" * 60)
    print(f"   🔌 数据库: {'✅ 正常' if db_ok else '❌ 异常'}")
    print(f"   🏗️ 模型: {'✅ 正常' if models_ok else '❌ 异常'}")
    print(f"   📦 导入: {'✅ 正常' if imports_ok else '❌ 异常'}")
    
    if db_ok and models_ok and imports_ok:
        print("\n🎉 所有检查通过！系统应该可以正常运行")
        print("💡 建议: 运行 python fix_database.py 进行最终修复")
    else:
        print("\n⚠️ 发现问题，请根据上述诊断结果进行修复")
        print("💡 建议: 运行 python fix_database.py 进行修复")


if __name__ == "__main__":
    main() 