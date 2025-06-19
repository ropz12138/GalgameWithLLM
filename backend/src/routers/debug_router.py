"""
调试路由 - 定义调试相关的API端点
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Query, Depends

from controllers.debug_controller import DebugController
from utils.auth import get_current_user

# 创建路由器
debug_router = APIRouter(prefix="/api/debug", tags=["调试"])

# 创建控制器实例
debug_controller = DebugController()


# API端点
@debug_router.get("/workflow_state")
async def debug_workflow_state(
    session_id: str = Query(default="default", description="会话ID"),
    current_user = Depends(get_current_user)
):
    """
    获取工作流状态
    
    Args:
        session_id: 会话ID
        current_user: 当前认证用户
        
    Returns:
        工作流状态
    """
    return debug_controller.get_workflow_state(session_id)


@debug_router.get("/workflow_info")
async def debug_workflow_info(current_user = Depends(get_current_user)):
    """
    获取工作流信息
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        工作流信息
    """
    return debug_controller.get_workflow_info()


@debug_router.get("/locations")
async def debug_locations(current_user = Depends(get_current_user)):
    """
    获取位置信息
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        位置信息
    """
    return debug_controller.get_locations_info()


@debug_router.get("/npc_locations")
async def debug_npc_locations(
    session_id: str = Query(default="default", description="会话ID"),
    current_user = Depends(get_current_user)
):
    """
    获取NPC位置
    
    Args:
        session_id: 会话ID
        current_user: 当前认证用户
        
    Returns:
        NPC位置信息
    """
    return debug_controller.get_npc_locations(session_id)


@debug_router.get("/npc_status")
async def debug_npc_status(
    session_id: str = Query(default="default", description="会话ID"),
    current_user = Depends(get_current_user)
):
    """
    获取NPC状态信息
    
    Args:
        session_id: 会话ID
        current_user: 当前认证用户
        
    Returns:
        NPC状态信息
    """
    return debug_controller.get_npc_status_info(session_id)


@debug_router.get("/npcs")
async def debug_npcs(current_user = Depends(get_current_user)):
    """
    获取NPC信息
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        NPC信息列表
    """
    return debug_controller.get_npcs_info()


@debug_router.get("/messages")
async def debug_messages(
    session_id: str = Query(default="default", description="会话ID"),
    current_user = Depends(get_current_user)
):
    """
    获取消息历史
    
    Args:
        session_id: 会话ID
        current_user: 当前认证用户
        
    Returns:
        消息历史
    """
    return debug_controller.get_messages(session_id)


@debug_router.post("/reset_session")
async def debug_reset_session(
    session_id: str = Query(default="default", description="会话ID"),
    current_user = Depends(get_current_user)
):
    """
    重置会话
    
    Args:
        session_id: 会话ID
        current_user: 当前认证用户
        
    Returns:
        重置结果
    """
    return debug_controller.reset_session(session_id)


@debug_router.get("/all_sessions")
async def debug_all_sessions(current_user = Depends(get_current_user)):
    """
    获取所有会话
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        所有会话信息
    """
    return debug_controller.get_all_sessions() 