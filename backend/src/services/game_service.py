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

from models.game_state_model import GameStateModel
from models.player_model import PlayerModel
from models.npc_model import NPCModel
from models.message_model import MessageModel
from services.workflow_service import WorkflowService
from services.state_service import StateService


class GameService:
    """游戏服务类"""
    
    def __init__(self):
        self.workflow_service = WorkflowService()
        self.state_service = StateService()
    
    async def process_action(self, action: str, session_id: str = "default") -> Dict[str, Any]:
        """
        处理玩家行动
        
        Args:
            action: 玩家行动
            session_id: 会话ID
            
        Returns:
            处理结果
        """
        try:
            print(f"\n🔍 [GameService] 开始处理行动:")
            print(f"  📝 行动内容: '{action}'")
            print(f"  🆔 会话ID: {session_id}")
            
            # 获取处理前的状态
            before_state = self.state_service.get_game_state(session_id)
            print(f"  📊 处理前状态:")
            print(f"    💬 消息数量: {len(before_state.messages)}")
            print(f"    💬 消息内容: {before_state.messages}")
            
            # 执行工作流
            print(f"  🔄 开始执行工作流...")
            result = await self.workflow_service.execute_action(action, session_id)
            print(f"  ✅ 工作流执行完成:")
            print(f"    📊 执行结果: {result}")
            print(f"    💬 返回消息数量: {len(result.get('messages', []))}")
            print(f"    💬 返回消息内容: {result.get('messages', [])}")
            
            if result["success"]:
                # 获取更新后的状态
                print(f"  📊 获取更新后状态...")
                game_state = self.state_service.get_game_state(session_id)
                print(f"  📊 更新后状态:")
                print(f"    💬 消息数量: {len(game_state.messages)}")
                print(f"    💬 消息内容: {game_state.messages}")
                
                formatted_response = self._format_game_response(game_state)
                print(f"  📤 格式化响应:")
                print(f"    💬 对话历史长度: {len(formatted_response.get('dialogue_history', []))}")
                print(f"    💬 对话历史内容: {formatted_response.get('dialogue_history', [])}")
                
                return formatted_response
            else:
                # 处理失败，返回当前状态
                print(f"  ❌ 工作流执行失败: {result.get('error')}")
                game_state = self.state_service.get_game_state(session_id)
                return self._format_game_response(game_state, error=result.get("error"))
                
        except Exception as e:
            print(f"❌ [GameService] 处理行动错误: {e}")
            game_state = self.state_service.get_game_state(session_id)
            return self._format_game_response(game_state, error=str(e))
    
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
            async for chunk in self.workflow_service.stream_action(action, session_id):
                yield chunk
        except Exception as e:
            yield f"data: {self._create_error_response(str(e))}\n\n"
    
    def get_game_state(self, session_id: str = "default") -> Dict[str, Any]:
        """
        获取游戏状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            游戏状态
        """
        game_state = self.state_service.get_game_state(session_id)
        return self._format_game_response(game_state)
    
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
    
    def _format_game_response(self, game_state: GameStateModel, error: Optional[str] = None) -> Dict[str, Any]:
        """
        格式化游戏响应
        
        Args:
            game_state: 游戏状态
            error: 错误信息
            
        Returns:
            格式化的响应
        """
        try:
            from data.locations import all_locations_data, location_connections
            
            # 获取当前位置详情
            location_details = self._get_location_details(
                game_state.player_location,
                game_state.npc_locations,
                game_state.current_time
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
                "dialogue_history": self._convert_messages_to_dialogue_history(game_state.messages)
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
            return {
                "error": f"格式化响应失败: {str(e)}",
                "player_location": game_state.player_location,
                "current_time": game_state.current_time,
                "location_description": "",
                "connected_locations": [],
                "npcs_at_current_location": [],
                "dialogue_history": []
            }
    
    def _get_location_details(self, location_name: str, npc_locations: Dict[str, str], current_time: str) -> Dict[str, Any]:
        """获取位置详情"""
        try:
            from data.locations import all_locations_data, location_connections
            from data.characters import all_actresses
            
            location_data = all_locations_data.get(location_name, {})
            connections = location_connections.get(location_name, [])
            
            # 获取当前位置的NPC
            npcs_present = []
            for actress in all_actresses:
                npc_name = actress["name"]
                if npc_locations.get(npc_name) == location_name:
                    npc_info = {
                        "name": npc_name,
                        "personality": actress.get("personality", "友善"),
                        "activity": "空闲"
                    }
                    
                    # 查找当前时间的活动
                    for event_info in actress.get("schedule", []):
                        try:
                            start_time = datetime.strptime(event_info["start_time"], "%H:%M").time()
                            end_time = datetime.strptime(event_info["end_time"], "%H:%M").time()
                            current_time_obj = datetime.strptime(current_time, "%H:%M").time()
                            
                            if start_time <= current_time_obj < end_time:
                                npc_info["activity"] = event_info.get("activity", "忙碌")
                                break
                        except ValueError:
                            continue
                    
                    npcs_present.append(npc_info)
            
            return {
                "description": location_data.get("description", ""),
                "connections": connections,
                "npcs_present": npcs_present
            }
            
        except Exception as e:
            print(f"获取位置详情失败: {e}")
            return {
                "description": "",
                "connections": [],
                "npcs_present": []
            }
    
    def _convert_messages_to_dialogue_history(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """转换消息为对话历史格式"""
        print(f"\n🔍 [GameService] 开始转换消息为对话历史:")
        print(f"  📝 原始消息数量: {len(messages)}")
        print(f"  📝 原始消息内容: {messages}")
        
        dialogue_history = []
        
        for i, msg in enumerate(messages):
            print(f"  🔍 处理消息 {i+1}: {msg}")
            if self._is_important_message(msg):
                print(f"    ✅ 标记为重要消息，添加到对话历史")
                dialogue_history.append({
                    "speaker": msg["speaker"],
                    "message": msg["message"]
                })
            else:
                print(f"    ❌ 标记为非重要消息，跳过")
        
        print(f"  📤 转换完成:")
        print(f"    💬 对话历史数量: {len(dialogue_history)}")
        print(f"    💬 对话历史内容: {dialogue_history}")
        
        return dialogue_history
    
    def _is_important_message(self, msg: Dict[str, str]) -> bool:
        """判断是否为重要消息"""
        speaker = msg.get("speaker", "")
        message = msg.get("message", "")
        
        print(f"    🔍 判断消息重要性: speaker='{speaker}', message='{message[:50]}...'")
        
        # 系统消息
        if speaker == "系统":
            print(f"      ✅ 系统消息，标记为重要")
            return True
        
        # 玩家消息 - 应该显示在对话历史中
        if speaker == "玩家":
            print(f"      ✅ 玩家消息，标记为重要")
            return True
        
        # NPC消息
        if speaker not in ["玩家", "系统", "游戏"]:
            print(f"      ✅ NPC消息 ({speaker})，标记为重要")
            return True
        
        # 重要的游戏消息
        important_keywords = ["到达", "离开", "遇到", "发现", "获得", "失去"]
        if any(keyword in message for keyword in important_keywords):
            print(f"      ✅ 包含重要关键词，标记为重要")
            return True
        
        print(f"      ❌ 其他消息，标记为非重要")
        return False
    
    def _create_error_response(self, error: str) -> str:
        """创建错误响应"""
        return f'{{"error": "{error}"}}' 