"""
位置数据库路由 - 定义位置相关的API端点
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..services.location_db_service import location_db_service
from ..services.story_service import story_service
from ..services.auth_service import auth_service


# 请求模型
class CreateLocationRequest(BaseModel):
    story_id: int = Field(..., description="故事ID")
    key: str = Field(..., description="位置键名")
    name: str = Field(..., description="位置名称")
    en_name: str = Field(None, description="英文名称")
    description: str = Field(None, description="位置描述")
    connections: List[str] = Field(default_factory=list, description="连接的位置")


class UpdateLocationRequest(BaseModel):
    key: str = Field(None, description="位置键名")
    name: str = Field(None, description="位置名称")
    en_name: str = Field(None, description="英文名称")
    description: str = Field(None, description="位置描述")
    connections: List[str] = Field(None, description="连接的位置")


# 创建路由器
router = APIRouter(prefix="/api/locations", tags=["位置管理"])


async def verify_story_access(story_id: int, user_id: int):
    """验证用户对故事的访问权限"""
    story_result = story_service.get_story_by_id(story_id)
    if not story_result["success"]:
        raise HTTPException(status_code=404, detail="故事不存在")
    
    story = story_result["data"]
    if story["creator_id"] != user_id:
        raise HTTPException(status_code=403, detail="无权限访问此故事")


@router.post("/", response_model=Dict[str, Any])
async def create_location(
    request: CreateLocationRequest,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """创建新位置"""
    # 验证权限
    await verify_story_access(request.story_id, current_user["id"])
    
    result = location_db_service.create_location(
        story_id=request.story_id,
        key=request.key,
        name=request.name,
        en_name=request.en_name,
        description=request.description,
        connections=request.connections
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result["data"]


@router.get("/story/{story_id}", response_model=List[Dict[str, Any]])
async def get_story_locations(
    story_id: int,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """获取故事的所有位置"""
    # 验证权限
    await verify_story_access(story_id, current_user["id"])
    
    result = location_db_service.get_locations_by_story(story_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result["data"]


@router.get("/{location_id}", response_model=Dict[str, Any])
async def get_location_by_id(
    location_id: int,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """根据ID获取位置"""
    # 这里需要先获取位置信息，然后验证权限
    from ..database.config import get_session
    from ..database.models import Location
    
    session = get_session()
    try:
        location = session.query(Location).filter_by(id=location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="位置不存在")
        
        # 验证权限
        await verify_story_access(location.story_id, current_user["id"])
        
        return location.to_dict()
        
    finally:
        session.close()


@router.put("/{location_id}", response_model=Dict[str, Any])
async def update_location(
    location_id: int,
    request: UpdateLocationRequest,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """更新位置信息"""
    # 验证权限
    from ..database.config import get_session
    from ..database.models import Location
    
    session = get_session()
    try:
        location = session.query(Location).filter_by(id=location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="位置不存在")
        
        await verify_story_access(location.story_id, current_user["id"])
        
    finally:
        session.close()
    
    # 准备更新数据
    update_data = {}
    if request.key is not None:
        update_data["key"] = request.key
    if request.name is not None:
        update_data["name"] = request.name
    if request.en_name is not None:
        update_data["en_name"] = request.en_name
    if request.description is not None:
        update_data["description"] = request.description
    if request.connections is not None:
        update_data["connections"] = request.connections
    
    result = location_db_service.update_location(location_id, **update_data)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result["data"]


@router.delete("/{location_id}", response_model=Dict[str, str])
async def delete_location(
    location_id: int,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """删除位置"""
    # 验证权限
    from ..database.config import get_session
    from ..database.models import Location
    
    session = get_session()
    try:
        location = session.query(Location).filter_by(id=location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="位置不存在")
        
        await verify_story_access(location.story_id, current_user["id"])
        
    finally:
        session.close()
    
    result = location_db_service.delete_location(location_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": result["message"]} 