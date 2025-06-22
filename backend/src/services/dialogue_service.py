"""
对话服务 - 处理NPC对话生成和计划表更新
"""
import re
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from langchain_core.output_parsers import JsonOutputParser

from ..models.game_state_model import GameStateModel
from ..prompts.prompt_templates import PromptTemplates
from ..utils.llm_client import LLMClient

logger = logging.getLogger(__name__)


class DialogueService:
    """对话服务类"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompt_templates = PromptTemplates()
        self.json_parser = JsonOutputParser()
    
    async def process_dialogue(self, action: str, game_state: GameStateModel) -> Dict[str, Any]:
        """
        处理对话行动的主入口方法
        
        Args:
            action: 玩家的对话行动
            game_state: 游戏状态
            
        Returns:
            处理结果
        """
        try:
            print(f"\n💬 [DialogueService] 处理对话行动: {action}")
            
            # 解析对话行动
            dialogue_info = self.parse_dialogue_action(action)
            if not dialogue_info:
                return {
                    "success": False,
                    "error": "无法理解的对话格式，请使用类似'和某人说话：内容'的格式",
                    "messages": []
                }
            
            npc_name = dialogue_info["npc"]
            player_message = dialogue_info["message"]
            
            print(f"  👤 对话对象: {npc_name}")
            print(f"  💭 玩家消息: {player_message}")
            
            # 检查NPC是否在当前位置
            current_npcs = self._get_npcs_at_current_location(game_state)
            if npc_name not in current_npcs:
                return {
                    "success": False,
                    "error": f"{npc_name}不在这里，无法与其对话",
                    "messages": []
                }
            
            # 生成NPC对话响应
            npc_response = await self.generate_npc_dialogue(npc_name, player_message, game_state)
            
            # 尝试更新NPC计划表
            schedule_updated = await self.analyze_and_update_schedule(
                npc_name, player_message, npc_response, game_state
            )
            
            # 计算对话耗时
            time_cost = self._calculate_dialogue_time(player_message, npc_response)
            new_time = self._advance_game_time(game_state.current_time, time_cost)
            
            messages = [
                {"speaker": npc_name, "message": npc_response, "type": "dialogue", "timestamp": new_time}
            ]
            
            if schedule_updated:
                messages.append({
                    "speaker": "系统", 
                    "message": f"{npc_name}的计划发生了变化。", 
                    "type": "system", 
                    "timestamp": new_time
                })
            
            return {
                "success": True,
                "current_time": new_time,
                "messages": messages,
                "time_cost": time_cost,
                "npc_name": npc_name,
                "schedule_updated": schedule_updated
            }
            
        except Exception as e:
            logger.error(f"❌ 对话处理失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"对话处理失败：{str(e)}",
                "messages": []
            }
    
    def _get_npcs_at_current_location(self, game_state: GameStateModel) -> List[str]:
        """获取当前位置的NPC列表"""
        try:
            from .location_service import LocationService
            location_service = LocationService()
            npc_objects = location_service.get_npcs_at_location(
                game_state.player_location,
                game_state.npc_locations,
                game_state.current_time,
                game_state
            )
            # 提取NPC名称
            return [npc['name'] for npc in npc_objects]
        except Exception as e:
            logger.error(f"获取当前位置NPC失败: {e}")
            return []
    
    def _calculate_dialogue_time(self, player_message: str, npc_response: str) -> int:
        """计算对话耗时（分钟）"""
        # 基础对话时间：2-5分钟
        base_time = 2
        
        # 根据消息长度调整
        total_length = len(player_message) + len(npc_response)
        if total_length > 100:
            base_time += 2
        elif total_length > 50:
            base_time += 1
        
        return base_time
    
    def _advance_game_time(self, current_time: str, minutes: int) -> str:
        """推进游戏时间"""
        try:
            from ..utils.time_utils import TimeUtils
            return TimeUtils.add_minutes(current_time, minutes)
        except Exception as e:
            logger.error(f"时间推进失败: {e}")
            return current_time
    
    def parse_dialogue_action(self, action: str) -> Optional[Dict[str, str]]:
        """
        解析对话行动
        
        Args:
            action: 用户输入的行动
            
        Returns:
            解析结果字典，包含npc和message字段，如果不是对话行动则返回None
        """
        try:
            # 支持多种对话格式
            patterns = [
                r"和(.+?)说话?[:：](.+)",  # "和林若曦说话：一会来我房间陪我打会游戏呗"
                r"对(.+?)说[:：](.+)",    # "对林若曦说：你好"
                r"跟(.+?)说[:：](.+)",    # "跟林若曦说：你好"
                r"告诉(.+?)[:：](.+)",    # "告诉林若曦：你好"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, action)
                if match:
                    npc_name = match.group(1).strip()
                    message = match.group(2).strip()
                    
                    logger.info(f"✅ 对话解析成功 - NPC: {npc_name}, 消息: {message}")
                    return {
                        "npc": npc_name,
                        "message": message
                    }
            
            logger.debug(f"❌ 对话解析失败 - 输入: {action}")
            return None
            
        except Exception as e:
            logger.error(f"对话解析异常: {e}")
            return None
    
    async def generate_npc_dialogue(self, npc_name: str, player_message: str, 
                                  game_state: GameStateModel) -> str:
        """
        生成NPC对话响应
        
        Args:
            npc_name: NPC名称
            player_message: 玩家消息
            game_state: 游戏状态
            
        Returns:
            NPC的对话响应
        """
        try:
            # 获取NPC信息
            from data.characters import all_actresses
            npc_info = next((a for a in all_actresses if a['name'] == npc_name), None)
            
            if not npc_info:
                return f"抱歉，我不知道{npc_name}是谁。"
            
            # 获取NPC当前状态和事件
            from .npc_service import NPCService
            npc_service = NPCService()
            current_location, current_event = npc_service.get_npc_current_location_and_event(
                npc_name, game_state.current_time, game_state
            )
            
            # 获取对话历史
            dialogue_history = game_state.npc_dialogue_histories.get(npc_name, [])
            recent_history = dialogue_history[-5:] if dialogue_history else []
            
            # 构建提示词
            prompt = self.prompt_templates.get_npc_dialogue_prompt(
                npc_name=npc_name,
                personality=npc_info.get("personality", "友好"),
                background=npc_info.get("background", ""),
                relations=str(npc_info.get("relations", {})),
                mood=npc_info.get("mood", "平静"),
                npc_location=current_location,
                npc_event=current_event,
                player_name="林凯",  # 玩家名称
                current_time=game_state.current_time,
                location_details=current_location,
                location_description="",  # 可以后续补充
                other_npcs_info="",  # 可以后续补充
                player_personality=game_state.player_personality,
                history_str=str(recent_history),
                dialogue_summary="",  # 可以后续补充
                message=player_message
            )
            
            logger.info(f"🤖 [DialogueService] 调用LLM生成NPC对话")
            logger.info(f"📝 输入提示词:\n{prompt}")
            
            # 调用LLM生成对话
            response = await self.llm_client.chat_completion(prompt)
            
            logger.info(f"🤖 LLM原始响应:\n{response}")
            
            # 更新对话历史
            if npc_name not in game_state.npc_dialogue_histories:
                game_state.npc_dialogue_histories[npc_name] = []
            
            game_state.npc_dialogue_histories[npc_name].extend([
                {"speaker": "玩家", "message": player_message},
                {"speaker": npc_name, "message": response}
            ])
            
            # 保持对话历史不超过20条
            if len(game_state.npc_dialogue_histories[npc_name]) > 20:
                game_state.npc_dialogue_histories[npc_name] = \
                    game_state.npc_dialogue_histories[npc_name][-20:]
            
            logger.info(f"✅ NPC对话生成成功: {npc_name} -> {response[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"❌ NPC对话生成失败: {e}")
            import traceback
            traceback.print_exc()
            return f"抱歉，{npc_name}现在无法回应。"
    
    async def analyze_and_update_schedule(self, npc_name: str, player_message: str, 
                                        npc_response: str, game_state: GameStateModel) -> bool:
        """
        分析对话内容并更新NPC计划表
        
        Args:
            npc_name: NPC名称
            player_message: 玩家消息
            npc_response: NPC响应
            game_state: 游戏状态
            
        Returns:
            是否更新了计划表
        """
        try:
            # 获取NPC当前计划表
            from .npc_service import NPCService
            npc_service = NPCService()
            current_schedule = npc_service.get_npc_schedule(npc_name)
            
            if not current_schedule:
                logger.warning(f"未找到{npc_name}的计划表")
                return False
            
            # 获取所有可用位置
            from data.locations import all_locations_data
            available_locations = list(all_locations_data.keys())
            
            # 构建分析提示词
            prompt = self.prompt_templates.get_schedule_update_prompt(
                available_locations=", ".join(available_locations),
                npc_name=npc_name,
                player_message=player_message,
                npc_reply=npc_response,
                current_time=game_state.current_time,
                current_schedule=str(current_schedule)
            )
            
            logger.info(f"🤖 [DialogueService] 调用LLM分析计划表更新")
            logger.info(f"📝 输入提示词:\n{prompt}")
            
            # 调用LLM分析
            response = await self.llm_client.chat_completion(prompt)
            
            logger.info(f"🤖 LLM原始响应:\n{response}")
            
            # 使用JsonOutputParser解析响应
            try:
                # 先尝试直接解析
                try:
                    analysis = json.loads(response)
                except json.JSONDecodeError:
                    # 如果直接解析失败，使用JsonOutputParser处理包含代码块的响应
                    analysis = self.json_parser.parse(response)
                
                if analysis.get("needs_schedule_update", False):
                    new_schedule = analysis.get("new_complete_schedule", [])
                    
                    if new_schedule and isinstance(new_schedule, list):
                        # 更新完整计划表
                        npc_service.replace_npc_complete_schedule(npc_name, new_schedule, game_state)
                        
                        logger.info(f"✅ 已更新{npc_name}的完整计划表")
                        logger.info(f"📋 新计划表: {new_schedule}")
                        return True
                    else:
                        logger.warning("LLM返回的新计划表格式不正确")
                        return False
                else:
                    logger.info("LLM判断不需要更新计划表")
                    return False
                    
            except Exception as parse_error:
                logger.error(f"解析LLM响应失败: {parse_error}")
                logger.error(f"原始响应: {response}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 计划表更新分析失败: {e}")
            import traceback
            traceback.print_exc()
            return False 