"""
LLM路由 - 定义LLM相关的API端点
"""
from typing import Dict, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from controllers.llm_controller import LLMController

# 创建路由器
llm_router = APIRouter(prefix="/api/llm", tags=["LLM"])

# 创建控制器实例
llm_controller = LLMController()


# 请求模型
class LLMRequest(BaseModel):
    prompt: str = Field(description="提示词")
    model_name: str = Field(default="gemini", description="模型名称")


# API端点
@llm_router.get("/models")
async def get_available_models():
    """
    获取可用的模型列表
    
    Returns:
        可用模型配置
    """
    return llm_controller.get_available_models()


@llm_router.get("/test_connection")
async def test_llm_connection(model_name: str = Query(default="gemini", description="模型名称")):
    """
    测试LLM连接
    
    Args:
        model_name: 模型名称
        
    Returns:
        测试结果
    """
    return llm_controller.test_llm_connection(model_name)


@llm_router.post("/invoke")
async def invoke_llm(request: LLMRequest):
    """
    调用LLM
    
    Args:
        request: LLM请求
        
    Returns:
        LLM响应
    """
    return await llm_controller.invoke_llm(request.prompt, request.model_name)


@llm_router.post("/reset")
async def reset_llm_instance():
    """
    重置LLM实例
    
    Returns:
        重置结果
    """
    return llm_controller.reset_llm_instance()


@llm_router.get("/config/{model_name}")
async def get_llm_config(model_name: str):
    """
    获取LLM配置
    
    Args:
        model_name: 模型名称
        
    Returns:
        LLM配置（隐藏敏感信息）
    """
    return llm_controller.get_llm_config(model_name) 