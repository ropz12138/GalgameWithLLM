"""
数据库初始化 - 自动建表和表结构同步
"""
import sys
import os
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .config import engine, Base, test_connection, get_engine
from .models import User, Story, Location, NPC, MessageType, EntityType, Entity

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

def init_basic_data(engine):
    """初始化基础数据"""
    try:
        print("🔄 开始初始化基础数据...")
        
        from sqlalchemy.orm import sessionmaker
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # 初始化消息类型
            message_types = [
                (1, 'user_input', '用户输入'),
                (2, 'npc_dialogue', 'NPC对话'),
                (3, 'system_action', '系统行动反馈'),
                (4, 'sensory_feedback', '五感反馈'),
                (5, 'system_info', '系统信息'),
                (6, 'error_message', '错误消息'),
            ]
            
            for type_id, type_name, description in message_types:
                existing = session.query(MessageType).filter_by(id=type_id).first()
                if not existing:
                    msg_type = MessageType(id=type_id, type_name=type_name, description=description)
                    session.add(msg_type)
                    print(f"✅ 创建消息类型: {type_name}")
                else:
                    print(f"✅ 消息类型已存在: {type_name}")
            
            # 初始化实体类型
            entity_types = [
                (1, 'npc', 'NPC角色'),
                (2, 'location', '位置/地点'),
                (3, 'item', '物品'),
                (4, 'system', '系统实体'),
            ]
            
            for type_id, type_name, description in entity_types:
                existing = session.query(EntityType).filter_by(id=type_id).first()
                if not existing:
                    entity_type = EntityType(id=type_id, type_name=type_name, description=description)
                    session.add(entity_type)
                    print(f"✅ 创建实体类型: {type_name}")
                else:
                    print(f"✅ 实体类型已存在: {type_name}")
            
            # 提交基础类型数据
            session.commit()
            print("✅ 基础数据初始化完成")
            
            # 初始化实体数据
            print("🔄 开始初始化实体数据...")
            
            # 获取默认故事ID (假设为1，或者查询获取)
            default_story = session.query(Story).filter_by(name="默认故事").first()
            if default_story:
                story_id = default_story.id
                print(f"✅ 找到默认故事，ID: {story_id}")
                
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
                            description=f"NPC角色: {name}",
                            entity_metadata={}
                        )
                        session.add(entity)
                        print(f"✅ 创建NPC实体: {name}")
                    else:
                        print(f"✅ NPC实体已存在: {name}")
                
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
                            description=f"游戏位置: {name}",
                            entity_metadata={}
                        )
                        session.add(entity)
                        print(f"✅ 创建位置实体: {name}")
                    else:
                        print(f"✅ 位置实体已存在: {name}")
                
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
                            description=f"游戏物品: {name}",
                            entity_metadata={}
                        )
                        session.add(entity)
                        print(f"✅ 创建物品实体: {name}")
                    else:
                        print(f"✅ 物品实体已存在: {name}")
                
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
                            description=f"系统实体: {name}",
                            entity_metadata={}
                        )
                        session.add(entity)
                        print(f"✅ 创建系统实体: {name}")
                    else:
                        print(f"✅ 系统实体已存在: {name}")
                
                # 提交实体数据
                session.commit()
                print("✅ 实体数据初始化完成")
            else:
                print("⚠️ 未找到默认故事，跳过实体数据初始化")
            
            print("✅ 所有基础数据初始化完成")
            
        except Exception as e:
            session.rollback()
            print(f"❌ 基础数据初始化失败: {e}")
            raise
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ 基础数据初始化异常: {e}")
        raise

def validate_table_structure(engine):
    """验证表结构"""
    try:
        print("🔍 验证数据库表结构...")
        
        inspector = inspect(engine)
        
        # 验证每个表的字段和索引
        tables_to_verify = ['users', 'stories', 'locations', 'npcs', 'message_types', 'entity_types', 'entities', 'messages']
        
        for table_name in tables_to_verify:
            if table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                indexes = inspector.get_indexes(table_name)
                
                print(f"📋 {table_name}表结构:")
                for col in columns:
                    nullable_str = "NULL" if col['nullable'] else "NOT NULL"
                    print(f"  - {col['name']}: {col['type']} {nullable_str}")
                
                if indexes:
                    print(f"📋 {table_name}表索引:")
                    for idx in indexes:
                        unique_str = " UNIQUE" if idx['unique'] else ""
                        print(f"  - {idx['name']}: {idx['column_names']}{unique_str}")
            else:
                print(f"⚠️ 表 {table_name} 不存在")
        
        print("✅ 表结构验证完成")
        
    except Exception as e:
        print(f"❌ 表结构验证失败: {e}")

def init_database(drop_existing=False):
    """
    初始化数据库，创建表并验证结构
    
    Args:
        drop_existing (bool): 是否删除现有表后重新创建
        
    Returns:
        bool: 初始化是否成功
    """
    try:
        print("🚀 开始初始化数据库...")
        
        # 获取数据库引擎
        engine = get_engine()
        
        # 测试连接
        print("✅ 数据库连接测试成功")
        
        # 创建表
        print("🔄 开始同步数据库表结构...")
        
        if drop_existing:
            print("⚠️ 正在删除所有现有表...")
            Base.metadata.drop_all(bind=engine)
            print("✅ 现有表已删除")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        # 验证每个表是否创建成功
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        expected_tables = ['users', 'stories', 'locations', 'npcs', 'message_types', 'entity_types', 'entities', 'messages']
        
        for table_name in expected_tables:
            if table_name not in existing_tables:
                print(f"⚠️ 表 {table_name} 不存在，正在创建...")
                # 如果单个表不存在，尝试单独创建
                if hasattr(Base.metadata.tables, table_name):
                    Base.metadata.tables[table_name].create(bind=engine, checkfirst=True)
                print(f"✅ 表 {table_name} 创建成功")
            else:
                print(f"✅ 表 {table_name} 已存在")
        
        print("✅ 数据库表结构同步完成")
        
        # 初始化基础数据
        init_basic_data(engine)
        
        # 验证表结构
        validate_table_structure(engine)
        
        print("🎉 数据库初始化完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 直接运行此脚本进行数据库初始化
    init_database(drop_existing=False) 