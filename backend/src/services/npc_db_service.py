"""
NPC数据库服务层 - 处理NPC相关的数据库操作
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..database.config import get_session
from ..database.models import NPC, Story


class NPCDBService:
    """NPC数据库服务类"""
    
    def __init__(self):
        pass
    
    def create_npc(self, story_id: int, name: str, personality: Optional[str] = None,
                   background: Optional[str] = None, mood: str = "平静",
                   relations: Optional[Dict[str, Any]] = None,
                   schedule: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        创建新NPC
        
        Args:
            story_id: 故事ID
            name: NPC名称
            personality: 性格描述
            background: 背景描述
            mood: 当前心情
            relations: 人物关系
            schedule: 日程安排
            
        Returns:
            创建结果
        """
        session = get_session()
        try:
            # 检查故事是否存在
            story = session.query(Story).filter_by(id=story_id, is_active=True).first()
            if not story:
                return {"success": False, "error": "故事不存在"}
            
            # 检查NPC名称是否重复
            existing_npc = session.query(NPC).filter_by(story_id=story_id, name=name).first()
            if existing_npc:
                return {"success": False, "error": "NPC名称已存在"}
            
            # 创建NPC
            npc = NPC(
                story_id=story_id,
                name=name,
                personality=personality,
                background=background,
                mood=mood,
                relations=relations or {},
                schedule=schedule or []
            )
            session.add(npc)
            session.commit()
            
            return {
                "success": True,
                "data": npc.to_dict()
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": f"创建NPC失败: {str(e)}"}
        finally:
            session.close()
    
    def get_npcs_by_story(self, story_id: int) -> Dict[str, Any]:
        """
        获取故事的所有NPC
        
        Args:
            story_id: 故事ID
            
        Returns:
            NPC列表
        """
        session = get_session()
        try:
            npcs = session.query(NPC).filter_by(story_id=story_id).all()
            
            return {
                "success": True,
                "data": [npc.to_dict() for npc in npcs]
            }
            
        except Exception as e:
            return {"success": False, "error": f"获取NPC列表失败: {str(e)}"}
        finally:
            session.close()
    
    def get_npc_by_name(self, story_id: int, name: str) -> Dict[str, Any]:
        """
        根据名称获取NPC
        
        Args:
            story_id: 故事ID
            name: NPC名称
            
        Returns:
            NPC信息
        """
        session = get_session()
        try:
            npc = session.query(NPC).filter_by(story_id=story_id, name=name).first()
            if not npc:
                return {"success": False, "error": "NPC不存在"}
            
            return {
                "success": True,
                "data": npc.to_dict()
            }
            
        except Exception as e:
            return {"success": False, "error": f"获取NPC失败: {str(e)}"}
        finally:
            session.close()
    
    def update_npc(self, npc_id: int, **kwargs) -> Dict[str, Any]:
        """
        更新NPC信息
        
        Args:
            npc_id: NPC ID
            **kwargs: 要更新的字段
            
        Returns:
            更新结果
        """
        session = get_session()
        try:
            npc = session.query(NPC).filter_by(id=npc_id).first()
            if not npc:
                return {"success": False, "error": "NPC不存在"}
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(npc, key) and key not in ['id', 'story_id', 'created_at']:
                    setattr(npc, key, value)
            
            session.commit()
            
            return {
                "success": True,
                "data": npc.to_dict()
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": f"更新NPC失败: {str(e)}"}
        finally:
            session.close()
    
    def update_npc_schedule(self, npc_id: int, schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        更新NPC日程表
        
        Args:
            npc_id: NPC ID
            schedule: 新的日程表
            
        Returns:
            更新结果
        """
        session = get_session()
        try:
            npc = session.query(NPC).filter_by(id=npc_id).first()
            if not npc:
                return {"success": False, "error": "NPC不存在"}
            
            npc.schedule = schedule
            session.commit()
            
            return {
                "success": True,
                "data": npc.to_dict()
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": f"更新NPC日程表失败: {str(e)}"}
        finally:
            session.close()
    
    def update_npc_relations(self, npc_id: int, relations: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新NPC人物关系
        
        Args:
            npc_id: NPC ID
            relations: 新的人物关系
            
        Returns:
            更新结果
        """
        session = get_session()
        try:
            npc = session.query(NPC).filter_by(id=npc_id).first()
            if not npc:
                return {"success": False, "error": "NPC不存在"}
            
            npc.relations = relations
            session.commit()
            
            return {
                "success": True,
                "data": npc.to_dict()
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": f"更新NPC人物关系失败: {str(e)}"}
        finally:
            session.close()
    
    def delete_npc(self, npc_id: int) -> Dict[str, Any]:
        """
        删除NPC
        
        Args:
            npc_id: NPC ID
            
        Returns:
            删除结果
        """
        session = get_session()
        try:
            npc = session.query(NPC).filter_by(id=npc_id).first()
            if not npc:
                return {"success": False, "error": "NPC不存在"}
            
            # 删除NPC
            session.delete(npc)
            session.commit()
            
            return {"success": True, "message": "NPC删除成功"}
            
        except SQLAlchemyError as e:
            session.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": f"删除NPC失败: {str(e)}"}
        finally:
            session.close()
    
    def batch_update_npcs(self, story_id: int, npcs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量更新NPC信息
        
        Args:
            story_id: 故事ID
            npcs_data: NPC数据列表
            
        Returns:
            更新结果
        """
        session = get_session()
        try:
            updated_npcs = []
            
            for npc_data in npcs_data:
                npc_id = npc_data.get('id')
                if npc_id:
                    # 更新现有NPC
                    npc = session.query(NPC).filter_by(id=npc_id, story_id=story_id).first()
                    if npc:
                        for key, value in npc_data.items():
                            if hasattr(npc, key) and key not in ['id', 'story_id', 'created_at']:
                                setattr(npc, key, value)
                        updated_npcs.append(npc.to_dict())
                else:
                    # 创建新NPC
                    npc = NPC(
                        story_id=story_id,
                        name=npc_data.get('name'),
                        personality=npc_data.get('personality'),
                        background=npc_data.get('background'),
                        mood=npc_data.get('mood', '平静'),
                        relations=npc_data.get('relations', {}),
                        schedule=npc_data.get('schedule', [])
                    )
                    session.add(npc)
                    session.flush()
                    updated_npcs.append(npc.to_dict())
            
            session.commit()
            
            return {
                "success": True,
                "data": updated_npcs
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": f"批量更新NPC失败: {str(e)}"}
        finally:
            session.close()


# 创建全局服务实例
npc_db_service = NPCDBService() 