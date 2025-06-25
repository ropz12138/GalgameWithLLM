"""
游戏路由 - 定义游戏相关的API端点
"""
from typing import List, Dict
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel, Field

from ..controllers.game_controller import GameController
from ..services.auth_service import auth_service

# 创建路由器
game_router = APIRouter(prefix="/api", tags=["游戏"])

# 创建控制器实例
game_controller = GameController()


# 请求模型
class ActionRequest(BaseModel):
    action: str = Field(description="玩家行动")
    session_id: str = Field(default="default", description="会话ID")
    story_id: int = Field(default=None, description="故事ID")


class DialogueRequest(BaseModel):
    message: str = Field(description="对话消息")
    history: List[Dict] = Field(default=[], description="对话历史（兼容性字段）")


# API端点
@game_router.get("/")
async def root():
    """根端点"""
    return {
        "message": "LLM文字游戏 API",
        "version": "2.0.0",
        "status": "运行中"
    }


@game_router.get("/game_state")
async def get_current_game_state(
    session_id: str = Query(default="default", description="会话ID"),
    story_id: int = Query(default=None, description="故事ID")
):
    """
    获取当前游戏状态
    
    Args:
        session_id: 会话ID
        story_id: 故事ID（可选，用于从数据库恢复状态）
        
    Returns:
        游戏状态
    """
    return await game_controller.get_game_state(session_id, story_id)


@game_router.post("/process_action")
async def process_player_action(request: ActionRequest):
    """
    处理玩家行动
    
    Args:
        request: 行动请求
        
    Returns:
        处理结果
    """
    return await game_controller.process_action(request.action, request.session_id, request.story_id)


@game_router.post("/stream_action")
async def stream_player_action(request: ActionRequest):
    """
    流式处理玩家行动
    
    Args:
        request: 行动请求
        
    Returns:
        流式响应
    """
    return await game_controller.stream_action(request.action, request.session_id)


@game_router.post("/initialize_game")
async def initialize_game(session_id: str = Query(default="default", description="会话ID")):
    """
    初始化游戏
    
    Args:
        session_id: 会话ID
        
    Returns:
        初始化结果
    """
    return await game_controller.initialize_game(session_id)


@game_router.get("/npc_dialogue_history/{npc_name}")
async def get_npc_dialogue_history(
    npc_name: str,
    session_id: str = Query(default="default", description="会话ID")
):
    """
    获取NPC对话历史
    
    Args:
        npc_name: NPC名称
        session_id: 会话ID
        
    Returns:
        NPC对话历史
    """
    return await game_controller.get_npc_dialogue_history(npc_name, session_id)


@game_router.post("/continue_dialogue/{npc_name}")
async def continue_dialogue_with_npc(
    npc_name: str,
    request: DialogueRequest,
    session_id: str = Query(default="default", description="会话ID")
):
    """
    继续与NPC对话
    
    Args:
        npc_name: NPC名称
        request: 对话请求
        session_id: 会话ID
        
    Returns:
        对话结果
    """
    return await game_controller.continue_dialogue(npc_name, request.message, session_id)


@game_router.get("/stories/{story_id}/messages")
async def get_story_messages(
    story_id: int,
    session_id: str = Query(default=None, description="会话ID（可选）"),
    limit: int = Query(default=100, description="限制返回数量"),
    offset: int = Query(default=0, description="偏移量"),
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    获取故事的消息历史
    
    Args:
        story_id: 故事ID
        session_id: 会话ID（可选，为None时获取所有会话）
        limit: 限制返回数量
        offset: 偏移量
        current_user: 当前用户信息
        
    Returns:
        消息历史数据
    """
    result = await game_controller.get_story_messages(
        user_id=current_user["id"],
        story_id=story_id,
        session_id=session_id,
        limit=limit,
        offset=offset
    )
    
    if not result["success"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result["data"] 