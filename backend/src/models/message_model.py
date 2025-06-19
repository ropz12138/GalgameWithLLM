"""
消息模型 - 定义消息相关的数据结构
"""
from typing import Dict, Any, Optional
from datetime import datetime


class MessageModel:
    """消息模型类"""
    
    def __init__(self, speaker: str, message: str, message_type: str = "normal"):
        self.speaker = speaker
        self.message = message
        self.message_type = message_type
        self.timestamp = datetime.now()
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "speaker": self.speaker,
            "message": self.message,
            "type": self.message_type,
            "timestamp": self.timestamp.strftime("%H:%M:%S"),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageModel':
        """从字典创建实例"""
        instance = cls(
            data.get("speaker", "系统"),
            data.get("message", ""),
            data.get("type", "normal")
        )
        instance.timestamp = datetime.strptime(data.get("timestamp", datetime.now().strftime("%H:%M:%S")), "%H:%M:%S")
        instance.metadata = data.get("metadata", {})
        return instance
    
    def add_metadata(self, key: str, value: Any):
        """添加元数据"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据"""
        return self.metadata.get(key, default)
    
    def is_system_message(self) -> bool:
        """是否为系统消息"""
        return self.speaker == "系统" or self.message_type == "system"
    
    def is_npc_message(self) -> bool:
        """是否为NPC消息"""
        return self.speaker not in ["玩家", "系统", "游戏"] and not self.is_system_message()
    
    def is_player_message(self) -> bool:
        """是否为玩家消息"""
        return self.speaker == "玩家" or self.message_type == "player" 