"""
调试路由 - 定义调试相关的API端点
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Query, HTTPException

from ..controllers.debug_controller import DebugController

# 创建路由器
debug_router = APIRouter(prefix="/api/debug", tags=["debug"])

# 创建控制器实例
debug_controller = DebugController()


# API端点
@debug_router.get("/workflow_state")
async def debug_workflow_state(session_id: str = Query(default="default", description="会话ID")):
    """
    获取工作流状态
    
    Args:
        session_id: 会话ID
        
    Returns:
        工作流状态
    """
    return await debug_controller.get_workflow_state(session_id)


@debug_router.get("/workflow_info")
async def debug_workflow_info():
    """
    获取工作流信息
    
    Returns:
        工作流信息
    """
    return debug_controller.get_workflow_info()


@debug_router.get("/locations")
async def debug_locations(story_id: int = Query(default=1, description="故事ID")):
    """
    获取位置信息
    
    Args:
        story_id: 故事ID
        
    Returns:
        位置信息
    """
    return debug_controller.get_locations_info(story_id)


@debug_router.get("/npc_locations")
async def debug_npc_locations(
    session_id: str = Query(default="default", description="会话ID"),
    user_id: int = Query(default=1, description="用户ID"),
    story_id: int = Query(default=1, description="故事ID")
):
    """
    获取NPC位置
    
    Args:
        session_id: 会话ID
        user_id: 用户ID
        story_id: 故事ID
        
    Returns:
        NPC位置信息
    """
    return await debug_controller.get_npc_locations(session_id, user_id, story_id)


@debug_router.get("/npcs")
async def debug_npcs(story_id: int = Query(default=1, description="故事ID")):
    """
    获取NPC信息
    
    Args:
        story_id: 故事ID
        
    Returns:
        NPC信息列表
    """
    return debug_controller.get_npcs_info(story_id)


@debug_router.post("/reset_session")
async def debug_reset_session(session_id: str = Query(default="default", description="会话ID")):
    """
    重置会话
    
    Args:
        session_id: 会话ID
        
    Returns:
        重置结果
    """
    return debug_controller.reset_session(session_id)


@debug_router.get("/all_sessions")
async def debug_all_sessions():
    """
    获取所有会话
    
    Returns:
        所有会话信息
    """
    return debug_controller.get_all_sessions()


# 新的调试API端点
@debug_router.get("/game_state")
async def debug_game_state(
    session_id: str = Query(default="default", description="会话ID"),
    user_id: int = Query(default=1, description="用户ID"),
    story_id: int = Query(default=1, description="故事ID")
):
    """
    获取游戏状态
    
    Args:
        session_id: 会话ID
        user_id: 用户ID
        story_id: 故事ID
        
    Returns:
        游戏状态
    """
    return await debug_controller.get_workflow_state(session_id, user_id, story_id)


@debug_router.get("/location_status")
async def get_location_status(
    session_id: str = Query(default="default", description="会话ID"),
    user_id: int = Query(default=1, description="用户ID"),
    story_id: int = Query(default=1, description="故事ID")
):
    """获取位置状态"""
    try:
        # 获取游戏状态
        game_state = await debug_controller.state_service.get_game_state(session_id, user_id, story_id)
        
        # 获取位置信息
        locations_info = debug_controller.get_locations_info(story_id)
        
        return {
            "current_location": game_state.player_location,
            "current_time": game_state.current_time,
            "npc_locations": game_state.npc_locations,
            "locations_info": locations_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取位置状态失败: {str(e)}")


@debug_router.get("/npc_status")
async def get_npc_status(
    session_id: str = Query(default="default", description="会话ID"),
    user_id: int = Query(default=1, description="用户ID"),
    story_id: int = Query(default=1, description="故事ID")
):
    """获取NPC状态"""
    return await debug_controller.get_npc_status_info(session_id, user_id, story_id)


@debug_router.get("/messages")
async def debug_messages(
    session_id: str = Query(default="default", description="会话ID"),
    user_id: int = Query(default=1, description="用户ID"),
    story_id: int = Query(default=1, description="故事ID")
):
    """
    获取消息历史
    
    Args:
        session_id: 会话ID
        user_id: 用户ID
        story_id: 故事ID
        
    Returns:
        消息历史
    """
    return await debug_controller.get_messages(session_id, user_id, story_id) 