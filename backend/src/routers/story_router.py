"""
故事路由 - 定义故事相关的API端点
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..controllers.story_controller import StoryController

# 创建路由器
story_router = APIRouter(prefix="/api/story", tags=["story"])

# 创建控制器实例
story_controller = StoryController()


@story_router.get("/info")
async def get_story_info() -> Dict[str, Any]:
    """
    获取所有故事信息
    
    Returns:
        故事信息，包括所有NPC和位置数据
    """
    try:
        result = story_controller.get_all_story_info()
        if result["success"]:
            return result["data"]
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取故事信息失败: {str(e)}") 