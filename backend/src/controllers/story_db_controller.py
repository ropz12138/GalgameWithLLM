"""
故事数据库控制器 - 处理故事相关的HTTP请求
"""
from typing import Dict, Any, List
from fastapi import HTTPException
from pydantic import BaseModel, Field

from ..services.story_service import story_service
from ..services.location_db_service import location_db_service
from ..services.npc_db_service import npc_db_service


# 请求模型
class CreateStoryRequest(BaseModel):
    name: str = Field(..., description="故事名称")
    description: str = Field("", description="故事描述")
    game_config: Dict[str, Any] = Field(default_factory=dict, description="游戏配置")


class UpdateStoryRequest(BaseModel):
    name: str = Field(None, description="故事名称")
    description: str = Field(None, description="故事描述")
    game_config: Dict[str, Any] = Field(None, description="游戏配置")


class SaveStoryDataRequest(BaseModel):
    story_id: int = Field(..., description="故事ID")
    npcs: List[Dict[str, Any]] = Field(default_factory=list, description="NPC数据")
    locations: List[Dict[str, Any]] = Field(default_factory=list, description="位置数据")
    game_config: Dict[str, Any] = Field(default_factory=dict, description="游戏配置")


class CreateCompleteStoryRequest(BaseModel):
    name: str = Field(..., description="故事名称")
    description: str = Field("", description="故事描述")
    npcs: List[Dict[str, Any]] = Field(..., description="NPC数据")
    locations: List[Dict[str, Any]] = Field(..., description="位置数据")
    game_config: Dict[str, Any] = Field(..., description="游戏配置")


