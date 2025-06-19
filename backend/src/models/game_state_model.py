"""
游戏状态模型 - 定义游戏状态的数据结构
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


class GameStateModel:
    """游戏状态模型类"""
    
    def __init__(self, session_id: str = "default"):
        from utils.config_loader import get_user_place, get_init_time
        
        self.session_id = session_id
        self.player_location = get_user_place()  # 从配置文件获取玩家初始位置
        self.player_personality = "普通"
        self.current_time = get_init_time()  # 从配置文件获取游戏初始时间
        self.messages: List[Dict[str, str]] = []
        self.npc_locations: Dict[str, str] = {}
        self.npc_moods: Dict[str, str] = {}
        self.npc_dialogue_histories: Dict[str, List[Dict]] = {}
        self.npc_dynamic_data: Dict[str, Dict] = {}
        self.game_events: List[Dict[str, Any]] = []
        self.current_action = ""
        self.action_target: Optional[str] = None
        self.compound_actions: Optional[List[Any]] = None
        self.last_update_time = datetime.now().strftime("%H:%M:%S")
        self.next_node: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "session_id": self.session_id,
            "player_location": self.player_location,
            "player_personality": self.player_personality,
            "current_time": self.current_time,
            "messages": self.messages,
            "npc_locations": self.npc_locations,
            "npc_moods": self.npc_moods,
            "npc_dialogue_histories": self.npc_dialogue_histories,
            "npc_dynamic_data": self.npc_dynamic_data,
            "game_events": self.game_events,
            "current_action": self.current_action,
            "action_target": self.action_target,
            "compound_actions": self.compound_actions,
            "last_update_time": self.last_update_time,
            "next_node": self.next_node
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameStateModel':
        """从字典创建实例"""
        from utils.config_loader import get_user_place, get_init_time
        
        instance = cls(data.get("session_id", "default"))
        instance.player_location = data.get("player_location", get_user_place())
        instance.player_personality = data.get("player_personality", "普通")
        instance.current_time = data.get("current_time", get_init_time())
        instance.messages = data.get("messages", [])
        instance.npc_locations = data.get("npc_locations", {})
        instance.npc_moods = data.get("npc_moods", {})
        instance.npc_dialogue_histories = data.get("npc_dialogue_histories", {})
        instance.npc_dynamic_data = data.get("npc_dynamic_data", {})
        instance.game_events = data.get("game_events", [])
        instance.current_action = data.get("current_action", "")
        instance.action_target = data.get("action_target")
        instance.compound_actions = data.get("compound_actions")
        instance.last_update_time = data.get("last_update_time", datetime.now().strftime("%H:%M:%S"))
        instance.next_node = data.get("next_node")
        return instance
    
    def add_message(self, speaker: str, message: str, message_type: str = "normal"):
        """添加消息"""
        self.messages.append({
            "speaker": speaker,
            "message": message,
            "type": message_type,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    
    def update_location(self, new_location: str):
        """更新玩家位置"""
        self.player_location = new_location
        self.last_update_time = datetime.now().strftime("%H:%M:%S")
    
    def update_time(self, new_time: str):
        """更新时间"""
        self.current_time = new_time
        self.last_update_time = datetime.now().strftime("%H:%M:%S") 