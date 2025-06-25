"""
NPC数据库路由 - 定义NPC相关的API端点
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..services.npc_db_service import npc_db_service
from ..services.story_service import story_service
from ..services.auth_service import auth_service


# 请求模型
class CreateNPCRequest(BaseModel):
    story_id: int = Field(..., description="故事ID")
    name: str = Field(..., description="NPC名称")
    personality: str = Field(None, description="性格描述")
    background: str = Field(None, description="背景描述")
    mood: str = Field("平静", description="当前心情")
    relations: Dict[str, Any] = Field(default_factory=dict, description="人物关系")
    schedule: List[Dict[str, Any]] = Field(default_factory=list, description="日程安排")


class UpdateNPCRequest(BaseModel):
    name: str = Field(None, description="NPC名称")
    personality: str = Field(None, description="性格描述")
    background: str = Field(None, description="背景描述")
    mood: str = Field(None, description="当前心情")
    relations: Dict[str, Any] = Field(None, description="人物关系")
    schedule: List[Dict[str, Any]] = Field(None, description="日程安排")


class UpdateNPCScheduleRequest(BaseModel):
    schedule: List[Dict[str, Any]] = Field(..., description="新的日程安排")


class UpdateNPCRelationsRequest(BaseModel):
    relations: Dict[str, Any] = Field(..., description="新的人物关系")


# 创建路由器
router = APIRouter(prefix="/api/npcs", tags=["NPC管理"])


async def verify_story_access(story_id: int, user_id: int):
    """验证用户对故事的访问权限"""
    story_result = story_service.get_story_by_id(story_id)
    if not story_result["success"]:
        raise HTTPException(status_code=404, detail="故事不存在")
    
    story = story_result["data"]
    if story["creator_id"] != user_id:
        raise HTTPException(status_code=403, detail="无权限访问此故事")


@router.post("/", response_model=Dict[str, Any])
async def create_npc(
    request: CreateNPCRequest,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """创建新NPC"""
    # 验证权限
    await verify_story_access(request.story_id, current_user["id"])
    
    result = npc_db_service.create_npc(
        story_id=request.story_id,
        name=request.name,
        personality=request.personality,
        background=request.background,
        mood=request.mood,
        relations=request.relations,
        schedule=request.schedule
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result["data"]


@router.get("/story/{story_id}", response_model=List[Dict[str, Any]])
async def get_story_npcs(
    story_id: int,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """获取故事的所有NPC"""
    # 验证权限
    await verify_story_access(story_id, current_user["id"])
    
    result = npc_db_service.get_npcs_by_story(story_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result["data"]


@router.get("/{npc_id}", response_model=Dict[str, Any])
async def get_npc_by_id(
    npc_id: int,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """根据ID获取NPC"""
    # 这里需要先获取NPC信息，然后验证权限
    from ..database.config import get_session
    from ..database.models import NPC
    
    session = get_session()
    try:
        npc = session.query(NPC).filter_by(id=npc_id).first()
        if not npc:
            raise HTTPException(status_code=404, detail="NPC不存在")
        
        # 验证权限
        await verify_story_access(npc.story_id, current_user["id"])
        
        return npc.to_dict()
        
    finally:
        session.close()


@router.put("/{npc_id}", response_model=Dict[str, Any])
async def update_npc(
    npc_id: int,
    request: UpdateNPCRequest,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """更新NPC信息"""
    # 验证权限
    from ..database.config import get_session
    from ..database.models import NPC
    
    session = get_session()
    try:
        npc = session.query(NPC).filter_by(id=npc_id).first()
        if not npc:
            raise HTTPException(status_code=404, detail="NPC不存在")
        
        await verify_story_access(npc.story_id, current_user["id"])
        
    finally:
        session.close()
    
    # 准备更新数据
    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.personality is not None:
        update_data["personality"] = request.personality
    if request.background is not None:
        update_data["background"] = request.background
    if request.mood is not None:
        update_data["mood"] = request.mood
    if request.relations is not None:
        update_data["relations"] = request.relations
    if request.schedule is not None:
        update_data["schedule"] = request.schedule
    
    result = npc_db_service.update_npc(npc_id, **update_data)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result["data"]


@router.put("/{npc_id}/schedule", response_model=Dict[str, Any])
async def update_npc_schedule(
    npc_id: int,
    request: UpdateNPCScheduleRequest,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """更新NPC日程表"""
    # 验证权限
    from ..database.config import get_session
    from ..database.models import NPC
    
    session = get_session()
    try:
        npc = session.query(NPC).filter_by(id=npc_id).first()
        if not npc:
            raise HTTPException(status_code=404, detail="NPC不存在")
        
        await verify_story_access(npc.story_id, current_user["id"])
        
    finally:
        session.close()
    
    result = npc_db_service.update_npc_schedule(npc_id, request.schedule)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result["data"]


@router.put("/{npc_id}/relations", response_model=Dict[str, Any])
async def update_npc_relations(
    npc_id: int,
    request: UpdateNPCRelationsRequest,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """更新NPC人物关系"""
    # 验证权限
    from ..database.config import get_session
    from ..database.models import NPC
    
    session = get_session()
    try:
        npc = session.query(NPC).filter_by(id=npc_id).first()
        if not npc:
            raise HTTPException(status_code=404, detail="NPC不存在")
        
        await verify_story_access(npc.story_id, current_user["id"])
        
    finally:
        session.close()
    
    result = npc_db_service.update_npc_relations(npc_id, request.relations)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result["data"]


@router.delete("/{npc_id}", response_model=Dict[str, str])
async def delete_npc(
    npc_id: int,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """删除NPC"""
    # 验证权限
    from ..database.config import get_session
    from ..database.models import NPC
    
    session = get_session()
    try:
        npc = session.query(NPC).filter_by(id=npc_id).first()
        if not npc:
            raise HTTPException(status_code=404, detail="NPC不存在")
        
        await verify_story_access(npc.story_id, current_user["id"])
        
    finally:
        session.close()
    
    result = npc_db_service.delete_npc(npc_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": result["message"]} 