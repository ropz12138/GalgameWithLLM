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

from ..services.npc_db_service import NPCDBService


class NPCService:
    """NPC服务类"""
    
    def __init__(self):
        self.npc_db_service = NPCDBService()
    
    def _get_all_npcs_for_story(self, story_id: int) -> List[Dict[str, Any]]:
        """从数据库获取指定故事的所有NPC数据"""
        try:
            result = self.npc_db_service.get_npcs_by_story(story_id)
            if result.get("success"):
                return result.get("data", [])
            else:
                print(f"❌ 获取故事NPC失败: {result.get('error')}")
                return []
        except Exception as e:
            print(f"❌ 获取故事NPC异常: {e}")
            return []
    
    def update_npc_locations_by_time(self, current_time: str, game_state: GameStateModel = None) -> Dict[str, str]:
        """根据时间更新NPC位置"""
        print(f"\n📍 [NPCService] 根据时间更新NPC位置 - 当前时间: {current_time}")
        
        if not game_state or not game_state.story_id:
            print("❌ 无法获取故事ID")
            return {}
        
        print(f"📊 故事ID: {game_state.story_id}")
        
        npc_locations = {}
        
        # 从数据库获取当前故事的所有NPC
        all_npcs = self._get_all_npcs_for_story(game_state.story_id)
        print(f"📊 从数据库获取的NPC数量: {len(all_npcs)}")
        
        for npc_data in all_npcs:
            npc_name = npc_data.get("name")
            print(f"🔍 处理NPC: {npc_name}")
            location, event = self.get_npc_current_location_and_event(npc_name, current_time, game_state)
            npc_locations[npc_name] = location
            print(f"  📍 {npc_name}: {location} (正在{event})")
        
        print(f"📊 最终NPC位置结果: {npc_locations}")
        return npc_locations
    
    def get_npc_current_location_and_event(self, npc_name: str, current_time: str, game_state: GameStateModel = None) -> Tuple[str, str]:
        """获取NPC当前位置和活动"""
        
        # 首先尝试从动态计划表获取
        if game_state and hasattr(game_state, 'npc_dynamic_schedules'):
            dynamic_schedule = game_state.npc_dynamic_schedules.get(npc_name)
            if dynamic_schedule:
                print(f"✅ {npc_name} 使用动态计划表")
                location, event = self._get_location_and_event_from_schedule(dynamic_schedule, current_time)
                if location != "unknown_location":
                    print(f"✅ {npc_name} 在 {location} 进行 {event}")
                    return location, event
        
        # 获取NPC的数据库记录
        if game_state and game_state.story_id:
            result = self.npc_db_service.get_npc_by_name(game_state.story_id, npc_name)
            if result.get("success"):
                npc_data = result.get("data", {})
                original_schedule = npc_data.get("schedule", [])
                if original_schedule:
                    print(f"✅ {npc_name} 使用数据库计划表")
                    location, event = self._get_location_and_event_from_schedule(original_schedule, current_time)
                    if location != "unknown_location":
                        print(f"✅ {npc_name} 在 {location} 进行 {event}")
                        return location, event
        
        print(f"❌ {npc_name} 无法确定位置")
        return "unknown_location", "空闲"
    
    def _get_location_and_event_from_schedule(self, schedule: List[Dict], current_time: str) -> Tuple[str, str]:
        """从计划表中获取当前时间的位置和活动"""
        try:
            from ..utils.time_utils import TimeUtils
            current_time_obj = TimeUtils.parse_game_time(current_time)
            
            for item in schedule:
                start_time = TimeUtils.parse_game_time(item["start_time"])
                end_time = TimeUtils.parse_game_time(item["end_time"])
                
                if start_time <= current_time_obj < end_time:
                    return item["location"], item["event"]
            
            return "unknown_location", "空闲"
        except Exception as e:
            print(f"计划表解析失败: {e}")
            return "unknown_location", "空闲"
    
    def get_npc_by_name(self, npc_name: str, story_id: int = None) -> Optional[dict]:
        """根据名称获取NPC数据"""
        if story_id:
            result = self.npc_db_service.get_npc_by_name(story_id, npc_name)
            if result.get("success"):
                return result.get("data")
        return None
    
    def get_all_npcs(self, story_id: int = None) -> List[dict]:
        """获取所有NPC数据"""
        if story_id:
            return self._get_all_npcs_for_story(story_id)
        return []
    
    def get_npc_mood(self, npc_name: str, game_state: GameStateModel) -> str:
        """获取NPC当前心情"""
        # 优先从游戏状态获取
        if hasattr(game_state, 'npc_moods') and npc_name in game_state.npc_moods:
            return game_state.npc_moods[npc_name]
        
        # 从数据库获取默认心情
        if game_state and game_state.story_id:
            npc_obj = self.get_npc_by_name(npc_name, game_state.story_id)
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
    
    def get_npc_schedule(self, npc_name: str, story_id: int = None) -> List[Dict]:
        """获取NPC的计划表"""
        if story_id:
            npc_obj = self.get_npc_by_name(npc_name, story_id)
            if npc_obj:
                return npc_obj.get("schedule", [])
        return []
    
    def get_npc_personality(self, npc_name: str, story_id: int = None) -> str:
        """获取NPC性格"""
        if story_id:
            npc_obj = self.get_npc_by_name(npc_name, story_id)
            if npc_obj:
                return npc_obj.get("personality", "")
        return ""
    
    def get_npc_background(self, npc_name: str, story_id: int = None) -> str:
        """获取NPC背景"""
        if story_id:
            npc_obj = self.get_npc_by_name(npc_name, story_id)
            if npc_obj:
                return npc_obj.get("background", "")
        return ""
    
    def get_npc_relations(self, npc_name: str, story_id: int = None) -> Dict:
        """获取NPC关系"""
        if story_id:
            npc_obj = self.get_npc_by_name(npc_name, story_id)
            if npc_obj:
                return npc_obj.get("relations", {})
        return {}
    
    def get_npc_current_schedule(self, npc_name: str, game_state: GameStateModel = None) -> List[Dict]:
        """获取NPC当前有效的计划表（优先动态计划表）"""
        # 优先使用动态计划表
        if game_state and hasattr(game_state, 'npc_dynamic_schedules'):
            dynamic_schedule = game_state.npc_dynamic_schedules.get(npc_name)
            if dynamic_schedule:
                print(f"✅ 获取 {npc_name} 的动态计划表")
                return dynamic_schedule
        
        # 使用原始计划表
        if game_state and game_state.story_id:
            original_schedule = self.get_npc_schedule(npc_name, game_state.story_id)
            if original_schedule:
                print(f"✅ 获取 {npc_name} 的原始计划表")
                return original_schedule
        
        print(f"❌ {npc_name} 没有可用的计划表")
        return []
    
    def replace_npc_complete_schedule(self, npc_name: str, new_schedule: List[Dict], game_state: GameStateModel) -> bool:
        """完全替换NPC的计划表"""
        try:
            if not hasattr(game_state, 'npc_dynamic_schedules'):
                game_state.npc_dynamic_schedules = {}
            
            # 更新内存中的动态计划表
            game_state.npc_dynamic_schedules[npc_name] = new_schedule
            print(f"✅ 更新 {npc_name} 的动态计划表到内存")
            
            # 持久化到数据库
            if game_state.story_id:
                self._persist_schedule_to_database(npc_name, new_schedule, game_state.story_id)
            
            return True
        except Exception as e:
            print(f"❌ 替换NPC计划表失败: {e}")
            return False
    
    def _persist_schedule_to_database(self, npc_name: str, new_schedule: List[Dict], story_id: int):
        """将计划表持久化到数据库"""
        try:
            # 先通过story_id和npc_name获取NPC记录
            npc_result = self.npc_db_service.get_npc_by_name(story_id, npc_name)
            if not npc_result.get("success"):
                print(f"❌ 获取NPC记录失败: {npc_result.get('error')}")
                return
            
            npc_data = npc_result.get("data", {})
            npc_id = npc_data.get("id")
            if not npc_id:
                print(f"❌ 无法获取NPC ID: {npc_name}")
                return
            
            # 调用update_npc_schedule方法
            result = self.npc_db_service.update_npc_schedule(npc_id, new_schedule)
            if result.get("success"):
                print(f"✅ {npc_name} 的计划表已持久化到数据库")
            else:
                print(f"❌ 持久化计划表失败: {result.get('error')}")
        except Exception as e:
            print(f"❌ 持久化计划表异常: {e}") 