class StoryDBController:
    """故事数据库控制器类"""
    
    def __init__(self):
        pass
    
    def create_story(self, request: CreateStoryRequest, user_id: int) -> Dict[str, Any]:
        """
        创建新故事
        
        Args:
            request: 创建故事请求
            user_id: 用户ID
            
        Returns:
            创建结果
        """
        try:
            result = story_service.create_story(
                name=request.name,
                description=request.description,
                creator_id=user_id,
                game_config=request.game_config
            )
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["error"])
            
            return result["data"]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"创建故事失败: {str(e)}")
    
    def get_user_stories(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户的所有故事
        
        Args:
            user_id: 用户ID
            
        Returns:
            故事列表
        """
        try:
            result = story_service.get_stories_by_user(user_id)
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["error"])
            
            return result["data"]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取故事列表失败: {str(e)}")
    
    def get_story_details(self, story_id: int, user_id: int) -> Dict[str, Any]:
        """
        获取故事详情
        
        Args:
            story_id: 故事ID
            user_id: 用户ID（权限验证）
            
        Returns:
            故事详情
        """
        try:
            # 验证权限
            story_result = story_service.get_story_by_id(story_id)
            if not story_result["success"]:
                raise HTTPException(status_code=404, detail="故事不存在")
            
            story = story_result["data"]
            if story["creator_id"] != user_id:
                raise HTTPException(status_code=403, detail="无权限访问此故事")
            
            # 获取完整信息
            result = story_service.get_story_with_details(story_id)
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["error"])
            
            return result["data"]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取故事详情失败: {str(e)}")
    
    def update_story(self, story_id: int, request: UpdateStoryRequest, user_id: int) -> Dict[str, Any]:
        """
        更新故事信息
        
        Args:
            story_id: 故事ID
            request: 更新请求
            user_id: 用户ID
            
        Returns:
            更新结果
        """
        try:
            # 准备更新数据
            update_data = {}
            if request.name is not None:
                update_data["name"] = request.name
            if request.description is not None:
                update_data["description"] = request.description
            if request.game_config is not None:
                update_data["game_config"] = request.game_config
            
            result = story_service.update_story(story_id, user_id, **update_data)
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["error"])
            
            return result["data"]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"更新故事失败: {str(e)}")
    
    def delete_story(self, story_id: int, user_id: int) -> Dict[str, str]:
        """
        删除故事
        
        Args:
            story_id: 故事ID
            user_id: 用户ID
            
        Returns:
            删除结果
        """
        try:
            result = story_service.delete_story(story_id, user_id)
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["error"])
            
            return {"message": result["message"]}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"删除故事失败: {str(e)}")
    
    def save_story_data(self, request: SaveStoryDataRequest, user_id: int) -> Dict[str, Any]:
        """
        保存故事数据（NPC和位置）
        
        Args:
            request: 保存请求
            user_id: 用户ID
            
        Returns:
            保存结果
        """
        try:
            # 验证权限
            story_result = story_service.get_story_by_id(request.story_id)
            if not story_result["success"]:
                raise HTTPException(status_code=404, detail="故事不存在")
            
            story = story_result["data"]
            if story["creator_id"] != user_id:
                raise HTTPException(status_code=403, detail="无权限修改此故事")
            
            # 批量更新位置
            locations_result = location_db_service.batch_update_locations(
                request.story_id, request.locations
            )
            if not locations_result["success"]:
                raise HTTPException(status_code=400, detail=f"保存位置数据失败: {locations_result['error']}")
            
            # 批量更新NPC
            npcs_result = npc_db_service.batch_update_npcs(
                request.story_id, request.npcs
            )
            if not npcs_result["success"]:
                raise HTTPException(status_code=400, detail=f"保存NPC数据失败: {npcs_result['error']}")
            
            # 更新游戏配置
            if request.game_config:
                config_result = story_service.update_story(
                    request.story_id, user_id, game_config=request.game_config
                )
                if not config_result["success"]:
                    raise HTTPException(status_code=400, detail=f"保存游戏配置失败: {config_result['error']}")
            
            return {
                "message": "故事数据保存成功",
                "locations": locations_result["data"],
                "npcs": npcs_result["data"]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"保存故事数据失败: {str(e)}")
    
    def create_complete_story(self, request: CreateCompleteStoryRequest, user_id: int) -> Dict[str, Any]:
        """
        创建完整的新故事（包含NPC和位置数据）
        
        Args:
            request: 创建完整故事请求
            user_id: 用户ID
            
        Returns:
            创建结果
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"🚀 [CreateCompleteStory] 开始创建完整故事 - 用户ID: {user_id}, 故事名: {request.name}")
        logger.info(f"📊 [CreateCompleteStory] 请求数据统计 - NPC数量: {len(request.npcs)}, 位置数量: {len(request.locations)}")
        
        try:
            # 1. 首先创建故事
            logger.info(f"📝 [CreateCompleteStory] 步骤1: 创建基础故事信息")
            story_result = story_service.create_story(
                name=request.name,
                description=request.description,
                creator_id=user_id,
                game_config=request.game_config
            )
            
            if not story_result["success"]:
                logger.error(f"❌ [CreateCompleteStory] 故事创建失败: {story_result['error']}")
                raise HTTPException(status_code=400, detail=story_result["error"])
            
            story_id = story_result["data"]["id"]
            logger.info(f"✅ [CreateCompleteStory] 故事创建成功 - 故事ID: {story_id}")
            
            # 2. 批量创建位置
            logger.info(f"🗺️ [CreateCompleteStory] 步骤2: 批量创建位置 - 数量: {len(request.locations)}")
            locations_result = location_db_service.batch_update_locations(
                story_id, request.locations
            )
            if not locations_result["success"]:
                logger.error(f"❌ [CreateCompleteStory] 位置创建失败: {locations_result['error']}")
                logger.info(f"🔄 [CreateCompleteStory] 开始回滚 - 删除已创建的故事ID: {story_id}")
                # 如果位置创建失败，删除已创建的故事
                story_service.delete_story(story_id, user_id)
                raise HTTPException(status_code=400, detail=f"创建位置失败: {locations_result['error']}")
            
            logger.info(f"✅ [CreateCompleteStory] 位置创建成功 - 创建数量: {len(locations_result.get('data', []))}")
            
            # 3. 批量创建NPC
            logger.info(f"👥 [CreateCompleteStory] 步骤3: 批量创建NPC - 数量: {len(request.npcs)}")
            npcs_result = npc_db_service.batch_update_npcs(
                story_id, request.npcs
            )
            if not npcs_result["success"]:
                logger.error(f"❌ [CreateCompleteStory] NPC创建失败: {npcs_result['error']}")
                logger.info(f"🔄 [CreateCompleteStory] 开始回滚 - 删除已创建的故事ID: {story_id}")
                # 如果NPC创建失败，删除已创建的故事和位置
                story_service.delete_story(story_id, user_id)
                raise HTTPException(status_code=400, detail=f"创建NPC失败: {npcs_result['error']}")
            
            logger.info(f"✅ [CreateCompleteStory] NPC创建成功 - 创建数量: {len(npcs_result.get('data', []))}")
            
            # 4. 返回完整的故事信息
            complete_story = {
                "story": story_result["data"],
                "locations": locations_result["data"],
                "npcs": npcs_result["data"],
                "message": "完整故事创建成功"
            }
            
            logger.info(f"🎉 [CreateCompleteStory] 完整故事创建成功 - 故事ID: {story_id}, 用户ID: {user_id}")
            return complete_story
            
        except HTTPException as he:
            logger.error(f"❌ [CreateCompleteStory] HTTP异常 - 状态码: {he.status_code}, 详情: {he.detail}")
            raise
        except Exception as e:
            logger.error(f"❌ [CreateCompleteStory] 系统异常 - 用户ID: {user_id}, 错误: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"创建完整故事失败: {str(e)}")

    def get_all_stories(self) -> List[Dict[str, Any]]:
        """
        获取所有故事（公开接口，不需要认证）
        
        Returns:
            所有故事列表
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("🌐 [GetAllStories] 开始获取所有故事列表")
        
        try:
            result = story_service.get_all_stories()
            
            if not result["success"]:
                logger.error(f"❌ [GetAllStories] 获取失败: {result['error']}")
                raise HTTPException(status_code=400, detail=result["error"])
            
            stories = result["data"]
            logger.info(f"✅ [GetAllStories] 获取成功 - 故事总数: {len(stories)}")
            
            # 记录故事统计信息
            active_count = sum(1 for story in stories if story.get('is_active', True))
            logger.info(f"📊 [GetAllStories] 故事统计 - 活跃故事: {active_count}, 总故事: {len(stories)}")
            
            return stories
            
        except HTTPException as he:
            logger.error(f"❌ [GetAllStories] HTTP异常 - 状态码: {he.status_code}, 详情: {he.detail}")
            raise
        except Exception as e:
            logger.error(f"❌ [GetAllStories] 系统异常 - 错误: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"获取所有故事失败: {str(e)}")


# 创建全局控制器实例
story_db_controller = StoryDBController() 