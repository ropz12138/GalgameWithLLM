"""
游戏服务 - 处理游戏核心业务逻辑
"""
import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(os.path.dirname(SRC_DIR))
sys.path.append(PROJECT_ROOT)
sys.path.append(SRC_DIR)

from ..models.game_state_model import GameStateModel
from ..models.player_model import PlayerModel
from ..models.npc_model import NPCModel
from ..models.message_model import MessageModel
from .state_service import StateService
from .action_router_service import ActionRouterService
from .dialogue_service import DialogueService
from .movement_service import MovementService
from .location_service import LocationService
from .npc_service import NPCService
from .llm_service import LLMService
from ..prompts.prompt_templates import PromptTemplates
from .message_service import message_service


class GameService:
    """游戏服务类"""
    
    def __init__(self):
        """初始化游戏服务"""
        self.state_service = StateService()
        self.action_router_service = ActionRouterService()
        self.dialogue_service = DialogueService()
        self.movement_service = MovementService()
        self.location_service = LocationService()
        self.npc_service = NPCService()
        self.llm_service = LLMService()
        self.message_service = message_service
    
    async def process_action(self, action: str, session_id: str = "default", story_id: int = None) -> Dict[str, Any]:
        """
        处理玩家行动
        
        Args:
            action: 玩家行动描述
            session_id: 会话ID
            story_id: 故事ID
            
        Returns:
            处理结果
        """
        try:
            print(f"\n🔍 [GameService] 开始处理行动:")
            print(f"  📝 行动内容: '{action}'")
            print(f"  🆔 会话ID: {session_id}")
            
            # 获取用户和故事信息
            user_id, story_id = self._get_user_and_story_info(session_id, story_id)
            
            # 获取当前游戏状态（现在支持从数据库恢复）
            game_state = await self.state_service.get_game_state(session_id, user_id, story_id)
            print(f"  📊 当前状态:")
            print(f"    📍 位置: {game_state.player_location}")
            print(f"    ⏰ 时间: {game_state.current_time}")
            print(f"    💬 消息数量: {len(game_state.messages)}")
            
            # 首先记录玩家的输入消息到内存
            game_state.add_message("玩家", action, "player_action")
            print(f"  📝 已记录玩家输入到内存: {action}")
            
            # 持久化用户输入到数据库
            try:
                game_time = datetime.fromisoformat(game_state.current_time.replace('Z', '+00:00')) if isinstance(game_state.current_time, str) else game_state.current_time
                
                await self.message_service.save_user_input(
                    user_id=user_id,
                    story_id=story_id,
                    session_id=session_id,
                    content=action,
                    location=game_state.player_location,
                    game_time=game_time
                )
            except Exception as e:
                print(f"⚠️ [GameService] 用户输入持久化失败: {e}")
                # 持久化失败不影响游戏流程
            
            # 使用行动路由服务分析行动
            route_result = await self.action_router_service.route_action(action, game_state)
            action_type = route_result["action_type"]
            
            print(f"  🎯 行动类型: {action_type}")
            print(f"  📊 置信度: {route_result['confidence']}")
            print(f"  💭 判断理由: {route_result['reason']}")
            
            # 根据行动类型分发处理
            if action_type == "talk":
                result = await self.dialogue_service.process_dialogue(action, game_state)
            elif action_type == "move":
                result = await self.movement_service.process_movement(action, game_state)
            elif action_type == "explore":
                result = await self._process_exploration(action, game_state)
            elif action_type == "compound":
                result = await self._process_compound_action(action, route_result, game_state)
            else:  # general
                result = await self._process_general_action(action, game_state)
            
            print(f"  📤 处理结果: {result}")
            
            if result["success"]:
                # 持久化处理结果
                await self._save_action_result(action_type, result, game_state, session_id, user_id, story_id)
                
                # 更新游戏状态
                await self._update_game_state(result, game_state, session_id)
                
                # 返回格式化响应，只包含新消息
                updated_game_state = await self.state_service.get_game_state(session_id, user_id, story_id)
                new_messages = result.get("messages", [])
                return self._format_game_response(updated_game_state, new_messages=new_messages)
            else:
                # 处理失败，保存错误消息
                try:
                    game_time = datetime.fromisoformat(game_state.current_time.replace('Z', '+00:00')) if isinstance(game_state.current_time, str) else game_state.current_time
                    
                    await self.message_service.save_error_message(
                        user_id=user_id,
                        story_id=story_id,
                        session_id=session_id,
                        error=result.get("error", "未知错误"),
                        location=game_state.player_location,
                        game_time=game_time
                    )
                except Exception as e:
                    print(f"⚠️ [GameService] 错误消息持久化失败: {e}")
                
                # 返回错误信息
                return self._format_game_response(game_state, error=result.get("error"))
                
        except Exception as e:
            print(f"❌ [GameService] 处理行动错误: {e}")
            import traceback
            traceback.print_exc()
            
            # 尝试获取用户信息，如果失败则使用默认值
            try:
                user_id, story_id = self._get_user_and_story_info(session_id, story_id)
                game_state = await self.state_service.get_game_state(session_id, user_id, story_id)
            except:
                game_state = await self.state_service.get_game_state(session_id)
                
            return self._format_game_response(game_state, error=str(e))
    
    async def _process_exploration(self, action: str, game_state: GameStateModel) -> Dict[str, Any]:
        """处理探索行动"""
        print(f"\n🔍 [GameService] 处理探索行动: {action}")
        
        try:
            # 获取当前位置信息
            current_npcs = self.location_service.get_npcs_at_location(
                game_state.player_location,
                game_state.npc_locations,
                game_state.current_time
            )
            
            # 生成探索反馈
            sensory_feedback = await self.location_service.generate_sensory_feedback(
                action,
                {"name": game_state.player_location, "description": ""},
                current_npcs,
                game_state.current_time,
                game_state.player_personality
            )
            
            # 计算探索耗时
            time_cost = await self._calculate_exploration_time(action, game_state.player_personality)
            new_time = self._advance_game_time(game_state.current_time, time_cost)
            
            return {
                "success": True,
                "current_time": new_time,
                "messages": [
                    {"speaker": "系统", "message": sensory_feedback, "type": "exploration", "timestamp": new_time}
                ],
                "time_cost": time_cost
            }
            
        except Exception as e:
            print(f"❌ 探索处理失败: {e}")
            return {
                "success": False,
                "error": f"探索失败：{str(e)}",
                "messages": []
            }
    
    async def _process_general_action(self, action: str, game_state: GameStateModel) -> Dict[str, Any]:
        """处理一般行动"""
        print(f"\n⚙️ [GameService] 处理一般行动: {action}")
        
        try:
            # 使用LLM生成响应
            llm = self.llm_service.get_llm_instance()
            
            from langchain_core.messages import SystemMessage, HumanMessage
            
            # 使用prompt_manager获取通用响应提示词
            system_prompt = PromptTemplates.get_general_response_prompt(
                player_location=game_state.player_location,
                current_time=game_state.current_time,
                player_personality=game_state.player_personality,
                action=action
            )
            
            print(f"\n🤖 LLM调用 - 通用响应生成")
            print(f"📤 输入 (System):")
            print(f"  玩家位置: {game_state.player_location}")
            print(f"  当前时间: {game_state.current_time}")
            print(f"  玩家性格: {game_state.player_personality}")
            print(f"📤 输入 (Human): 玩家行动：{action}")
            
            response = await llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"玩家行动：{action}")
            ])
            
            print(f"📥 LLM输出: {response.content}")
            
            # 计算行动耗时
            time_cost = self._calculate_general_action_time(action, game_state.player_personality)
            new_time = self._advance_game_time(game_state.current_time, time_cost)
            
            return {
                "success": True,
                "current_time": new_time,
                "messages": [
                    {"speaker": "系统", "message": response.content, "type": "general", "timestamp": new_time}
                ],
                "time_cost": time_cost
            }
            
        except Exception as e:
            print(f"❌ 一般行动处理失败: {e}")
            return {
                "success": False,
                "error": f"行动处理失败：{str(e)}",
                "messages": []
            }
    
    async def _process_compound_action(self, action: str, route_result: Dict, game_state: GameStateModel) -> Dict[str, Any]:
        """处理复合行动"""
        print(f"\n🔀 [GameService] 处理复合行动: {action}")
        
        sub_actions = route_result.get("sub_actions", [])
        if not sub_actions:
            return await self._process_general_action(action, game_state)
        
        all_messages = []
        total_time_cost = 0
        current_state = game_state
        
        try:
            for i, sub_action in enumerate(sub_actions):
                print(f"  🔄 处理子行动 {i+1}/{len(sub_actions)}: {sub_action}")
                
                # 获取子行动的类型和内容
                if hasattr(sub_action, 'type') and hasattr(sub_action, 'action'):
                    sub_type = sub_action.type
                    sub_action_text = sub_action.action
                else:
                    sub_type = sub_action.get('type', 'general')
                    sub_action_text = sub_action.get('action', '')
                
                # 根据子行动类型处理
                if sub_type == "talk":
                    sub_result = await self.dialogue_service.process_dialogue(sub_action_text, current_state)
                elif sub_type == "move":
                    sub_result = await self.movement_service.process_movement(sub_action_text, current_state)
                elif sub_type == "explore":
                    sub_result = await self._process_exploration(sub_action_text, current_state)
                else:
                    sub_result = await self._process_general_action(sub_action_text, current_state)
                
                if sub_result["success"]:
                    # 累积消息和时间
                    all_messages.extend(sub_result.get("messages", []))
                    total_time_cost += sub_result.get("time_cost", 0)
                    
                    # 更新当前状态（为下一个子行动准备）
                    if "current_time" in sub_result:
                        current_state.current_time = sub_result["current_time"]
                    if "player_location" in sub_result:
                        current_state.player_location = sub_result["player_location"]
                    if "npc_dialogue_histories" in sub_result:
                        for npc_name, history in sub_result["npc_dialogue_histories"].items():
                            current_state.npc_dialogue_histories[npc_name] = history
                else:
                    # 子行动失败，中断处理
                    all_messages.append({
                        "speaker": "系统",
                        "message": f"行动中断：{sub_result.get('error', '未知错误')}",
                        "type": "error",
                        "timestamp": current_state.current_time
                    })
                    break
            
            return {
                "success": True,
                "current_time": current_state.current_time,
                "player_location": current_state.player_location,
                "messages": all_messages,
                "npc_dialogue_histories": current_state.npc_dialogue_histories,
                "time_cost": total_time_cost
            }
            
        except Exception as e:
            print(f"❌ 复合行动处理失败: {e}")
            return {
                "success": False,
                "error": f"复合行动处理失败：{str(e)}",
                "messages": all_messages
            }
    
    async def _update_game_state(self, result: Dict[str, Any], game_state: GameStateModel, session_id: str):
        """更新游戏状态"""
        print(f"\n📊 [GameService] 更新游戏状态")
        
        # 更新时间
        if "current_time" in result:
            game_state.current_time = result["current_time"]
            print(f"  ⏰ 更新时间: {game_state.current_time}")
        
        # 更新位置
        if "player_location" in result:
            game_state.player_location = result["player_location"]
            print(f"  📍 更新位置: {game_state.player_location}")
        
        # 更新NPC位置（基于新时间）
        game_state.npc_locations = self.npc_service.update_npc_locations_by_time(
            game_state.current_time, game_state
        )
        
        # 更新对话历史
        if "npc_dialogue_histories" in result:
            for npc_name, history in result["npc_dialogue_histories"].items():
                game_state.npc_dialogue_histories[npc_name] = history
                print(f"  💬 更新 {npc_name} 对话历史: {len(history)} 条")
        
        # 添加消息到游戏状态
        if "messages" in result:
            game_state.messages.extend(result["messages"])
            print(f"  💬 添加消息: {len(result['messages'])} 条")
        
        # 保存状态
        self.state_service.save_game_state(session_id, game_state, story_id)
        print(f"  💾 状态已保存")
    
    async def _calculate_exploration_time(self, action: str, personality: str) -> int:
        """计算探索耗时"""
        try:
            # 使用LLM智能估算时间
            llm = self.llm_service.get_llm_instance()
            
            # 使用prompt_manager获取时间估算提示词
            from ..prompts.prompt_templates import PromptTemplates
            system_prompt = PromptTemplates.get_time_estimation_prompt(
                action=action,
                personality=personality
            )
            
            from langchain_core.messages import SystemMessage, HumanMessage
            from langchain_core.output_parsers import JsonOutputParser
            
            print(f"\n🤖 LLM调用 - 时间估算")
            print(f"📤 输入 (System):")
            print(f"  行动内容: {action}")
            print(f"  玩家性格: {personality}")
            print(f"📤 输入 (Human): 请估算行动耗时：{action}")
            
            # 使用JsonOutputParser来解析LLM响应
            parser = JsonOutputParser()
            response = parser.invoke(await llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"请估算行动耗时：{action}")
            ]))
            
            print(f"📥 LLM输出: {response}")
            
            # 解析JSON响应
            if isinstance(response, dict):
                estimated_minutes = response.get("estimated_minutes", 3)
                reason = response.get("reason", "默认估算")
                print(f"  ⏰ 估算结果: {estimated_minutes}分钟，理由: {reason}")
                return max(1, int(estimated_minutes))
                
        except Exception as e:
            print(f"  ❌ LLM时间估算失败: {e}")
        
        # 降级到简单估算
        base_time = 3  # 基础3分钟
        
        # 根据行动内容调整
        if "仔细" in action or "详细" in action:
            base_time += 2
        elif "快速" in action or "简单" in action:
            base_time -= 1
        
        # 根据性格调整
        if "细致" in personality:
            base_time += 1
        elif "急躁" in personality:
            base_time -= 1
        
        return max(1, base_time)
    
    def _calculate_general_action_time(self, action: str, personality: str) -> int:
        """计算一般行动耗时"""
        base_time = 2  # 基础2分钟
        
        # 根据行动长度调整
        if len(action) > 20:
            base_time += 1
        
        # 根据性格调整
        if "慢性子" in personality:
            base_time += 1
        elif "急性子" in personality:
            base_time -= 1
        
        return max(1, base_time)
    
    def _advance_game_time(self, current_time: str, minutes: int) -> str:
        """推进游戏时间"""
        try:
            from ..utils.time_utils import TimeUtils
            return TimeUtils.add_minutes(current_time, minutes)
        except Exception as e:
            print(f"时间推进失败: {e}")
            return current_time

    async def stream_action(self, action: str, session_id: str = "default"):
        """
        流式处理玩家行动
        
        Args:
            action: 玩家行动
            session_id: 会话ID
            
        Yields:
            流式响应数据
        """
        try:
            # 目前简化实现，直接返回完整结果
            result = await self.process_action(action, session_id)
            yield f"data: {result}\n\n"
        except Exception as e:
            yield f"data: {self._create_error_response(str(e))}\n\n"
    
    async def get_game_state(self, session_id: str = "default", story_id: int = None) -> Dict[str, Any]:
        """
        获取游戏状态
        
        Args:
            session_id: 会话ID
            story_id: 故事ID
            
        Returns:
            游戏状态响应
        """
        try:
            # 获取用户和故事信息
            user_id, story_id = self._get_user_and_story_info(session_id, story_id)
            
            # 获取游戏状态（支持从数据库恢复）
            game_state = await self.state_service.get_game_state(session_id, user_id, story_id)
            return self._format_game_response(game_state)
            
        except Exception as e:
            print(f"❌ [GameService] 获取游戏状态失败: {e}")
            # 降级到默认状态
            game_state = await self.state_service.get_game_state(session_id)
            return self._format_game_response(game_state, error=str(e))
    
    def initialize_game(self, session_id: str = "default") -> Dict[str, Any]:
        """
        初始化游戏
        
        Args:
            session_id: 会话ID
            
        Returns:
            初始化结果
        """
        try:
            game_state = self.state_service.initialize_game(session_id)
            return self._format_game_response(game_state)
        except Exception as e:
            return {"error": str(e)}
    
    def get_npc_dialogue_history(self, npc_name: str, session_id: str = "default") -> List[Dict[str, str]]:
        """
        获取NPC对话历史
        
        Args:
            npc_name: NPC名称
            session_id: 会话ID
            
        Returns:
            NPC对话历史
        """
        game_state = self.state_service.get_game_state(session_id)
        return game_state.npc_dialogue_histories.get(npc_name, [])
    
    def continue_dialogue(self, npc_name: str, message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        继续与NPC对话
        
        Args:
            npc_name: NPC名称
            message: 对话消息
            session_id: 会话ID
            
        Returns:
            对话结果
        """
        action = f"和{npc_name}说：{message}"
        return self.process_action(action, session_id)

    def _format_game_response(self, game_state: GameStateModel, error: Optional[str] = None, new_messages: List[Dict] = None) -> Dict[str, Any]:
        """
        格式化游戏响应
        
        Args:
            game_state: 游戏状态
            error: 错误信息
            new_messages: 当前操作产生的新消息（避免重复显示历史消息）
            
        Returns:
            格式化的响应
        """
        try:
            from data.locations import all_locations_data, location_connections
            
            # 获取当前位置详情
            location_details = self.location_service.get_location_details(
                game_state.player_location,
                game_state.npc_locations,
                game_state.current_time,
                game_state
            )
            
            response = {
                "player_location": game_state.player_location,
                "current_time": game_state.current_time,
                "location_description": location_details.get("description", ""),
                "connected_locations": [
                    all_locations_data.get(loc_key, {}).get("name", loc_key) 
                    for loc_key in location_details.get("connections", [])
                ],
                "npcs_at_current_location": location_details.get("npcs_present", []),
                # 只返回新消息，不返回完整历史（避免重复）
                "dialogue_history": self._convert_messages_to_dialogue_history(new_messages or [])
            }
            
            # 确保NPC信息包含必要字段
            for npc in response["npcs_at_current_location"]:
                if "event" not in npc:
                    npc["event"] = npc.get("activity", "空闲")
                if "personality" not in npc:
                    npc["personality"] = "友善"
            
            if error:
                response["error"] = error
            
            return response
            
        except Exception as e:
            print(f"❌ 格式化响应失败: {e}")
            return {
                "error": f"格式化响应失败: {str(e)}",
                "player_location": game_state.player_location if game_state else "unknown",
                "current_time": game_state.current_time if game_state else "00:00",
                "location_description": "",
                "connected_locations": [],
                "npcs_at_current_location": [],
                "dialogue_history": []
            }

    def _convert_messages_to_dialogue_history(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        将消息列表转换为对话历史格式
        
        Args:
            messages: 消息列表
            
        Returns:
            对话历史列表
        """
        dialogue_history = []
        
        for msg in messages:
            # 只保留重要的消息类型
            if self._is_important_message(msg):
                dialogue_entry = {
                    "speaker": msg.get("speaker", "系统"),
                    "message": msg.get("message", ""),
                    "timestamp": msg.get("timestamp", ""),
                    "type": msg.get("type", "general")
                }
                dialogue_history.append(dialogue_entry)
        
        return dialogue_history

    def _is_important_message(self, msg: Dict[str, str]) -> bool:
        """
        判断消息是否重要
        
        Args:
            msg: 消息
            
        Returns:
            是否重要
        """
        msg_type = msg.get("type", "")
        speaker = msg.get("speaker", "")
        
        # 保留对话、系统重要消息等
        important_types = ["dialogue", "movement", "exploration", "error", "sensory_feedback"]
        important_speakers = ["系统"]
        
        return (
            msg_type in important_types or 
            speaker in important_speakers or
            speaker != "系统"  # 所有非系统消息都保留
        )

    def _create_error_response(self, error: str) -> str:
        """
        创建错误响应
        
        Args:
            error: 错误信息
            
        Returns:
            错误响应JSON字符串
        """
        import json
        return json.dumps({"error": error}, ensure_ascii=False)

    def _get_user_and_story_info(self, session_id: str, story_id: int = None) -> tuple:
        """获取用户ID和故事ID"""
        # TODO: 从JWT token或会话中获取真实的user_id
        # 目前使用硬编码值作为示例
        user_id = 1  # admin用户
        
        # 使用传入的story_id，如果没有传入则使用默认值
        if story_id is None:
            story_id = 1  # 默认故事
            print(f"⚠️ [GameService] 未传入故事ID，使用默认值: {story_id}")
        
        print(f"🔍 [GameService] 获取会话信息: 用户ID={user_id}, 故事ID={story_id}, 会话ID={session_id}")
        return user_id, story_id

    async def _save_action_result(self, action_type: str, result: Dict[str, Any], game_state: GameStateModel, session_id: str, user_id: int, story_id: int):
        """保存行动处理结果到数据库"""
        try:
            # 使用result中的更新后时间，如果没有则使用当前游戏状态时间
            result_time = result.get("current_time", game_state.current_time)
            game_time = datetime.fromisoformat(result_time.replace('Z', '+00:00')) if isinstance(result_time, str) else result_time
            
            # 获取结果中的消息列表
            messages = result.get("messages", [])
            
            for msg in messages:
                speaker = msg.get("speaker", "系统")
                content = msg.get("message", "")
                msg_type = msg.get("type", "general")
                
                # 使用消息中的时间戳（如果有的话），否则使用计算出的game_time
                msg_timestamp = msg.get("timestamp")
                if msg_timestamp:
                    try:
                        # 尝试解析消息时间戳
                        if isinstance(msg_timestamp, str):
                            if len(msg_timestamp) <= 5:  # 只有时间部分如"07:03"
                                # 将时间部分与结果时间的日期部分组合
                                from ..utils.time_utils import TimeUtils
                                result_dt = TimeUtils.parse_game_time(result_time)
                                time_only = datetime.strptime(msg_timestamp, "%H:%M").time()
                                msg_game_time = datetime.combine(result_dt.date(), time_only)
                            else:
                                msg_game_time = datetime.fromisoformat(msg_timestamp.replace('Z', '+00:00'))
                        else:
                            msg_game_time = msg_timestamp
                    except:
                        msg_game_time = game_time
                else:
                    msg_game_time = game_time
                
                # 根据行动类型和消息类型决定持久化策略
                if action_type == "talk" and speaker != "系统" and speaker != "玩家":
                    # NPC对话
                    await self.message_service.save_npc_dialogue(
                        user_id=user_id,
                        story_id=story_id,
                        session_id=session_id,
                        npc_name=speaker,
                        dialogue=content,
                        location=game_state.player_location,
                        game_time=msg_game_time,
                        metadata={"action_type": action_type, "original_action": result.get("original_action", "")}
                    )
                elif action_type == "talk" and msg_type == "sensory_feedback":
                    # 对话场景的五感反馈
                    await self.message_service.save_sensory_feedback(
                        user_id=user_id,
                        story_id=story_id,
                        session_id=session_id,
                        feedback=content,
                        location=game_state.player_location,
                        game_time=msg_game_time,
                        structured_data={"action_type": action_type, "dialogue_type": "sensory"}
                    )
                elif action_type == "move":
                    # 移动行动
                    await self.message_service.save_system_action(
                        user_id=user_id,
                        story_id=story_id,
                        session_id=session_id,
                        action_result=content,
                        location=game_state.player_location,
                        game_time=msg_game_time,
                        sub_type="movement",
                        metadata={"action_type": action_type, "new_location": result.get("player_location")}
                    )
                    
                    # 如果有五感反馈，也要保存
                    if "sensory_feedback" in result:
                        sensory_data = result["sensory_feedback"]
                        await self.message_service.save_sensory_feedback(
                            user_id=user_id,
                            story_id=story_id,
                            session_id=session_id,
                            feedback=sensory_data.get("description", ""),
                            location=game_state.player_location,
                            game_time=msg_game_time,
                            structured_data=sensory_data
                        )
                elif action_type == "explore":
                    # 探索行动 - 主要是五感反馈
                    if msg_type == "exploration":
                        await self.message_service.save_sensory_feedback(
                            user_id=user_id,
                            story_id=story_id,
                            session_id=session_id,
                            feedback=content,
                            location=game_state.player_location,
                            game_time=msg_game_time,
                            structured_data={"action_type": action_type, "exploration_type": "sensory"}
                        )
                    else:
                        await self.message_service.save_system_info(
                            user_id=user_id,
                            story_id=story_id,
                            session_id=session_id,
                            info=content,
                            location=game_state.player_location,
                            game_time=msg_game_time,
                            sub_type="exploration"
                        )
                else:
                    # 一般行动或其他类型
                    await self.message_service.save_system_info(
                        user_id=user_id,
                        story_id=story_id,
                        session_id=session_id,
                        info=content,
                        location=game_state.player_location,
                        game_time=msg_game_time,
                        sub_type=action_type
                    )
            
            print(f"✅ [GameService] 行动结果持久化完成: {action_type}, 消息数={len(messages)}")
            
        except Exception as e:
            print(f"⚠️ [GameService] 行动结果持久化失败: {e}")
            # 持久化失败不影响游戏流程 