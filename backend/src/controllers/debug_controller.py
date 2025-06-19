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