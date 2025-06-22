"""
数据库初始化 - 自动建表和表结构同步
"""
import sys
import os
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .config import engine, Base, test_connection
from .models import User, Story, Location, NPC

def check_table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return table_name in tables
    except Exception as e:
        print(f"❌ 检查表 {table_name} 是否存在失败: {e}")
        return False

def create_tables():
    """创建所有表"""
    try:
        print("🏗️ 开始创建数据库表...")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        print("✅ 数据库表创建完成")
        
        # 验证表是否创建成功
        tables_to_verify = ["users", "stories", "locations", "npcs"]
        for table_name in tables_to_verify:
            if check_table_exists(table_name):
                print(f"✅ {table_name} 表创建成功")
            else:
                print(f"❌ {table_name} 表创建失败")
            
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ 创建数据库表失败: {e}")
        return False

def drop_tables():
    """删除所有表（慎用！）"""
    try:
        print("🗑️ 开始删除数据库表...")
        Base.metadata.drop_all(bind=engine)
        print("✅ 数据库表删除完成")
        return True
    except SQLAlchemyError as e:
        print(f"❌ 删除数据库表失败: {e}")
        return False

def sync_table_structure():
    """同步表结构（检查并创建缺失的表）"""
    try:
        print("🔄 开始同步数据库表结构...")
        
        # 检查每个表是否存在，不存在则创建
        tables_to_check = {
            "users": User.__table__,
            "stories": Story.__table__,
            "locations": Location.__table__,
            "npcs": NPC.__table__
        }
        
        for table_name, table_obj in tables_to_check.items():
            if check_table_exists(table_name):
                print(f"✅ 表 {table_name} 已存在")
            else:
                print(f"⚠️ 表 {table_name} 不存在，正在创建...")
                table_obj.create(bind=engine)
                print(f"✅ 表 {table_name} 创建成功")
        
        print("✅ 数据库表结构同步完成")
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ 同步数据库表结构失败: {e}")
        return False

def verify_table_structure():
    """验证表结构是否正确"""
    try:
        print("🔍 验证数据库表结构...")
        
        inspector = inspect(engine)
        
        # 验证users表结构
        if check_table_exists("users"):
            columns = inspector.get_columns("users")
            indexes = inspector.get_indexes("users")
            
            print(f"📋 users表结构:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']} {'NOT NULL' if not col['nullable'] else 'NULL'}")
            
            print(f"📋 users表索引:")
            for idx in indexes:
                print(f"  - {idx['name']}: {idx['column_names']} {'UNIQUE' if idx['unique'] else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证表结构失败: {e}")
        return False

def init_database(drop_existing: bool = False):
    """
    初始化数据库
    
    Args:
        drop_existing: 是否删除现有表重新创建
    """
    print("🚀 开始初始化数据库...")
    
    # 1. 测试数据库连接
    if not test_connection():
        print("❌ 数据库连接失败，初始化中止")
        return False
    
    try:
        # 2. 如果需要，删除现有表
        if drop_existing:
            print("⚠️ 删除现有表...")
            drop_tables()
        
        # 3. 创建/同步表结构
        if drop_existing:
            success = create_tables()
        else:
            success = sync_table_structure()
        
        if not success:
            return False
        
        # 4. 验证表结构
        verify_table_structure()
        
        print("🎉 数据库初始化完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

if __name__ == "__main__":
    # 直接运行此脚本进行数据库初始化
    init_database(drop_existing=False) 