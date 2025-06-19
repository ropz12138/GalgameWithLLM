"""
NPC模型 - 定义NPC相关的数据结构
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


class NPCModel:
    """NPC模型类"""
    
    def __init__(self, name: str):
        self.name = name
        self.location = "未知地点"
        self.mood = "普通"
        self.personality = "友善"
        self.schedule: List[Dict[str, Any]] = []
        self.dialogue_history: List[Dict[str, str]] = []
        self.relationships: Dict[str, Dict[str, Any]] = {}
        self.dynamic_data: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.last_interaction = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "location": self.location,
            "mood": self.mood,
            "personality": self.personality,
            "schedule": self.schedule,
            "dialogue_history": self.dialogue_history,
            "relationships": self.relationships,
            "dynamic_data": self.dynamic_data,
            "created_at": self.created_at.isoformat(),
            "last_interaction": self.last_interaction.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NPCModel':
        """从字典创建实例"""
        instance = cls(data.get("name", "未知NPC"))
        instance.location = data.get("location", "未知地点")
        instance.mood = data.get("mood", "普通")
        instance.personality = data.get("personality", "友善")
        instance.schedule = data.get("schedule", [])
        instance.dialogue_history = data.get("dialogue_history", [])
        instance.relationships = data.get("relationships", {})
        instance.dynamic_data = data.get("dynamic_data", {})
        instance.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        instance.last_interaction = datetime.fromisoformat(data.get("last_interaction", datetime.now().isoformat()))
        return instance
    
    def move_to(self, new_location: str):
        """移动到新位置"""
        self.location = new_location
        self.last_interaction = datetime.now()
    
    def update_mood(self, new_mood: str):
        """更新心情"""
        self.mood = new_mood
        self.last_interaction = datetime.now()
    
    def add_dialogue(self, speaker: str, message: str, message_type: str = "normal"):
        """添加对话记录"""
        self.dialogue_history.append({
            "speaker": speaker,
            "message": message,
            "type": message_type,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        self.last_interaction = datetime.now()
    
    def update_relationship(self, target_name: str, relationship_data: Dict[str, Any]):
        """更新与其他角色的关系"""
        self.relationships[target_name] = relationship_data
        self.last_interaction = datetime.now()
    
    def update_dynamic_data(self, key: str, value: Any):
        """更新动态数据"""
        self.dynamic_data[key] = value
        self.last_interaction = datetime.now()
    
    def get_current_activity(self, current_time: str) -> Dict[str, Any]:
        """获取当前时间的活动"""
        current_time_obj = datetime.strptime(current_time, "%H:%M").time()
        
        for event in self.schedule:
            try:
                start_time = datetime.strptime(event["start_time"], "%H:%M").time()
                end_time = datetime.strptime(event["end_time"], "%H:%M").time()
                
                if start_time <= current_time_obj < end_time:
                    return event
            except (ValueError, KeyError):
                continue
        
        return {"activity": "空闲", "location": self.location} 