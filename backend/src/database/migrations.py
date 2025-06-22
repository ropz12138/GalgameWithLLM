"""
数据库迁移脚本
"""
import sys
import os
from sqlalchemy import text

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_ROOT)

from backend.src.database.config import get_engine, get_session
from backend.src.database.models import Base, Story, Location, NPC, User
from data.characters import all_actresses
from data.locations import all_locations_data, location_connections


def create_tables():
    """创建所有表"""
    print("🔄 创建数据库表...")
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")


def migrate_default_story():
    """迁移默认故事数据"""
    print("🔄 迁移默认故事数据...")
    
    session = get_session()
    try:
        # 检查是否已有默认故事
        existing_story = session.query(Story).filter_by(name="默认故事").first()
        if existing_story:
            print("ℹ️ 默认故事已存在，跳过迁移")
            return existing_story.id
        
        # 获取admin用户
        admin_user = session.query(User).filter_by(username="admin").first()
        if not admin_user:
            print("❌ 未找到admin用户，请先创建用户")
            return None
        
        # 创建默认故事
        default_story = Story(
            name="默认故事",
            description="系统默认的文字游戏故事",
            creator_id=admin_user.id,
            game_config={
                "user_name": "林凯",
                "user_place": "linkai_room",
                "init_time": "2024-01-15 07:00"
            }
        )
        session.add(default_story)
        session.flush()  # 获取story_id
        
        print(f"✅ 创建默认故事，ID: {default_story.id}")
        
        # 迁移位置数据
        print("🔄 迁移位置数据...")
        for location_key, location_data in all_locations_data.items():
            location = Location(
                story_id=default_story.id,
                key=location_key,
                name=location_data.get("name", ""),
                en_name=location_data.get("en_name", location_key),
                description=location_data.get("description", ""),
                connections=location_connections.get(location_key, [])
            )
            session.add(location)
        
        print(f"✅ 迁移了 {len(all_locations_data)} 个位置")
        
        # 迁移NPC数据
        print("🔄 迁移NPC数据...")
        for npc_data in all_actresses:
            npc = NPC(
                story_id=default_story.id,
                name=npc_data.get("name", ""),
                personality=npc_data.get("personality", ""),
                background=npc_data.get("background", ""),
                mood=npc_data.get("mood", "平静"),
                relations=npc_data.get("relations", {}),
                schedule=npc_data.get("schedule", [])
            )
            session.add(npc)
        
        print(f"✅ 迁移了 {len(all_actresses)} 个NPC")
        
        session.commit()
        print("✅ 默认故事数据迁移完成")
        return default_story.id
        
    except Exception as e:
        session.rollback()
        print(f"❌ 迁移失败: {e}")
        return None
    finally:
        session.close()


def run_migrations():
    """执行所有迁移"""
    print("🚀 开始数据库迁移...")
    
    # 1. 创建表
    create_tables()
    
    # 2. 迁移默认故事数据
    story_id = migrate_default_story()
    
    if story_id:
        print(f"✅ 数据库迁移完成，默认故事ID: {story_id}")
    else:
        print("❌ 数据库迁移失败")
    
    return story_id


if __name__ == "__main__":
    run_migrations() 