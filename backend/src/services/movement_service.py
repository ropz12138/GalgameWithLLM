"""
移动服务 - 处理玩家移动相关逻辑
"""
import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(os.path.dirname(SRC_DIR))
sys.path.append(PROJECT_ROOT)
sys.path.append(SRC_DIR)

from .location_service import LocationService
from .llm_service import LLMService
from ..models.game_state_model import GameStateModel
from ..prompts.prompt_templates import PromptTemplates
import sys
import os
# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from data.locations import all_locations_data, location_name_map


class MovementService:
    """移动服务类"""
    
    def __init__(self):
        self.location_service = LocationService()
        self.llm_service = LLMService()
    
    async def process_movement(self, action: str, game_state: GameStateModel) -> Dict[str, Any]:
        """
        处理移动行动
        
        Args:
            action: 玩家行动
            game_state: 游戏状态
            
        Returns:
            移动处理结果
        """
        print(f"\n🚶 [MovementService] 处理移动: {action}")
        
        # 使用LLM智能识别目的地
        target_location_key = await self.llm_extract_destination(action, game_state)
        
        if not target_location_key:
            print(f"❌ 无法识别目的地")
            return {
                "success": False,
                "error": "无法理解你想去哪里，请明确指定目的地。",
                "messages": []
            }
        
        print(f"✅ 目标位置: {target_location_key}")
        
        # 检查是否已经在目标位置
        if game_state.player_location == target_location_key:
            destination_name = all_locations_data.get(target_location_key, {}).get("name", target_location_key)
            print(f"⚠️ 玩家已经在目标位置")
            return {
                "success": True,
                "messages": [
                    {"speaker": "系统", "message": f"你已经在{destination_name}了。", "type": "info", "timestamp": game_state.current_time}
                ]
            }
        
        # 寻找路径（支持多步移动）
        path = self.location_service.find_path_to_destination(game_state.player_location, target_location_key)
        
        if not path:
            destination_name = all_locations_data.get(target_location_key, {}).get("name", target_location_key)
            print(f"❌ 无法找到到达路径")
            return {
                "success": False,
                "error": f"无法到达{destination_name}，可能没有连通的路径。",
                "messages": []
            }
        
        print(f"✅ 找到路径: {path}")
        
        # 执行多步移动
        return await self.execute_multi_step_movement(path, game_state, action)
    
    async def llm_extract_destination(self, action: str, game_state: GameStateModel) -> Optional[str]:
        """使用LLM智能识别目的地"""
        try:
            llm = self.llm_service.get_llm_instance()
            
            # 构建所有可用位置信息
            available_locations = []
            for key, data in all_locations_data.items():
                available_locations.append(f"- {key}: {data['name']} - {data.get('description', '无描述')}")
            
            all_location_info = "\n".join(available_locations)
            
            # 使用现有的move_destination提示词
            system_prompt = PromptTemplates.get_move_destination_prompt(
                player_name="林凯",
                current_location=all_locations_data.get(game_state.player_location, {}).get("name", game_state.player_location),
                all_location_info=all_location_info,
                action=action
            )
            
            from langchain_core.messages import SystemMessage, HumanMessage
            from langchain_core.output_parsers import JsonOutputParser
            
            print(f"\n🤖 LLM调用 - 移动目的地识别")
            print(f"📤 输入 (System):")
            print(f"  玩家名: 林凯")
            print(f"  当前位置: {game_state.player_location}")
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
                destination_key = response.get("destination_key", "")
                destination_name = response.get("destination_name", "")
                reason = response.get("reason", "无理由")
                
                print(f"  🎯 识别结果:")
                print(f"    目标key: {destination_key}")
                print(f"    目标名称: {destination_name}")
                print(f"    识别理由: {reason}")
                
                # 验证destination_key是否有效
                if destination_key and destination_key in all_locations_data:
                    return destination_key
                else:
                    print(f"    ❌ 无效的destination_key: {destination_key}")
                    return None
            
        except Exception as e:
            print(f"  ❌ LLM目的地识别失败: {e}")
        
        return None
    
    async def execute_multi_step_movement(self, path: List[str], game_state: GameStateModel, original_action: str) -> Dict[str, Any]:
        """执行多步移动"""
        print(f"\n🚶‍♂️ 执行多步移动，共{len(path)}步")
        
        all_messages = []
        total_time_cost = 0
        current_location = game_state.player_location
        current_time = game_state.current_time
        
        for i, next_location in enumerate(path):
            step_num = i + 1
            location_name = all_locations_data.get(next_location, {}).get("name", next_location)
            
            print(f"  步骤{step_num}: {current_location} → {next_location} ({location_name})")
            
            # 计算单步移动时间
            step_time = self.calculate_single_step_time(current_location, next_location, game_state.player_personality)
            current_time = self.advance_game_time(current_time, step_time)
            total_time_cost += step_time
            
            # 生成移动描述
            if len(path) == 1:
                # 单步移动
                move_description = self.generate_single_move_description(current_location, next_location)
                all_messages.append({
                    "speaker": "系统",
                    "message": move_description,
                    "type": "movement",
                    "timestamp": current_time
                })
            else:
                # 多步移动
                if step_num == 1:
                    # 第一步：开始移动
                    move_description = f"你开始前往目标地点..."
                    all_messages.append({
                        "speaker": "系统",
                        "message": move_description,
                        "type": "movement",
                        "timestamp": current_time
                    })
                
                step_description = self.generate_step_description(current_location, next_location, step_num, len(path))
                all_messages.append({
                    "speaker": "系统",
                    "message": step_description,
                    "type": "movement",
                    "timestamp": current_time
                })
            
            # 更新当前位置
            current_location = next_location
        
        # 到达最终目的地，生成五感反馈
        final_location_data = all_locations_data.get(current_location, {})
        arrival_feedback = await self.location_service.generate_sensory_feedback(
            f"到达{final_location_data.get('name', current_location)}",
            final_location_data,
            [],  # 到达时暂时不考虑NPC，会在后续更新
            current_time,
            game_state.player_personality
        )
        
        all_messages.append({
            "speaker": "系统",
            "message": arrival_feedback,
            "type": "sensory",
            "timestamp": current_time
        })
        
        print(f"  ✅ 移动完成，总耗时: {total_time_cost}分钟")
        
        return {
            "success": True,
            "player_location": current_location,
            "current_time": current_time,
            "messages": all_messages,
            "time_cost": total_time_cost
        }
    
    def calculate_single_step_time(self, from_location: str, to_location: str, personality: str) -> int:
        """计算单步移动时间"""
        base_time = 3  # 基础3分钟
        
        # 根据性格调整
        personality_factor = 1.0
        if "急躁" in personality or "急性子" in personality:
            personality_factor = 0.8
        elif "慢性子" in personality or "悠闲" in personality:
            personality_factor = 1.2
        
        total_time = int(base_time * personality_factor)
        return max(1, total_time)  # 至少1分钟
    
    def generate_single_move_description(self, from_location: str, to_location: str) -> str:
        """生成单步移动描述"""
        from_name = all_locations_data.get(from_location, {}).get("name", from_location)
        to_name = all_locations_data.get(to_location, {}).get("name", to_location)
        return f"你从{from_name}来到了{to_name}。"
    
    def generate_step_description(self, from_location: str, to_location: str, step_num: int, total_steps: int) -> str:
        """生成多步移动中的单步描述"""
        from_name = all_locations_data.get(from_location, {}).get("name", from_location)
        to_name = all_locations_data.get(to_location, {}).get("name", to_location)
        
        if step_num == total_steps:
            return f"你经过{from_name}，最终到达了{to_name}。"
        else:
            return f"你经过了{from_name}，继续向目标前进..."
    

    
    def advance_game_time(self, current_time: str, minutes: int) -> str:
        """推进游戏时间"""
        try:
            from ..utils.time_utils import TimeUtils
            return TimeUtils.add_minutes(current_time, minutes)
        except Exception as e:
            print(f"时间推进失败: {e}")
            return current_time
    
    def get_available_destinations(self, current_location: str) -> List[Dict[str, str]]:
        """获取当前位置可到达的目的地"""
        connections = self.location_service.get_location_connections(current_location)
        destinations = []
        
        for loc_key in connections:
            loc_data = all_locations_data.get(loc_key, {})
            destinations.append({
                "key": loc_key,
                "name": loc_data.get("name", loc_key),
                "description": loc_data.get("description", "")
            })
        
        return destinations 