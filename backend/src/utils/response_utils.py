"""
响应工具类 - 提供标准化的响应格式
"""
from typing import Dict, Any, Optional
from datetime import datetime


class ResponseUtils:
    """响应工具类"""
    
    @staticmethod
    def success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
        """
        创建成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            
        Returns:
            成功响应
        """
        return {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error_response(error: str, code: int = 500, data: Any = None) -> Dict[str, Any]:
        """
        创建错误响应
        
        Args:
            error: 错误信息
            code: 错误代码
            data: 错误数据
            
        Returns:
            错误响应
        """
        return {
            "success": False,
            "error": error,
            "code": code,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def paginated_response(
        data: list,
        page: int = 1,
        size: int = 10,
        total: int = 0,
        message: str = "获取成功"
    ) -> Dict[str, Any]:
        """
        创建分页响应
        
        Args:
            data: 数据列表
            page: 当前页码
            size: 每页大小
            total: 总数量
            message: 响应消息
            
        Returns:
            分页响应
        """
        return {
            "success": True,
            "message": message,
            "data": data,
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def stream_response(data: str) -> str:
        """
        创建流式响应格式
        
        Args:
            data: 响应数据
            
        Returns:
            流式响应字符串
        """
        return f"data: {data}\n\n"
    
    @staticmethod
    def game_state_response(
        player_location: str,
        current_time: str,
        location_description: str,
        connected_locations: list,
        npcs_at_current_location: list,
        dialogue_history: list,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建游戏状态响应
        
        Args:
            player_location: 玩家位置
            current_time: 当前时间
            location_description: 位置描述
            connected_locations: 相连位置
            npcs_at_current_location: 当前位置的NPC
            dialogue_history: 对话历史
            error: 错误信息
            
        Returns:
            游戏状态响应
        """
        response = {
            "player_location": player_location,
            "current_time": current_time,
            "location_description": location_description,
            "connected_locations": connected_locations,
            "npcs_at_current_location": npcs_at_current_location,
            "dialogue_history": dialogue_history
        }
        
        if error:
            response["error"] = error
            
        return response 