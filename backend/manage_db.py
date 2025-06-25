#!/usr/bin/env python3
"""
数据库管理工具
用于创建、删除、重建数据库表，以及查看数据库状态
"""
import sys
import os

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from backend.src.database.init_db import init_database
from backend.src.database.config import test_connection, get_engine
from backend.src.database.migrations import run_migrations
from sqlalchemy import text, inspect


def check_db_status():
    """检查数据库状态"""
    print("🔍 检查数据库状态...")
    
    if not test_connection():
        print("❌ 数据库连接失败")
        return False
    
    print("✅ 数据库连接正常")
    
    # 检查表是否存在
    engine = get_engine()
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    expected_tables = [
        'users', 'stories', 'locations', 'npcs', 
        'message_types', 'entity_types', 'entities', 'messages'
    ]
    
    print(f"\n📊 数据库表状态:")
    for table in expected_tables:
        status = "✅ 存在" if table in existing_tables else "❌ 不存在"
        print(f"  {table}: {status}")
    
    # 检查基础数据
    try:
        with engine.connect() as conn:
            # 检查用户数量
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"\n👤 用户数量: {user_count}")
            
            # 检查故事数量
            if 'stories' in existing_tables:
                result = conn.execute(text("SELECT COUNT(*) FROM stories"))
                story_count = result.scalar()
                print(f"📚 故事数量: {story_count}")
            
            # 检查消息类型数量
            if 'message_types' in existing_tables:
                result = conn.execute(text("SELECT COUNT(*) FROM message_types"))
                msg_type_count = result.scalar()
                print(f"💬 消息类型数量: {msg_type_count}")
            
            # 检查实体数量
            if 'entities' in existing_tables:
                result = conn.execute(text("SELECT COUNT(*) FROM entities"))
                entity_count = result.scalar()
                print(f"🏷️ 实体数量: {entity_count}")
            
            # 检查消息数量
            if 'messages' in existing_tables:
                result = conn.execute(text("SELECT COUNT(*) FROM messages"))
                message_count = result.scalar()
                print(f"📝 消息数量: {message_count}")
                
    except Exception as e:
        print(f"⚠️ 检查数据时出错: {e}")
    
    return True


def create_db():
    """创建数据库表"""
    print("🚀 创建数据库表...")
    success = init_database(drop_existing=False)
    if success:
        print("✅ 数据库表创建成功")
    else:
        print("❌ 数据库表创建失败")
    return success


def recreate_db():
    """重建数据库表（删除所有数据）"""
    print("⚠️ 警告：这将删除所有现有数据！")
    confirm = input("确认要重建数据库吗？(输入 'YES' 确认): ")
    
    if confirm != "YES":
        print("❌ 操作已取消")
        return False
    
    print("🔄 重建数据库表...")
    success = init_database(drop_existing=True)
    if success:
        print("✅ 数据库表重建成功")
        
        # 运行迁移
        print("🔄 运行数据迁移...")
        story_id = run_migrations()
        if story_id:
            print(f"✅ 数据迁移完成，默认故事ID: {story_id}")
        else:
            print("⚠️ 数据迁移失败")
    else:
        print("❌ 数据库表重建失败")
    
    return success


def migrate_db():
    """运行数据迁移"""
    print("🔄 运行数据迁移...")
    story_id = run_migrations()
    if story_id:
        print(f"✅ 数据迁移完成，默认故事ID: {story_id}")
    else:
        print("❌ 数据迁移失败")
    return story_id is not None


def show_table_info():
    """显示表结构信息"""
    print("📋 显示表结构信息...")
    
    engine = get_engine()
    inspector = inspect(engine)
    
    tables = ['users', 'stories', 'locations', 'npcs', 'message_types', 'entity_types', 'entities', 'messages']
    
    for table_name in tables:
        if table_name in inspector.get_table_names():
            print(f"\n📊 表: {table_name}")
            columns = inspector.get_columns(table_name)
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f", DEFAULT: {col['default']}" if col.get('default') else ""
                print(f"  - {col['name']}: {col['type']} {nullable}{default}")
            
            # 显示索引
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print(f"  📚 索引:")
                for idx in indexes:
                    unique_str = " (UNIQUE)" if idx['unique'] else ""
                    print(f"    - {idx['name']}: {idx['column_names']}{unique_str}")
        else:
            print(f"\n❌ 表 {table_name} 不存在")


def show_sample_data():
    """显示示例数据"""
    print("📋 显示示例数据...")
    
    engine = get_engine()
    
    try:
        with engine.connect() as conn:
            # 用户数据
            print("\n👤 用户数据:")
            result = conn.execute(text("SELECT id, username, email, created_at FROM users LIMIT 5"))
            for row in result:
                print(f"  ID: {row[0]}, 用户名: {row[1]}, 邮箱: {row[2]}, 创建时间: {row[3]}")
            
            # 故事数据
            print("\n📚 故事数据:")
            result = conn.execute(text("SELECT id, name, description, creator_id, created_at FROM stories LIMIT 5"))
            for row in result:
                print(f"  ID: {row[0]}, 名称: {row[1]}, 创建者: {row[3]}, 创建时间: {row[4]}")
            
            # 消息类型数据
            print("\n💬 消息类型:")
            result = conn.execute(text("SELECT id, type_name, description FROM message_types"))
            for row in result:
                print(f"  ID: {row[0]}, 类型: {row[1]}, 描述: {row[2]}")
            
            # 实体类型数据
            print("\n🏷️ 实体类型:")
            result = conn.execute(text("SELECT id, type_name, description FROM entity_types"))
            for row in result:
                print(f"  ID: {row[0]}, 类型: {row[1]}, 描述: {row[2]}")
            
            # 实体数据示例
            print("\n🏷️ 实体数据 (前10个):")
            result = conn.execute(text("""
                SELECT e.id, et.type_name, e.name, e.key_name, e.story_id 
                FROM entities e 
                LEFT JOIN entity_types et ON e.entity_type = et.id 
                LIMIT 10
            """))
            for row in result:
                story_info = f"故事{row[4]}" if row[4] else "通用"
                print(f"  ID: {row[0]}, 类型: {row[1]}, 名称: {row[2]}, 键名: {row[3]}, 所属: {story_info}")
                
    except Exception as e:
        print(f"❌ 显示数据时出错: {e}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("数据库管理工具")
        print("\n用法:")
        print("  python manage_db.py <命令>")
        print("\n可用命令:")
        print("  status    - 检查数据库状态")
        print("  create    - 创建数据库表")
        print("  recreate  - 重建数据库表（删除所有数据）")
        print("  migrate   - 运行数据迁移")
        print("  info      - 显示表结构信息")
        print("  data      - 显示示例数据")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        check_db_status()
    elif command == "create":
        create_db()
    elif command == "recreate":
        recreate_db()
    elif command == "migrate":
        migrate_db()
    elif command == "info":
        show_table_info()
    elif command == "data":
        show_sample_data()
    else:
        print(f"❌ 未知命令: {command}")
        print("运行 'python manage_db.py' 查看帮助")


if __name__ == "__main__":
    main() 