"""
LLM服务 - 处理大语言模型相关逻辑
"""
import os
import json
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI


class LLMService:
    """LLM服务类"""
    
    def __init__(self):
        self._llm_instance = None
        self._config = None
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """从config.json加载配置"""
        if self._config is not None:
            return self._config
        
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
                return self._config
        except FileNotFoundError:
            print(f"⚠️  配置文件未找到: {config_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误: {e}")
            return None

    def get_llm_config(self, model_name: str = "gemini") -> Optional[Dict[str, str]]:
        """
        获取LLM配置
        
        Args:
            model_name: 模型名称 (gemini, doubao, xai, qwen)
            
        Returns:
            LLM配置
        """
        config = self.load_config()
        if not config:
            # 使用默认配置作为后备
            return {
                "url": "https://generativelanguage.googleapis.com/v1beta/openai/",
                "model": "gemini-2.5-flash-preview-05-20",
                "api_key": "AIzaSyDTjUqOBRlJpY9H55Bb5dzOQ8JyhgrirzE"
            }
        
        # 获取指定模型的配置
        llm_config = config.get("llm", {}).get(model_name, {})
        if not llm_config:
            print(f"⚠️  未找到{model_name}配置，尝试使用第一个可用的LLM配置")
            # 获取第一个可用的LLM配置
            llm_configs = config.get("llm", {})
            if llm_configs:
                first_config = list(llm_configs.values())[0]
                llm_config = first_config
            else:
                print("❌ 未找到任何LLM配置")
                return None
        
        return llm_config

    def get_llm_instance(self, model_name: str = "gemini") -> ChatOpenAI:
        """
        获取LLM实例
        
        Args:
            model_name: 模型名称
            
        Returns:
            LLM实例
        """
        if self._llm_instance is None:
            llm_config = self.get_llm_config(model_name)
            if not llm_config:
                raise ValueError("无法获取LLM配置")
            
            print(f"🔧 使用LLM配置: {llm_config.get('model', 'unknown')}")
            
            self._llm_instance = ChatOpenAI(
                model_name=llm_config.get("model", "gemini-2.5-flash-preview-05-20"),
                openai_api_key=llm_config.get("api_key"),
                openai_api_base=llm_config.get("url"),
                temperature=0.7,
            )
        
        return self._llm_instance
    
    def clean_llm_response(self, response) -> str:
        """
        清理LLM响应，确保只返回content内容
        
        Args:
            response: LLM响应
            
        Returns:
            清理后的响应内容
        """
        if response is None:
            return ""
        
        # 如果是字符串，直接返回
        if isinstance(response, str):
            return response
        
        # 如果有content属性，返回content
        if hasattr(response, 'content'):
            return response.content
        
        # 如果是字典，尝试获取content
        if isinstance(response, dict):
            return response.get('content', str(response))
        
        # 其他情况转换为字符串
        return str(response)

    async def invoke_llm(self, prompt: str, model_name: str = "gemini") -> str:
        """
        调用LLM
        
        Args:
            prompt: 提示词
            model_name: 模型名称
            
        Returns:
            LLM响应
        """
        try:
            llm = self.get_llm_instance(model_name)
            response = await llm.ainvoke(prompt)
            return self.clean_llm_response(response)
        except Exception as e:
            print(f"调用LLM失败: {e}")
            return f"LLM调用失败: {str(e)}"
    
    def reset_llm_instance(self):
        """重置LLM实例"""
        self._llm_instance = None
    
    def get_available_models(self) -> Dict[str, Dict[str, str]]:
        """
        获取可用的模型列表
        
        Returns:
            可用模型配置
        """
        config = self.load_config()
        if not config:
            return {}
        
        return config.get("llm", {})
    
    def test_llm_connection(self, model_name: str = "gemini") -> Dict[str, Any]:
        """
        测试LLM连接
        
        Args:
            model_name: 模型名称
            
        Returns:
            测试结果
        """
        try:
            llm = self.get_llm_instance(model_name)
            response = llm.invoke("你好，请简单回复'连接成功'。")
            content = self.clean_llm_response(response)
            
            return {
                "success": True,
                "model": model_name,
                "response": content,
                "message": "连接成功"
            }
        except Exception as e:
            return {
                "success": False,
                "model": model_name,
                "error": str(e),
                "message": "连接失败"
            }

if __name__ == "__main__":
    # Test the LLM instance
    try:
        llm_service = LLMService()
        response = llm_service.get_llm_instance().invoke("你好，请介绍一下你自己。")
        print("LLM Response:", response)
        print("Cleaned Response:", llm_service.clean_llm_response(response))
    except Exception as e:
        print(f"Error invoking LLM: {e}")

