"""
验证工具类 - 提供数据验证功能
"""
import re
from typing import Dict, Any, List, Optional


class ValidationUtils:
    """验证工具类"""
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """
        验证会话ID格式
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否有效
        """
        if not session_id:
            return False
        
        # 会话ID应该只包含字母、数字、下划线和连字符
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, session_id))
    
    @staticmethod
    def validate_action(action: str) -> bool:
        """
        验证玩家行动格式
        
        Args:
            action: 玩家行动
            
        Returns:
            是否有效
        """
        if not action or len(action.strip()) == 0:
            return False
        
        # 行动长度限制
        if len(action) > 500:
            return False
        
        return True
    
    @staticmethod
    def validate_npc_name(npc_name: str) -> bool:
        """
        验证NPC名称格式
        
        Args:
            npc_name: NPC名称
            
        Returns:
            是否有效
        """
        if not npc_name or len(npc_name.strip()) == 0:
            return False
        
        # NPC名称长度限制
        if len(npc_name) > 50:
            return False
        
        return True
    
    @staticmethod
    def validate_message(message: str) -> bool:
        """
        验证消息格式
        
        Args:
            message: 消息内容
            
        Returns:
            是否有效
        """
        if not message or len(message.strip()) == 0:
            return False
        
        # 消息长度限制
        if len(message) > 1000:
            return False
        
        return True
    
    @staticmethod
    def validate_model_name(model_name: str) -> bool:
        """
        验证模型名称
        
        Args:
            model_name: 模型名称
            
        Returns:
            是否有效
        """
        valid_models = ["gemini", "doubao", "xai", "qwen"]
        return model_name in valid_models
    
    @staticmethod
    def validate_prompt(prompt: str) -> bool:
        """
        验证提示词格式
        
        Args:
            prompt: 提示词
            
        Returns:
            是否有效
        """
        if not prompt or len(prompt.strip()) == 0:
            return False
        
        # 提示词长度限制
        if len(prompt) > 5000:
            return False
        
        return True
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        清理输入字符串
        
        Args:
            input_str: 输入字符串
            
        Returns:
            清理后的字符串
        """
        if not input_str:
            return ""
        
        # 移除首尾空白字符
        cleaned = input_str.strip()
        
        # 移除可能的危险字符（根据需要调整）
        # 这里只是基本清理，实际应用中可能需要更严格的验证
        cleaned = re.sub(r'[<>"\']', '', cleaned)
        
        return cleaned
    
    @staticmethod
    def validate_game_state(game_state: Dict[str, Any]) -> List[str]:
        """
        验证游戏状态数据
        
        Args:
            game_state: 游戏状态数据
            
        Returns:
            错误列表
        """
        errors = []
        
        required_fields = [
            "player_location", "current_time", "messages",
            "npc_locations", "npc_moods", "npc_dialogue_histories"
        ]
        
        for field in required_fields:
            if field not in game_state:
                errors.append(f"缺少必需字段: {field}")
        
        # 验证玩家位置
        if "player_location" in game_state:
            if not game_state["player_location"]:
                errors.append("玩家位置不能为空")
        
        # 验证时间格式
        if "current_time" in game_state:
            time_str = game_state["current_time"]
            if not re.match(r'^\d{2}:\d{2}$', time_str):
                errors.append("时间格式无效，应为 HH:MM 格式")
        
        return errors
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> List[str]:
        """
        验证配置数据
        
        Args:
            config: 配置数据
            
        Returns:
            错误列表
        """
        errors = []
        
        # 验证LLM配置
        if "llm" in config:
            llm_config = config["llm"]
            for model_name, model_config in llm_config.items():
                if not isinstance(model_config, dict):
                    errors.append(f"LLM配置 {model_name} 格式无效")
                    continue
                
                required_fields = ["url", "model", "api_key"]
                for field in required_fields:
                    if field not in model_config:
                        errors.append(f"LLM配置 {model_name} 缺少字段: {field}")
        
        return errors 