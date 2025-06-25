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
from backend.src.database.models import Base, Story, Location, NPC, User, Entity, EntityType, MessageType
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
        
        # 迁移实体数据
        print("🔄 迁移实体数据...")
        migrate_entities(session, default_story.id)
        
        session.commit()
        print("✅ 默认故事数据迁移完成")
        return default_story.id
        
    except Exception as e:
        session.rollback()
        print(f"❌ 迁移失败: {e}")
        return None
    finally:
        session.close()


def migrate_entities(session, story_id):
    """迁移实体数据"""
    try:
        # NPC实体（故事相关）
        npc_entities = [
            (1, story_id, '林凯', 'linkai'),
            (1, story_id, '林若曦', 'linruoxi'),
            (1, story_id, '张雨晴', 'zhangyuqing'),
        ]
        
        for entity_type, story_id_val, name, key_name in npc_entities:
            existing = session.query(Entity).filter_by(story_id=story_id_val, key_name=key_name).first()
            if not existing:
                entity = Entity(
                    entity_type=entity_type,
                    story_id=story_id_val,
                    name=name,
                    key_name=key_name,
                    description=f"NPC角色: {name}"
                )
                session.add(entity)
                print(f"✅ 创建NPC实体: {name}")
        
        # 位置实体（故事相关）
        location_entities = [
            (2, story_id, '林凯房间', 'linkai_room'),
            (2, story_id, '林若曦房间', 'linruoxi_room'),
            (2, story_id, '张雨晴房间', 'zhangyuqing_room'),
            (2, story_id, '客厅', 'livingroom'),
            (2, story_id, '厨房', 'kitchen'),
            (2, story_id, '卫生间', 'bathroom'),
        ]
        
        for entity_type, story_id_val, name, key_name in location_entities:
            existing = session.query(Entity).filter_by(story_id=story_id_val, key_name=key_name).first()
            if not existing:
                entity = Entity(
                    entity_type=entity_type,
                    story_id=story_id_val,
                    name=name,
                    key_name=key_name,
                    description=f"游戏位置: {name}"
                )
                session.add(entity)
                print(f"✅ 创建位置实体: {name}")
        
        # 物品实体（通用）
        item_entities = [
            (3, None, '苹果', 'apple'),
            (3, None, '手机', 'phone'),
            (3, None, '书籍', 'book'),
            (3, None, '咖啡', 'coffee'),
        ]
        
        for entity_type, story_id_val, name, key_name in item_entities:
            existing = session.query(Entity).filter_by(story_id=story_id_val, key_name=key_name).first()
            if not existing:
                entity = Entity(
                    entity_type=entity_type,
                    story_id=story_id_val,
                    name=name,
                    key_name=key_name,
                    description=f"游戏物品: {name}"
                )
                session.add(entity)
                print(f"✅ 创建物品实体: {name}")
        
        # 系统实体（通用）
        system_entities = [
            (4, None, '系统', 'system'),
            (4, None, '游戏引擎', 'game_engine'),
        ]
        
        for entity_type, story_id_val, name, key_name in system_entities:
            existing = session.query(Entity).filter_by(story_id=story_id_val, key_name=key_name).first()
            if not existing:
                entity = Entity(
                    entity_type=entity_type,
                    story_id=story_id_val,
                    name=name,
                    key_name=key_name,
                    description=f"系统实体: {name}"
                )
                session.add(entity)
                print(f"✅ 创建系统实体: {name}")
        
        print("✅ 实体数据迁移完成")
        
    except Exception as e:
        print(f"❌ 实体数据迁移失败: {e}")
        raise


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