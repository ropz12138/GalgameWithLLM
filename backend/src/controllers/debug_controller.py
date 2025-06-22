"""
调试控制器 - 处理调试相关的HTTP请求
"""
from typing import Dict, Any, List
from fastapi import HTTPException
import sys
import os

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from ..services.state_service import StateService


class DebugController:
    """调试控制器类"""
    
    def __init__(self):
        self.state_service = StateService()
        from ..services.npc_service import NPCService
        self.npc_service = NPCService()
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """
        获取工作流信息
        
        Returns:
            工作流信息
        """
        try:
            return {
                "message": "新架构已移除WorkflowService",
                "architecture": "MVC with Services",
                "services": [
                    "GameService",
                    "StateService", 
                    "DialogueService",
                    "NPCService",
                    "LocationService",
                    "MovementService",
                    "ActionRouterService"
                ]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取工作流信息失败: {str(e)}")
    
    def get_workflow_state(self, session_id: str = "default") -> Dict[str, Any]:
        """
        获取工作流状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            工作流状态
        """
        try:
            game_state = self.state_service.get_game_state(session_id)
            return game_state.to_dict()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取工作流状态失败: {str(e)}")
    
    def get_locations_info(self) -> Dict[str, Any]:
        """
        获取位置信息
        
        Returns:
            位置信息
        """
        try:
            from data.locations import all_locations_data, location_connections
            
            return {
                "locations": all_locations_data,
                "connections": location_connections
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取位置信息失败: {str(e)}")
    
    def get_npc_locations(self, session_id: str = "default") -> Dict[str, str]:
        """
        获取NPC位置
        
        Args:
            session_id: 会话ID
            
        Returns:
            NPC位置信息
        """
        try:
            game_state = self.state_service.get_game_state(session_id)
            return game_state.npc_locations
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取NPC位置失败: {str(e)}")
    
    def get_npcs_info(self) -> List[Dict[str, Any]]:
        """
        获取NPC信息
        
        Returns:
            NPC信息列表
        """
        try:
            from data.characters import all_actresses
            
            return all_actresses
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取NPC信息失败: {str(e)}")
    
    def get_npc_status_info(self, session_id: str = "default") -> Dict[str, Any]:
        """
        获取NPC状态信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            NPC状态信息
        """
        try:
            from data.characters import all_actresses
            from datetime import datetime
            
            print(f"\n🔍 [DEBUG] 开始获取NPC状态信息 - session_id: {session_id}")
            
            game_state = self.state_service.get_game_state(session_id)
            current_time = game_state.current_time
            player_location = game_state.player_location
            
            print(f"🔍 [DEBUG] 游戏状态信息:")
            print(f"  - 当前时间: {current_time}")
            print(f"  - 玩家位置: {player_location}")
            print(f"  - 游戏状态中的NPC位置: {game_state.npc_locations}")
            print(f"  - 动态计划表: {getattr(game_state, 'npc_dynamic_schedules', {})}")
            
            # 获取当前时间对象
            current_time_obj = datetime.strptime(current_time, "%H:%M").time()
            
            # 构建NPC状态信息
            npc_status = {}
            npcs_at_player_location = []
            
            print(f"\n🔍 [DEBUG] 开始计算每个NPC的状态:")
            
            for actress in all_actresses:
                npc_name = actress["name"]
                print(f"\n🔍 [DEBUG] 处理NPC: {npc_name}")
                print(f"  - 原始数据: {actress}")
                
                # 使用NPCService获取当前位置和活动（包括动态计划表）
                current_location, current_event = self.npc_service.get_npc_current_location_and_event(
                    npc_name, current_time_obj, game_state
                )
                
                print(f"  ✅ 使用NPCService获取状态:")
                print(f"    - 当前位置: {current_location}")
                print(f"    - 当前活动: {current_event}")
                
                # 获取当前有效的计划表（包括动态更新的）
                current_schedule = self.npc_service.get_npc_current_schedule(npc_name, game_state)
                print(f"    - 当前计划表: {current_schedule}")
                
                # 构建NPC状态信息
                npc_status[npc_name] = {
                    "current_location": current_location,
                    "current_event": current_event,
                    "personality": actress.get("personality", "友善"),
                    "schedule": current_schedule  # 使用当前有效的计划表
                }
                
                print(f"  - 最终状态: 位置={current_location}, 活动={current_event}")
                
                # 检查是否在玩家当前位置
                if current_location == player_location:
                    npcs_at_player_location.append({
                        "name": npc_name,
                        "event": current_event,
                        "personality": actress.get("personality", "友善")
                    })
                    print(f"  ✅ 在玩家当前位置，已添加到列表")
                else:
                    print(f"  ❌ 不在玩家当前位置")
            
            result = {
                "current_time": current_time,
                "player_location": player_location,
                "npcs_at_player_location": npcs_at_player_location,
                "npc_locations": npc_status
            }
            
            print(f"\n🔍 [DEBUG] NPC状态信息计算结果:")
            print(f"  - 在玩家位置的NPC: {[npc['name'] for npc in npcs_at_player_location]}")
            print(f"  - 所有NPC状态: {npc_status}")
            
            return result
            
        except Exception as e:
            print(f"❌ [DEBUG] 获取NPC状态信息失败: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"获取NPC状态信息失败: {str(e)}")
    
    def get_messages(self, session_id: str = "default") -> List[Dict[str, str]]:
        """
        获取消息历史
        
        Args:
            session_id: 会话ID
            
        Returns:
            消息历史
        """
        try:
            game_state = self.state_service.get_game_state(session_id)
            return game_state.messages
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取消息历史失败: {str(e)}")
    
    def reset_session(self, session_id: str = "default") -> Dict[str, str]:
        """
        重置会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            重置结果
        """
        try:
            self.state_service.clear_session(session_id)
            return {"message": f"会话 {session_id} 已重置"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"重置会话失败: {str(e)}")
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有会话
        
        Returns:
            所有会话信息
        """
        try:
            sessions = self.state_service.get_all_sessions()
            return {session_id: game_state.to_dict() for session_id, game_state in sessions.items()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取所有会话失败: {str(e)}") 