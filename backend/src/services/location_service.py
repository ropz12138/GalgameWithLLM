"""
位置服务 - 处理位置相关逻辑
"""
import sys
import os
from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from datetime import datetime

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(os.path.dirname(SRC_DIR))
sys.path.append(PROJECT_ROOT)
sys.path.append(SRC_DIR)

from .llm_service import LLMService
from .npc_service import NPCService
from ..prompts.prompt_templates import PromptTemplates
from ..models.game_state_model import GameStateModel
import sys
import os
# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from data.locations import all_locations_data, location_connections
from data.characters import all_actresses
from ..services.location_db_service import LocationDBService


class LocationService:
    """位置服务类"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.npc_service = NPCService()
        self.location_db_service = LocationDBService()
    
    def get_npcs_at_location(self, location_name: str, npc_locations: Dict[str, str], current_time: str, game_state=None) -> List[Dict]:
        """获取指定位置的NPC列表"""
        print(f"\n📍 [LocationService] 获取位置 {location_name} 的NPC")
        print(f"  📊 输入参数:")
        print(f"    - location_name: {location_name}")
        print(f"    - npc_locations: {npc_locations}")
        print(f"    - current_time: {current_time}")
        
        npcs_at_location = []
        
        if not game_state or not game_state.story_id:
            print("❌ 无法获取故事ID")
            return npcs_at_location
        
        # 从数据库获取当前故事的所有NPC
        all_npcs = self.npc_service.get_all_npcs(game_state.story_id)
        
        for npc_name, npc_location in npc_locations.items():
            print(f"  🔍 检查NPC {npc_name}: 位置 {npc_location}")
            
            if npc_location == location_name:
                print(f"    ✅ {npc_name} 在目标位置")
                
                # 获取NPC详细信息
                npc_obj = next((npc for npc in all_npcs if npc.get('name') == npc_name), None)
                if npc_obj:
                    # 获取当前活动
                    _, npc_event = self.npc_service.get_npc_current_location_and_event(npc_name, current_time, game_state)
                    
                    npc_info = {
                        "name": npc_name,
                        "personality": npc_obj.get("personality", "友善"),
                        "event": npc_event,
                        "activity": npc_event,  # 兼容字段
                        "mood": npc_obj.get("mood", "平静")
                    }
                    npcs_at_location.append(npc_info)
                    print(f"      📝 添加NPC信息: {npc_info}")
                else:
                    print(f"      ❌ 未找到NPC数据")
            else:
                print(f"    ❌ {npc_name} 不在目标位置 (在 {npc_location})")
        
        print(f"  📤 结果: 找到 {len(npcs_at_location)} 个NPC")
        return npcs_at_location
    
    def get_location_details(self, location_name: str, npc_locations: Dict[str, str], current_time: str, game_state=None) -> Dict[str, Any]:
        """获取位置详情"""
        print(f"\n🔍 [LocationService] 获取位置详情 - 位置: {location_name}")
        
        try:
            if not game_state or not game_state.story_id:
                print("❌ 无法获取故事ID")
                return {
                    "description": "",
                    "connections": [],
                    "npcs_present": []
                }
            
            # 从数据库获取位置数据
            location_result = self.location_db_service.get_location_by_key(game_state.story_id, location_name)
            if not location_result.get("success"):
                print(f"❌ 获取位置数据失败: {location_result.get('error')}")
                location_data = {}
                connections = []
            else:
                location_data = location_result.get("data", {})
                connections = location_data.get("connections", [])
            
            print(f"🔍 位置数据:")
            print(f"  - location_data: {location_data}")
            print(f"  - connections: {connections}")
            
            # 获取当前地点的NPC
            npcs_present = self.get_npcs_at_location(location_name, npc_locations, current_time, game_state)
            
            result = {
                "description": location_data.get("description", ""),
                "connections": connections,
                "npcs_present": npcs_present
            }
            
            print(f"\n🔍 位置详情计算结果:")
            print(f"  - 当前地点的NPC: {[npc['name'] for npc in npcs_present]}")
            print(f"  - 完整结果: {result}")
            
            return result
            
        except Exception as e:
            print(f"❌ 获取位置详情失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "description": "",
                "connections": [],
                "npcs_present": []
            }
    
    async def extract_destination_from_action(self, action: str) -> Optional[str]:
        """从行动文本中提取目的地"""
        # 首先尝试简单的字符串匹配
        keywords = ["去", "到", "前往", "移动到", "走到", "回"]
        
        for keyword in keywords:
            if keyword in action:
                parts = action.split(keyword)
                if len(parts) > 1:
                    destination = parts[1].strip()
                    # 清理标点符号
                    destination = destination.replace("。", "").replace("，", "").replace("、", "")
                    
                    # 处理特殊表达
                    if "我的房间" in destination or "自己的房间" in destination:
                        return "林凯房间"  # 玩家是林凯
                    
                    return destination
        
        # 如果没有关键词，检查是否直接是地点名
        for location_key, location_data in all_locations_data.items():
            if location_data["name"] in action or location_key in action:
                return location_data["name"]
        
        # 如果简单匹配失败，使用LLM智能解析
        try:
            llm = self.llm_service.get_llm_instance()
            
            # 构建可用位置列表
            available_locations = []
            for key, data in all_locations_data.items():
                available_locations.append(f"{data['name']} ({key})")
            
            locations_list = ", ".join(available_locations)
            
            # 使用prompt_manager获取目的地解析提示词
            system_prompt = PromptTemplates.get_move_destination_prompt(
                player_name="林凯",
                current_location="当前位置",  # 这里可以传入实际位置
                all_location_info=locations_list,
                action=action
            )
            
            from langchain_core.messages import SystemMessage, HumanMessage
            from langchain_core.output_parsers import JsonOutputParser
            
            print(f"\n🤖 LLM调用 - 目的地解析")
            print(f"📤 输入 (System):")
            print(f"  玩家名: 林凯")
            print(f"  可用位置数量: {len(available_locations)}个")
            print(f"📤 输入 (Human): 玩家行动：{action}")
            
            # 使用JsonOutputParser来解析LLM响应
            parser = JsonOutputParser()
            response = parser.invoke(await llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"玩家行动：{action}")
            ]))
            
            print(f"📥 LLM输出: {response}")
            
            # 解析JSON响应
            if isinstance(response, dict):
                destination_name = response.get("destination_name", "")
                destination_key = response.get("destination_key", "")
                
                # 优先使用destination_name
                if destination_name:
                    return destination_name
                elif destination_key:
                    # 如果只有key，转换为name
                    location_data = all_locations_data.get(destination_key, {})
                    return location_data.get("name", destination_key)
                
        except Exception as e:
            print(f"  ❌ LLM目的地解析失败: {e}")
        
        return None
    
    def find_path_to_destination(self, start_location: str, target_location: str) -> List[str]:
        """寻找到目的地的路径"""
        print(f"\n🗺️ [LocationService] 寻找路径: {start_location} -> {target_location}")
        
        # 构建完整的连接图
        all_connections = location_connections.copy()
        
        # 检查是否可以直接到达
        if target_location in all_connections.get(start_location, []):
            print(f"  ✅ 可直接到达")
            return [target_location]
        
        # BFS搜索路径
        from collections import deque
        
        queue = deque([(start_location, [start_location])])  # (当前位置, 路径)
        visited = {start_location}
        
        while queue:
            current_location, path = queue.popleft()
            
            # 检查所有连接的地点
            for next_location in all_connections.get(current_location, []):
                if next_location == target_location:
                    # 找到目标地点
                    final_path = path + [target_location]
                    route = final_path[1:]  # 去掉起点
                    print(f"  ✅ 找到路径: {' -> '.join(final_path)}")
                    print(f"  📍 移动步骤: {route}")
                    return route
                
                if next_location not in visited:
                    visited.add(next_location)
                    queue.append((next_location, path + [next_location]))
        
        # 无法到达
        print(f"  ❌ 无法找到到达路径")
        return []
    
    async def generate_sensory_feedback(self, action: str, location_info: dict, current_npcs: list, current_time: str, personality: str) -> str:
        """生成五感反馈"""
        llm = self.llm_service.get_llm_instance()
        
        npc_info = ""
        if current_npcs:
            npc_descriptions = [f"{npc['name']}正在{npc['event']}" for npc in current_npcs]
            npc_info = f"这里有：{', '.join(npc_descriptions)}"
        
        # 使用prompt_manager获取五感反馈提示词
        system_prompt = PromptTemplates.get_sensory_feedback_prompt(
            location_name=location_info.get('name', '某个地点'),
            location_description=location_info.get('description', '一个普通的地方'),
            current_time=current_time,
            npc_info=npc_info if npc_info else '无',
            action=action
        )
        
        user_input = f"玩家行动：{action}"
        
        print(f"  📤 LLM输入 (System):")
        print(f"    地点: {location_info.get('name', '某个地点')}")
        print(f"    描述: {location_info.get('description', '一个普通的地方')[:50]}...")
        print(f"    NPC: {npc_info if npc_info else '无'}")
        print(f"  📤 LLM输入 (Human): {user_input}")
        
        try:
            # 使用JsonOutputParser来解析LLM响应
            parser = JsonOutputParser()
            response = parser.invoke(await llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]))
            
            print(f"  📥 LLM原始输出: {response}")
            
            # 返回JSON格式，前端会自动解析并应用特殊的五感反馈UI
            if isinstance(response, dict):
                import json
                json_output = json.dumps(response, ensure_ascii=False)
                print(f"  📥 格式化输出: {json_output}")
                return json_output
            else:
                return str(response)
                
        except Exception as e:
            print(f"  ❌ LLM调用失败: {e}")
            # 降级处理
            fallback_response = f"你在{location_info.get('name', '这里')}进行了行动：{action}"
            print(f"  📥 降级输出: {fallback_response}")
            return fallback_response
    
    def get_all_locations(self) -> Dict[str, Dict]:
        """获取所有位置数据"""
        return all_locations_data.copy()
    
    def get_location_connections(self, location_name: str) -> List[str]:
        """获取位置的连接"""
        return location_connections.get(location_name, [])
    
    def is_valid_location(self, location_name: str) -> bool:
        """检查是否为有效位置"""
        return location_name in all_locations_data 