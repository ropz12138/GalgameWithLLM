"""
玩家模型 - 定义玩家相关的数据结构
"""
from typing import Dict, Any, Optional
from datetime import datetime


class PlayerModel:
    """玩家模型类"""
    
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.location = "linkai_room"
        self.personality = "普通"
        self.inventory: Dict[str, Any] = {}
        self.relationships: Dict[str, Dict[str, Any]] = {}
        self.stats: Dict[str, Any] = {
            "energy": 100,
            "mood": 50,
            "reputation": 0
        }
        self.created_at = datetime.now()
        self.last_active = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "session_id": self.session_id,
            "location": self.location,
            "personality": self.personality,
            "inventory": self.inventory,
            "relationships": self.relationships,
            "stats": self.stats,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerModel':
        """从字典创建实例"""
        instance = cls(data.get("session_id", "default"))
        instance.location = data.get("location", "linkai_room")
        instance.personality = data.get("personality", "普通")
        instance.inventory = data.get("inventory", {})
        instance.relationships = data.get("relationships", {})
        instance.stats = data.get("stats", {
            "energy": 100,
            "mood": 50,
            "reputation": 0
        })
        instance.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        instance.last_active = datetime.fromisoformat(data.get("last_active", datetime.now().isoformat()))
        return instance
    
    def move_to(self, new_location: str):
        """移动到新位置"""
        self.location = new_location
        self.last_active = datetime.now()
    
    def update_personality(self, new_personality: str):
        """更新性格"""
        self.personality = new_personality
        self.last_active = datetime.now()
    
    def add_item(self, item_name: str, item_data: Dict[str, Any]):
        """添加物品到背包"""
        self.inventory[item_name] = item_data
        self.last_active = datetime.now()
    
    def remove_item(self, item_name: str) -> bool:
        """从背包移除物品"""
        if item_name in self.inventory:
            del self.inventory[item_name]
            self.last_active = datetime.now()
            return True
        return False
    
    def update_relationship(self, npc_name: str, relationship_data: Dict[str, Any]):
        """更新与NPC的关系"""
        self.relationships[npc_name] = relationship_data
        self.last_active = datetime.now()
    
    def update_stat(self, stat_name: str, value: Any):
        """更新属性值"""
        self.stats[stat_name] = value
        self.last_active = datetime.now() 