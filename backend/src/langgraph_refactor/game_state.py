"""
LangGraph游戏状态定义
"""
from typing_extensions import TypedDict
from typing import Annotated, List, Dict, Any, Optional
import operator
from datetime import datetime

class GameState(TypedDict):
    # 玩家状态
    player_location: str
    player_personality: str  
    current_time: str
    
    # 消息历史 - 使用operator.add进行累加
    messages: Annotated[List[Dict[str, str]], operator.add]
    
    # NPC状态
    npc_locations: Dict[str, str]
    npc_moods: Dict[str, str]
    npc_dialogue_histories: Annotated[Dict[str, List[Dict]], lambda x, y: {**x, **y}]
    npc_dynamic_data: Annotated[Dict[str, Dict], lambda x, y: {**x, **y}]  # 动态修改的NPC数据（包括计划表）
    
    # 游戏事件
    game_events: Annotated[List[Dict[str, Any]], operator.add]
    
    # 当前操作上下文
    current_action: str
    action_target: Optional[str]
    
    # 复合指令支持
    compound_actions: Optional[List[Any]]  # 改为Any类型以支持SubAction对象
    
    # 系统状态
    last_update_time: str
    session_id: str
    
    # 工作流控制
    next_node: Optional[str]


def create_initial_state(session_id: str = "default") -> GameState:
    """创建初始游戏状态"""
    from datetime import datetime
    from utils.config_loader import get_user_place, get_init_time
    
    current_time = datetime.now().strftime("%H:%M")
    game_time = get_init_time()  # 从配置文件获取游戏开始时间
    player_location = get_user_place()  # 从配置文件获取玩家初始位置
    
    # 初始化NPC位置（根据游戏时间）
    initial_npc_locations = {}
    from datetime import datetime
    game_time_obj = datetime.strptime(game_time, "%H:%M").time()
    
    # 导入NPC数据
    try:
        from data.characters import all_actresses
        from data.locations import location_name_map
        
        for actress in all_actresses:
            npc_name = actress["name"]
            npc_location = "未知地点"
            
            # 查找当前时间的活动
            for event_info in actress.get("schedule", []):
                try:
                    start_time = datetime.strptime(event_info["start_time"], "%H:%M").time()
                    end_time = datetime.strptime(event_info["end_time"], "%H:%M").time()
                    
                    if start_time <= game_time_obj < end_time:
                        npc_location = location_name_map.get(event_info["location"], event_info["location"])
                        break
                except ValueError:
                    continue
            
            # 如果没找到当前活动，使用默认位置
            if npc_location == "未知地点":
                npc_location = location_name_map.get(actress.get("default_location", player_location), player_location)
            
            initial_npc_locations[npc_name] = npc_location
            
    except ImportError as e:
        print(f"导入NPC数据时出错: {e}")
        # 设置默认NPC位置
        initial_npc_locations = {
            "林若曦": "林若曦房间",
            "张雨晴": "张雨晴房间"
        }
    
    return {
        "player_location": player_location,
        "player_personality": "普通",
        "current_time": game_time,
        "messages": [],
        "npc_locations": initial_npc_locations,
        "npc_moods": {},
        "npc_dialogue_histories": {},
        "npc_dynamic_data": {},
        "game_events": [],
        "current_action": "",
        "action_target": None,
        "compound_actions": None,
        "last_update_time": current_time,
        "session_id": session_id,
        "next_node": None
    }


def create_message(speaker: str, content: str, message_type: str = "normal") -> Dict[str, str]:
    """创建标准化消息格式"""
    return {
        "speaker": speaker,
        "message": content,
        "type": message_type,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }


def create_game_event(event_type: str, **kwargs) -> Dict[str, Any]:
    """创建游戏事件"""
    return {
        "type": event_type,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        **kwargs
    } 