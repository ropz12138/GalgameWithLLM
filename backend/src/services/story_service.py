"""
故事服务层 - 处理故事相关的业务逻辑
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..database.config import get_session
from ..database.models import Story, Location, NPC, User


class StoryService:
    """故事服务类"""
    
    def __init__(self):
        pass
    
    def create_story(self, name: str, description: str, creator_id: int, 
                    game_config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        创建新故事
        
        Args:
            name: 故事名称
            description: 故事描述
            creator_id: 创建者ID
            game_config: 游戏配置
            
        Returns:
            创建的故事信息或None
        """
        session = get_session()
        try:
            # 检查用户是否存在
            user = session.query(User).filter_by(id=creator_id).first()
            if not user:
                return {"success": False, "error": "用户不存在"}
            
            # 检查故事名称是否重复
            existing_story = session.query(Story).filter_by(name=name, creator_id=creator_id).first()
            if existing_story:
                return {"success": False, "error": "故事名称已存在"}
            
            # 创建故事
            story = Story(
                name=name,
                description=description,
                creator_id=creator_id,
                game_config=game_config or {}
            )
            session.add(story)
            session.commit()
            
            return {
                "success": True,
                "data": story.to_dict()
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": f"创建故事失败: {str(e)}"}
        finally:
            session.close()
    
    def get_story_by_id(self, story_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取故事
        
        Args:
            story_id: 故事ID
            
        Returns:
            故事信息或None
        """
        session = get_session()
        try:
            story = session.query(Story).filter_by(id=story_id, is_active=True).first()
            if not story:
                return {"success": False, "error": "故事不存在"}
            
            return {
                "success": True,
                "data": story.to_dict()
            }
            
        except Exception as e:
            return {"success": False, "error": f"获取故事失败: {str(e)}"}
        finally:
            session.close()
    
    def get_stories_by_user(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户的所有故事
        
        Args:
            user_id: 用户ID
            
        Returns:
            故事列表
        """
        session = get_session()
        try:
            stories = session.query(Story).filter_by(creator_id=user_id, is_active=True).all()
            
            return {
                "success": True,
                "data": [story.to_dict() for story in stories]
            }
            
        except Exception as e:
            return {"success": False, "error": f"获取故事列表失败: {str(e)}"}
        finally:
            session.close()
    
    def update_story(self, story_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """
        更新故事信息
        
        Args:
            story_id: 故事ID
            user_id: 用户ID（权限验证）
            **kwargs: 要更新的字段
            
        Returns:
            更新结果
        """
        session = get_session()
        try:
            story = session.query(Story).filter_by(id=story_id, creator_id=user_id, is_active=True).first()
            if not story:
                return {"success": False, "error": "故事不存在或无权限"}
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(story, key) and key not in ['id', 'creator_id', 'created_at']:
                    setattr(story, key, value)
            
            session.commit()
            
            return {
                "success": True,
                "data": story.to_dict()
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": f"更新故事失败: {str(e)}"}
        finally:
            session.close()
    
    def delete_story(self, story_id: int, user_id: int) -> Dict[str, Any]:
        """
        删除故事（软删除）
        
        Args:
            story_id: 故事ID
            user_id: 用户ID（权限验证）
            
        Returns:
            删除结果
        """
        session = get_session()
        try:
            story = session.query(Story).filter_by(id=story_id, creator_id=user_id, is_active=True).first()
            if not story:
                return {"success": False, "error": "故事不存在或无权限"}
            
            # 软删除
            story.is_active = False
            session.commit()
            
            return {"success": True, "message": "故事删除成功"}
            
        except SQLAlchemyError as e:
            session.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": f"删除故事失败: {str(e)}"}
        finally:
            session.close()
    
    def get_story_with_details(self, story_id: int) -> Dict[str, Any]:
        """
        获取故事及其完整信息（包括位置和NPC）
        
        Args:
            story_id: 故事ID
            
        Returns:
            完整的故事信息
        """
        session = get_session()
        try:
            story = session.query(Story).filter_by(id=story_id, is_active=True).first()
            if not story:
                return {"success": False, "error": "故事不存在"}
            
            # 获取位置信息
            locations = session.query(Location).filter_by(story_id=story_id).all()
            
            # 获取NPC信息
            npcs = session.query(NPC).filter_by(story_id=story_id).all()
            
            story_data = story.to_dict()
            story_data['locations'] = [location.to_dict() for location in locations]
            story_data['npcs'] = [npc.to_dict() for npc in npcs]
            
            return {
                "success": True,
                "data": story_data
            }
            
        except Exception as e:
            return {"success": False, "error": f"获取故事详情失败: {str(e)}"}
        finally:
            session.close()

    def get_all_stories(self) -> Dict[str, Any]:
        """
        获取所有活跃的故事（公开接口）
        
        Returns:
            所有故事列表
        """
        import logging
        logger = logging.getLogger(__name__)
        
        session = get_session()
        try:
            logger.info("📊 [StoryService] 开始从数据库获取所有故事")
            
            # 获取所有活跃的故事，包含创建者信息
            stories = session.query(Story).join(User, Story.creator_id == User.id).filter(
                Story.is_active == True
            ).all()
            
            logger.info(f"📊 [StoryService] 从数据库获取到 {len(stories)} 个活跃故事")
            
            # 转换为字典格式，包含创建者信息
            story_list = []
            for story in stories:
                story_dict = story.to_dict()
                # 添加创建者用户名
                creator = session.query(User).filter_by(id=story.creator_id).first()
                if creator:
                    story_dict['creator_username'] = creator.username
                else:
                    story_dict['creator_username'] = 'Unknown'
                
                story_list.append(story_dict)
            
            logger.info(f"✅ [StoryService] 故事数据转换完成")
            
            return {
                "success": True,
                "data": story_list
            }
            
        except SQLAlchemyError as e:
            logger.error(f"❌ [StoryService] 数据库错误: {str(e)}")
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ [StoryService] 获取所有故事失败: {str(e)}", exc_info=True)
            return {"success": False, "error": f"获取所有故事失败: {str(e)}"}
        finally:
            session.close()


# 创建全局服务实例
story_service = StoryService() 