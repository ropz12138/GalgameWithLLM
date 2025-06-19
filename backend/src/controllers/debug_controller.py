"""
调试控制器 - 处理调试相关的HTTP请求
"""
from typing import Dict, Any, List
from fastapi import HTTPException

from services.workflow_service import WorkflowService
from services.state_service import StateService


class DebugController:
    """调试控制器类"""
    
    def __init__(self):
        self.workflow_service = WorkflowService()
        self.state_service = StateService()
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """
        获取工作流信息
        
        Returns:
            工作流信息
        """
        try:
            return self.workflow_service.get_workflow_info()
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
                
                # 获取NPC当前位置和活动
                current_location = "未知地点"
                current_event = "空闲"
                
                # 查找当前时间的活动
                print(f"  - 检查计划表: {actress.get('schedule', [])}")
                for event_info in actress.get("schedule", []):
                    try:
                        start_time = datetime.strptime(event_info["start_time"], "%H:%M").time()
                        end_time = datetime.strptime(event_info["end_time"], "%H:%M").time()
                        
                        print(f"    - 检查计划: {event_info['start_time']}-{event_info['end_time']} 在{event_info['location']}：{event_info.get('event', '忙碌')}")
                        print(f"    - 时间匹配: {start_time} <= {current_time_obj} < {end_time} = {start_time <= current_time_obj < end_time}")
                        
                        if start_time <= current_time_obj < end_time:
                            current_location = event_info["location"]
                            current_event = event_info.get("event", "忙碌")
                            print(f"    ✅ 匹配成功! 位置: {current_location}, 活动: {current_event}")
                            break
                    except ValueError as e:
                        print(f"    ❌ 时间解析错误: {e}")
                        continue
                
                # 如果没找到当前活动，使用默认位置
                if current_location == "未知地点":
                    current_location = actress.get("default_location", "未知地点")
                    print(f"  - 使用默认位置: {current_location}")
                
                # 构建NPC状态信息
                npc_status[npc_name] = {
                    "current_location": current_location,
                    "current_event": current_event,
                    "personality": actress.get("personality", "友善"),
                    "schedule": actress.get("schedule", [])
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
            self.workflow_service.reset_workflow()
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