"""
NPC服务 - 处理NPC相关逻辑
"""
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, time

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(os.path.dirname(SRC_DIR))
sys.path.append(PROJECT_ROOT)
sys.path.append(SRC_DIR)

from ..models.game_state_model import GameStateModel
import sys
import os
# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from data.characters import all_actresses
from data.locations import all_locations_data


class NPCService:
    """NPC服务类"""
    
    def __init__(self):
        pass
    
    def update_npc_locations_by_time(self, current_time: str, game_state: GameStateModel = None) -> Dict[str, str]:
        """根据时间更新NPC位置"""
        print(f"\n📍 [NPCService] 根据时间更新NPC位置 - 当前时间: {current_time}")
        
        npc_locations = {}
        
        for actress in all_actresses:
            npc_name = actress["name"]
            location, event = self.get_npc_current_location_and_event(npc_name, current_time, game_state)
            npc_locations[npc_name] = location
            print(f"  📍 {npc_name}: {location} (正在{event})")
        
        return npc_locations
    
    def get_npc_current_location_and_event(self, npc_name: str, current_time, game_state: GameStateModel = None) -> Tuple[str, str]:
        """获取NPC当前位置和活动"""
        # 查找NPC数据
        npc_obj = next((a for a in all_actresses if a['name'] == npc_name), None)
        if not npc_obj:
            print(f"❌ 未找到NPC: {npc_name}")
            return "unknown_location", "未知活动"
        
        # 获取当前有效的计划表（优先使用动态计划表）
        schedule = self.get_npc_current_schedule(npc_name, game_state)
        if not schedule:
            print(f"❌ {npc_name} 没有计划表")
            return "unknown_location", "空闲"
        
        # 查找当前时间对应的活动
        for item in schedule:
            # 使用TimeUtils判断时间范围
            from ..utils.time_utils import TimeUtils
            
            if TimeUtils.is_time_in_range(current_time, item["start_time"], item["end_time"]):
                location = item["location"]
                event = item["event"]
                print(f"✅ {npc_name} 在 {location} 进行 {event}")
                return location, event
        
        # 如果没有找到对应的时间段，使用最后一个计划或默认位置
        if schedule:
            last_item = schedule[-1]
            location = last_item["location"]
            event = "空闲"
            print(f"⚠️ {npc_name} 当前时间无计划，使用最后位置: {location}")
            return location, event
        
        print(f"❌ {npc_name} 无法确定位置")
        return "unknown_location", "空闲"
    
    def get_npc_by_name(self, npc_name: str) -> Optional[dict]:
        """根据名称获取NPC数据"""
        return next((a for a in all_actresses if a['name'] == npc_name), None)
    
    def get_all_npcs(self) -> List[dict]:
        """获取所有NPC数据"""
        return all_actresses.copy()
    
    def get_npc_mood(self, npc_name: str, game_state: GameStateModel) -> str:
        """获取NPC当前心情"""
        # 优先从游戏状态获取
        if hasattr(game_state, 'npc_moods') and npc_name in game_state.npc_moods:
            return game_state.npc_moods[npc_name]
        
        # 从NPC数据获取默认心情
        npc_obj = self.get_npc_by_name(npc_name)
        if npc_obj:
            return npc_obj.get("mood", "平静")
        
        return "平静"
    
    def update_npc_mood(self, npc_name: str, new_mood: str, game_state: GameStateModel) -> bool:
        """更新NPC心情"""
        try:
            if not hasattr(game_state, 'npc_moods'):
                game_state.npc_moods = {}
            
            game_state.npc_moods[npc_name] = new_mood
            print(f"✅ 更新 {npc_name} 心情为: {new_mood}")
            return True
        except Exception as e:
            print(f"❌ 更新NPC心情失败: {e}")
            return False
    
    def get_npc_dialogue_history(self, npc_name: str, game_state: GameStateModel) -> List[Dict]:
        """获取NPC对话历史"""
        if hasattr(game_state, 'npc_dialogue_histories'):
            return game_state.npc_dialogue_histories.get(npc_name, [])
        return []
    
    def add_dialogue_to_history(self, npc_name: str, speaker: str, message: str, timestamp: str, game_state: GameStateModel):
        """添加对话到历史记录"""
        if not hasattr(game_state, 'npc_dialogue_histories'):
            game_state.npc_dialogue_histories = {}
        
        if npc_name not in game_state.npc_dialogue_histories:
            game_state.npc_dialogue_histories[npc_name] = []
        
        dialogue_entry = {
            "speaker": speaker,
            "message": message,
            "timestamp": timestamp
        }
        
        game_state.npc_dialogue_histories[npc_name].append(dialogue_entry)
        print(f"✅ 添加对话到 {npc_name} 的历史记录: {speaker}: {message[:50]}...")
    
    def get_npc_schedule(self, npc_name: str) -> List[Dict]:
        """获取NPC的计划表"""
        npc_obj = self.get_npc_by_name(npc_name)
        if npc_obj:
            return npc_obj.get("schedule", [])
        return []
    
    def get_npc_personality(self, npc_name: str) -> str:
        """获取NPC性格"""
        npc_obj = self.get_npc_by_name(npc_name)
        if npc_obj:
            return npc_obj.get("personality", "")
        return ""
    
    def get_npc_background(self, npc_name: str) -> str:
        """获取NPC背景"""
        npc_obj = self.get_npc_by_name(npc_name)
        if npc_obj:
            return npc_obj.get("background", "")
        return ""
    
    def get_npc_relations(self, npc_name: str) -> Dict:
        """获取NPC关系"""
        npc_obj = self.get_npc_by_name(npc_name)
        if npc_obj:
            return npc_obj.get("relations", {})
        return {}
    
    def update_npc_schedule(self, npc_name: str, new_schedule_item: Dict, game_state: GameStateModel) -> bool:
        """
        动态更新NPC计划表（单个项目，保留兼容性）
        
        Args:
            npc_name: NPC名称
            new_schedule_item: 新的计划项
            game_state: 游戏状态
            
        Returns:
            是否更新成功
        """
        # 调用新的完整计划表更新方法
        current_schedule = self.get_npc_current_schedule(npc_name, game_state)
        
        # 构建新的完整计划表
        new_complete_schedule = []
        new_start = datetime.strptime(new_schedule_item["start_time"], "%H:%M").time()
        new_end = datetime.strptime(new_schedule_item["end_time"], "%H:%M").time()
        
        # 移除冲突的计划项，保留其他项
        for item in current_schedule:
            item_start = datetime.strptime(item["start_time"], "%H:%M").time()
            item_end = datetime.strptime(item["end_time"], "%H:%M").time()
            
            # 检查时间冲突
            if not (new_end <= item_start or new_start >= item_end):
                continue  # 跳过冲突项
            
            new_complete_schedule.append(item)
        
        # 添加新计划项
        new_complete_schedule.append(new_schedule_item)
        
        # 按时间排序
        new_complete_schedule.sort(key=lambda x: datetime.strptime(x["start_time"], "%H:%M").time())
        
        return self.replace_npc_complete_schedule(npc_name, new_complete_schedule, game_state)
    
    def replace_npc_complete_schedule(self, npc_name: str, new_complete_schedule: List[Dict], game_state: GameStateModel) -> bool:
        """
        替换NPC的完整计划表
        
        Args:
            npc_name: NPC名称
            new_complete_schedule: 新的完整计划表
            game_state: 游戏状态
            
        Returns:
            是否更新成功
        """
        try:
            print(f"\n📅 [NPCService] 替换 {npc_name} 的完整计划表")
            
            # 确保游戏状态有动态计划表字段
            if not hasattr(game_state, 'npc_dynamic_schedules'):
                game_state.npc_dynamic_schedules = {}
            
            # 更新动态计划表
            game_state.npc_dynamic_schedules[npc_name] = new_complete_schedule
            
            print(f"  ✅ 计划表已完全替换，新计划表:")
            for item in new_complete_schedule:
                print(f"    {item['start_time']}-{item['end_time']} 在{item['location']}：{item['event']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 替换NPC完整计划表失败: {e}")
            return False
    
    def get_npc_current_schedule(self, npc_name: str, game_state: GameStateModel = None) -> List[Dict]:
        """
        获取NPC当前有效的计划表（优先使用动态计划表）
        
        Args:
            npc_name: NPC名称
            game_state: 游戏状态
            
        Returns:
            当前有效的计划表
        """
        # 优先使用动态计划表
        if game_state and hasattr(game_state, 'npc_dynamic_schedules') and npc_name in game_state.npc_dynamic_schedules:
            return game_state.npc_dynamic_schedules[npc_name]
        
        # 否则使用原始计划表
        return self.get_npc_schedule(npc_name) 