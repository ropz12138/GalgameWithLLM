"""
LLM客户端工具类 - 统一管理LLM调用
"""
import os
import json
import logging
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM客户端类"""
    
    def __init__(self):
        self._llm_instance = None
        self._config = None
        self._load_config()
        self._initialize_llm()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '../../config/config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            logger.info("✅ 配置文件加载成功")
        except Exception as e:
            logger.error(f"❌ 配置文件加载失败: {e}")
            self._config = {}
    
    def _initialize_llm(self):
        """初始化LLM实例"""
        try:
            if not self._config or 'llm' not in self._config:
                logger.error("❌ 配置文件中未找到LLM配置")
                return
            
            # 默认使用gemini配置
            llm_configs = self._config['llm']
            
            # 按优先级选择可用的LLM
            for provider in ['gemini', 'qwen', 'doubao', 'xai']:
                if provider in llm_configs:
                    config = llm_configs[provider]
                    logger.info(f"🔧 使用LLM配置: {provider}")
                    
                    self._llm_instance = ChatOpenAI(
                        api_key=config['api_key'],
                        base_url=config['url'],
                        model=config['model'],
                        temperature=0.7,
                        max_tokens=2000,
                        timeout=30
                    )
                    
                    logger.info(f"✅ LLM客户端初始化成功 - 提供商: {provider}, 模型: {config['model']}")
                    return
            
            logger.error("❌ 未找到可用的LLM配置")
            
        except Exception as e:
            logger.error(f"❌ LLM客户端初始化失败: {e}")
            self._llm_instance = None
    
    def get_llm_instance(self):
        """获取LLM实例"""
        if self._llm_instance is None:
            self._initialize_llm()
        return self._llm_instance
    
    async def chat_completion(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        调用LLM进行对话完成
        
        Args:
            prompt: 用户提示词
            system_message: 系统消息（可选）
            
        Returns:
            LLM响应
        """
        try:
            llm = self.get_llm_instance()
            if llm is None:
                return "抱歉，LLM服务暂时不可用。"
            
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(HumanMessage(content=prompt))
            
            response = await llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"❌ LLM调用失败: {e}")
            return "抱歉，LLM服务暂时不可用。"
    
    def get_current_model_info(self) -> Dict[str, Any]:
        """获取当前使用的模型信息"""
        if not self._config or 'llm' not in self._config:
            return {}
        
        llm_configs = self._config['llm']
        for provider in ['gemini', 'qwen', 'doubao', 'xai']:
            if provider in llm_configs:
                config = llm_configs[provider]
                return {
                    'provider': provider,
                    'model': config['model'],
                    'url': config['url']
                }
        return {}

    def is_available(self) -> bool:
        """检查LLM是否可用"""
        return self._llm_instance is not None 