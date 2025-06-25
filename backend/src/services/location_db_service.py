"""
位置数据库服务层 - 处理位置相关的数据库操作
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..database.config import get_session
from ..database.models import Location, Story


class LocationDBService:
    """位置数据库服务类"""
    
    def __init__(self):
        pass
    
    def create_location(self, story_id: int, key: str, name: str, 
                       en_name: Optional[str] = None, description: Optional[str] = None,
                       connections: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        创建新位置
        
        Args:
            story_id: 故事ID
            key: 位置键名
            name: 位置名称
            en_name: 英文名称
            description: 描述
            connections: 连接的位置列表
            
        Returns:
            创建结果
        """
        session = get_session()
        try:
            # 检查故事是否存在
            story = session.query(Story).filter_by(id=story_id, is_active=True).first()
            if not story:
                return {"success": False, "error": "故事不存在"}
            
            # 检查位置键名是否重复
            existing_location = session.query(Location).filter_by(story_id=story_id, key=key).first()
            if existing_location:
                return {"success": False, "error": "位置键名已存在"}
            
            # 创建位置
            location = Location(
                story_id=story_id,
                key=key,
                name=name,
                en_name=en_name or key,
                description=description,
                connections=connections or []
            )
            session.add(location)
            session.commit()
            
            return {
                "success": True,
                "data": location.to_dict()
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": f"创建位置失败: {str(e)}"}
        finally:
            session.close()
    
    def get_locations_by_story(self, story_id: int) -> Dict[str, Any]:
        """
        获取故事的所有位置
        
        Args:
            story_id: 故事ID
            
        Returns:
            位置列表
        """
        session = get_session()
        try:
            locations = session.query(Location).filter_by(story_id=story_id).all()
            
            return {
                "success": True,
                "data": [location.to_dict() for location in locations]
            }
            
        except Exception as e:
            return {"success": False, "error": f"获取位置列表失败: {str(e)}"}
        finally:
            session.close()
    
    def get_location_by_key(self, story_id: int, key: str) -> Dict[str, Any]:
        """
        根据键名获取位置
        
        Args:
            story_id: 故事ID
            key: 位置键名
            
        Returns:
            位置信息
        """
        session = get_session()
        try:
            location = session.query(Location).filter_by(story_id=story_id, key=key).first()
            if not location:
                return {"success": False, "error": "位置不存在"}
            
            return {
                "success": True,
                "data": location.to_dict()
            }
            
        except Exception as e:
            return {"success": False, "error": f"获取位置失败: {str(e)}"}
        finally:
            session.close()
    
    def update_location(self, location_id: int, **kwargs) -> Dict[str, Any]:
        """
        更新位置信息
        
        Args:
            location_id: 位置ID
            **kwargs: 要更新的字段
            
        Returns:
            更新结果
        """
        session = get_session()
        try:
            location = session.query(Location).filter_by(id=location_id).first()
            if not location:
                return {"success": False, "error": "位置不存在"}
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(location, key) and key not in ['id', 'story_id', 'created_at']:
                    setattr(location, key, value)
            
            session.commit()
            
            return {
                "success": True,
                "data": location.to_dict()
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": f"更新位置失败: {str(e)}"}
        finally:
            session.close()
    
    def delete_location(self, location_id: int) -> Dict[str, Any]:
        """
        删除位置
        
        Args:
            location_id: 位置ID
            
        Returns:
            删除结果
        """
        session = get_session()
        try:
            location = session.query(Location).filter_by(id=location_id).first()
            if not location:
                return {"success": False, "error": "位置不存在"}
            
            # 从其他位置的连接中移除此位置
            story_locations = session.query(Location).filter_by(story_id=location.story_id).all()
            for loc in story_locations:
                if location.key in (loc.connections or []):
                    updated_connections = [conn for conn in loc.connections if conn != location.key]
                    loc.connections = updated_connections
            
            # 删除位置
            session.delete(location)
            session.commit()
            
            return {"success": True, "message": "位置删除成功"}
            
        except SQLAlchemyError as e:
            session.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": f"删除位置失败: {str(e)}"}
        finally:
            session.close()
    
    def batch_update_locations(self, story_id: int, locations_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量更新位置信息
        
        Args:
            story_id: 故事ID
            locations_data: 位置数据列表
            
        Returns:
            更新结果
        """
        session = get_session()
        try:
            updated_locations = []
            
            for location_data in locations_data:
                location_id = location_data.get('id')
                if location_id:
                    # 更新现有位置
                    location = session.query(Location).filter_by(id=location_id, story_id=story_id).first()
                    if location:
                        for key, value in location_data.items():
                            if hasattr(location, key) and key not in ['id', 'story_id', 'created_at']:
                                setattr(location, key, value)
                        updated_locations.append(location.to_dict())
                else:
                    # 创建新位置
                    location = Location(
                        story_id=story_id,
                        key=location_data.get('key'),
                        name=location_data.get('name'),
                        en_name=location_data.get('en_name'),
                        description=location_data.get('description'),
                        connections=location_data.get('connections', [])
                    )
                    session.add(location)
                    session.flush()
                    updated_locations.append(location.to_dict())
            
            session.commit()
            
            return {
                "success": True,
                "data": updated_locations
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {"success": False, "error": f"数据库错误: {str(e)}"}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": f"批量更新位置失败: {str(e)}"}
        finally:
            session.close()


# 创建全局服务实例
location_db_service = LocationDBService() 