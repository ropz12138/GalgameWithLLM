"""
工作流服务 - 处理LangGraph工作流相关逻辑
"""
import sys
import os
from typing import Dict, Any, Optional

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(os.path.dirname(SRC_DIR))
sys.path.append(PROJECT_ROOT)
sys.path.append(SRC_DIR)

# 导入原有的LangGraph模块
from langgraph_refactor.workflow import (
    execute_game_action,
    stream_game_action,
    get_game_graph
)


class WorkflowService:
    """工作流服务类"""
    
    def __init__(self):
        self.game_graph = None
    
    def _get_game_graph(self):
        """获取游戏图实例"""
        if self.game_graph is None:
            self.game_graph = get_game_graph()
        return self.game_graph
    
    async def execute_action(self, action: str, session_id: str = "default") -> Dict[str, Any]:
        """
        执行游戏行动
        
        Args:
            action: 玩家行动
            session_id: 会话ID
            
        Returns:
            执行结果
        """
        try:
            result = await execute_game_action(action, session_id)
            return result
        except Exception as e:
            print(f"执行行动失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "messages": []
            }
    
    async def stream_action(self, action: str, session_id: str = "default"):
        """
        流式执行游戏行动
        
        Args:
            action: 玩家行动
            session_id: 会话ID
            
        Yields:
            流式响应数据
        """
        try:
            async for chunk in stream_game_action(action, session_id):
                yield chunk
        except Exception as e:
            yield f"data: {self._create_error_response(str(e))}\n\n"
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """
        获取工作流信息
        
        Returns:
            工作流信息
        """
        try:
            graph = self._get_game_graph()
            graph_info = graph.get_graph()
            
            return {
                "nodes": list(graph_info.nodes.keys()),
                "edges": list(graph_info.edges),
                "version": "2.0.0"
            }
        except Exception as e:
            return {
                "error": str(e),
                "nodes": [],
                "edges": [],
                "version": "2.0.0"
            }
    
    def reset_workflow(self):
        """重置工作流"""
        self.game_graph = None
    
    def _create_error_response(self, error: str) -> str:
        """创建错误响应"""
        return f'{{"error": "{error}"}}' 