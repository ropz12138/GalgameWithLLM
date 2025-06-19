"""
LLM控制器 - 处理LLM相关的HTTP请求
"""
from typing import Dict, Any
from fastapi import HTTPException

from services.llm_service import LLMService


class LLMController:
    """LLM控制器类"""
    
    def __init__(self):
        self.llm_service = LLMService()
    
    def get_available_models(self) -> Dict[str, Dict[str, str]]:
        """
        获取可用的模型列表
        
        Returns:
            可用模型配置
        """
        try:
            return self.llm_service.get_available_models()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取可用模型失败: {str(e)}")
    
    def test_llm_connection(self, model_name: str = "gemini") -> Dict[str, Any]:
        """
        测试LLM连接
        
        Args:
            model_name: 模型名称
            
        Returns:
            测试结果
        """
        try:
            return self.llm_service.test_llm_connection(model_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"测试LLM连接失败: {str(e)}")
    
    async def invoke_llm(self, prompt: str, model_name: str = "gemini") -> Dict[str, str]:
        """
        调用LLM
        
        Args:
            prompt: 提示词
            model_name: 模型名称
            
        Returns:
            LLM响应
        """
        try:
            response = await self.llm_service.invoke_llm(prompt, model_name)
            return {"response": response}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"调用LLM失败: {str(e)}")
    
    def reset_llm_instance(self) -> Dict[str, str]:
        """
        重置LLM实例
        
        Returns:
            重置结果
        """
        try:
            self.llm_service.reset_llm_instance()
            return {"message": "LLM实例已重置"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"重置LLM实例失败: {str(e)}")
    
    def get_llm_config(self, model_name: str = "gemini") -> Dict[str, str]:
        """
        获取LLM配置
        
        Args:
            model_name: 模型名称
            
        Returns:
            LLM配置
        """
        try:
            config = self.llm_service.get_llm_config(model_name)
            if config:
                # 隐藏敏感信息
                safe_config = config.copy()
                if "api_key" in safe_config:
                    safe_config["api_key"] = "***" + safe_config["api_key"][-4:]
                return safe_config
            else:
                raise HTTPException(status_code=404, detail=f"未找到模型 {model_name} 的配置")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取LLM配置失败: {str(e)}") 