"""
游戏控制器 - 处理游戏相关的HTTP请求
"""
from typing import Dict, Any, List
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from ..services.game_service import GameService


class GameController:
    """游戏控制器类"""
    
    def __init__(self):
        self.game_service = GameService()
    
    async def get_game_state(self, session_id: str = "default") -> Dict[str, Any]:
        """
        获取游戏状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            游戏状态
        """
        try:
            return self.game_service.get_game_state(session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取游戏状态失败: {str(e)}")
    
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
            print(f"\n🔍 [后端] 收到处理行动请求:")
            print(f"  📝 行动内容: '{action}'")
            print(f"  🆔 会话ID: {session_id}")
            
            result = await self.game_service.process_action(action, session_id)
            
            print(f"✅ [后端] 行动处理完成:")
            print(f"  📊 返回结果: {result}")
            print(f"  💬 对话历史长度: {len(result.get('dialogue_history', []))}")
            print(f"  💬 对话历史内容: {result.get('dialogue_history', [])}")
            
            return result
        except Exception as e:
            print(f"❌ [后端] 处理行动时出错: {e}")
            return {"error": str(e)}
    
    async def stream_action(self, action: str, session_id: str = "default") -> StreamingResponse:
        """
        流式处理玩家行动
        
        Args:
            action: 玩家行动
            session_id: 会话ID
            
        Returns:
            流式响应
        """
        try:
            async def generate_stream():
                async for chunk in self.game_service.stream_action(action, session_id):
                    yield chunk
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"流式处理失败: {str(e)}")
    
    async def initialize_game(self, session_id: str = "default") -> Dict[str, Any]:
        """
        初始化游戏
        
        Args:
            session_id: 会话ID
            
        Returns:
            初始化结果
        """
        try:
            return self.game_service.initialize_game(session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"初始化游戏失败: {str(e)}")
    
    async def get_npc_dialogue_history(self, npc_name: str, session_id: str = "default") -> List[Dict[str, str]]:
        """
        获取NPC对话历史
        
        Args:
            npc_name: NPC名称
            session_id: 会话ID
            
        Returns:
            NPC对话历史
        """
        try:
            return self.game_service.get_npc_dialogue_history(npc_name, session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取NPC对话历史失败: {str(e)}")
    
    async def continue_dialogue(self, npc_name: str, message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        继续与NPC对话
        
        Args:
            npc_name: NPC名称
            message: 对话消息
            session_id: 会话ID
            
        Returns:
            对话结果
        """
        try:
            return await self.game_service.continue_dialogue(npc_name, message, session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"继续对话失败: {str(e)}") 