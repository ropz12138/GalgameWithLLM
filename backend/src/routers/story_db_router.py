"""
故事数据库路由 - 定义故事相关的API端点
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
import logging

from ..controllers.story_db_controller import (
    story_db_controller, 
    CreateStoryRequest, 
    UpdateStoryRequest, 
    SaveStoryDataRequest,
    CreateCompleteStoryRequest
)
from ..services.auth_service import auth_service


# 创建路由器
router = APIRouter(prefix="/api/stories", tags=["故事管理"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=Dict[str, Any])
async def create_story(
    request: CreateStoryRequest,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """创建新故事"""
    logger.info(f"🌐 [API-CreateStory] 创建故事请求 - 用户: {current_user.get('username')}, 故事名: {request.name}")
    try:
        result = story_db_controller.create_story(request, current_user["id"])
        logger.info(f"✅ [API-CreateStory] 故事创建成功 - 故事ID: {result.get('id')}")
        return result
    except Exception as e:
        logger.error(f"❌ [API-CreateStory] 故事创建失败 - 用户ID: {current_user.get('id')}, 错误: {str(e)}")
        raise


@router.get("/", response_model=List[Dict[str, Any]])
async def get_user_stories(
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """获取用户的故事列表"""
    logger.info(f"🌐 [API-GetUserStories] 获取故事列表 - 用户: {current_user.get('username')}")
    try:
        stories = story_db_controller.get_user_stories(current_user["id"])
        logger.info(f"✅ [API-GetUserStories] 获取成功 - 故事数量: {len(stories)}")
        return stories
    except Exception as e:
        logger.error(f"❌ [API-GetUserStories] 获取失败 - 用户ID: {current_user.get('id')}, 错误: {str(e)}")
        raise


@router.get("/all", response_model=List[Dict[str, Any]])
async def get_all_stories():
    """获取所有故事（公开接口，不需要认证）"""
    
    # 记录请求开始
    logger.info("🌐 [API-GetAllStories] 接收到获取所有故事请求（公开接口）")
    
    try:
        # 调用控制器
        stories = story_db_controller.get_all_stories()
        
        logger.info(f"✅ [API-GetAllStories] 请求处理成功 - 返回故事数量: {len(stories)}")
        return stories
        
    except HTTPException as he:
        logger.error(f"❌ [API-GetAllStories] HTTP异常 - 状态码: {he.status_code}, 详情: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ [API-GetAllStories] 系统异常 - 错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/{story_id}", response_model=Dict[str, Any])
async def get_story_details(
    story_id: int,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """获取故事详情"""
    logger.info(f"🌐 [API-GetStoryDetails] 获取故事详情 - 用户: {current_user.get('username')}, 故事ID: {story_id}")
    try:
        story = story_db_controller.get_story_details(story_id, current_user["id"])
        logger.info(f"✅ [API-GetStoryDetails] 获取成功 - 故事: {story.get('name')}")
        return story
    except Exception as e:
        logger.error(f"❌ [API-GetStoryDetails] 获取失败 - 故事ID: {story_id}, 用户ID: {current_user.get('id')}, 错误: {str(e)}")
        raise


@router.put("/{story_id}", response_model=Dict[str, Any])
async def update_story(
    story_id: int,
    request: UpdateStoryRequest,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """更新故事信息"""
    logger.info(f"🌐 [API-UpdateStory] 更新故事 - 用户: {current_user.get('username')}, 故事ID: {story_id}")
    try:
        result = story_db_controller.update_story(story_id, request, current_user["id"])
        logger.info(f"✅ [API-UpdateStory] 更新成功 - 故事ID: {story_id}")
        return result
    except Exception as e:
        logger.error(f"❌ [API-UpdateStory] 更新失败 - 故事ID: {story_id}, 用户ID: {current_user.get('id')}, 错误: {str(e)}")
        raise


@router.delete("/{story_id}", response_model=Dict[str, str])
async def delete_story(
    story_id: int,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """删除故事"""
    logger.info(f"🌐 [API-DeleteStory] 删除故事 - 用户: {current_user.get('username')}, 故事ID: {story_id}")
    try:
        result = story_db_controller.delete_story(story_id, current_user["id"])
        logger.info(f"✅ [API-DeleteStory] 删除成功 - 故事ID: {story_id}")
        return result
    except Exception as e:
        logger.error(f"❌ [API-DeleteStory] 删除失败 - 故事ID: {story_id}, 用户ID: {current_user.get('id')}, 错误: {str(e)}")
        raise


@router.post("/save-data", response_model=Dict[str, Any])
async def save_story_data(
    request: SaveStoryDataRequest,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """保存故事数据（NPC和位置）"""
    logger.info(f"🌐 [API-SaveStoryData] 保存故事数据 - 用户: {current_user.get('username')}, 故事ID: {request.story_id}")
    try:
        result = story_db_controller.save_story_data(request, current_user["id"])
        logger.info(f"✅ [API-SaveStoryData] 保存成功 - 故事ID: {request.story_id}")
        return result
    except Exception as e:
        logger.error(f"❌ [API-SaveStoryData] 保存失败 - 故事ID: {request.story_id}, 用户ID: {current_user.get('id')}, 错误: {str(e)}")
        raise


@router.post("/create-complete", response_model=Dict[str, Any])
async def create_complete_story(
    request: CreateCompleteStoryRequest,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """创建完整的新故事（包含故事、位置和NPC数据）"""
    
    # 记录请求开始
    logger.info(f"🌐 [API-CreateCompleteStory] 接收到创建完整故事请求")
    logger.info(f"👤 [API-CreateCompleteStory] 用户信息 - ID: {current_user.get('id')}, 用户名: {current_user.get('username')}")
    logger.info(f"📝 [API-CreateCompleteStory] 故事信息 - 名称: {request.name}, 描述长度: {len(request.description or '')}")
    logger.info(f"📊 [API-CreateCompleteStory] 数据统计 - NPC: {len(request.npcs)}, 位置: {len(request.locations)}")
    
    try:
        # 验证用户权限
        if not current_user or not current_user.get("id"):
            logger.error(f"❌ [API-CreateCompleteStory] 用户认证失败 - 无效的用户信息: {current_user}")
            raise HTTPException(status_code=401, detail="用户认证失败")
        
        # 调用控制器
        result = story_db_controller.create_complete_story(request, current_user["id"])
        
        logger.info(f"✅ [API-CreateCompleteStory] 请求处理成功 - 故事ID: {result.get('story', {}).get('id')}")
        return result
        
    except HTTPException as he:
        logger.error(f"❌ [API-CreateCompleteStory] HTTP异常 - 状态码: {he.status_code}, 详情: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ [API-CreateCompleteStory] 系统异常 - 用户ID: {current_user.get('id')}, 错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}") 