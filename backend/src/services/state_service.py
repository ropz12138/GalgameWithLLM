"""
状态服务 - 处理游戏状态管理
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

from ..models.game_state_model import GameStateModel
# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from data.game_config import INITIAL_GAME_STATE


class StateService:
    """状态服务类"""
    
    _instance = None
    _state_cache: Dict[str, GameStateModel] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 避免重复初始化
        if not hasattr(self, '_initialized'):
            self._initialized = True
    
    def get_game_state(self, session_id: str = "default") -> GameStateModel:
        """
        获取游戏状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            游戏状态模型
        """
        try:
            # 从缓存获取状态
            if session_id in StateService._state_cache:
                return StateService._state_cache[session_id]
            else:
                # 如果没有缓存，创建新状态
                return self._create_default_state(session_id)
            
        except Exception as e:
            print(f"获取游戏状态失败: {e}")
            return self._create_default_state(session_id)
    
    def initialize_game(self, session_id: str = "default") -> GameStateModel:
        """
        初始化游戏
        
        Args:
            session_id: 会话ID
            
        Returns:
            初始化的游戏状态
        """
        try:
            print(f"🎮 [StateService] 初始化游戏 - 会话ID: {session_id}")
            
            # 创建新的游戏状态
            game_state = GameStateModel(session_id)
            
            # 使用初始配置
            initial_config = INITIAL_GAME_STATE.copy()
            
            # 设置初始状态
            game_state.player_location = initial_config.get("player_location", "player_room")
            game_state.current_time = initial_config.get("current_time", "07:00")
            game_state.player_personality = initial_config.get("player_personality", "普通")
            
            # 初始化NPC位置
            from .npc_service import NPCService
            npc_service = NPCService()
            game_state.npc_locations = npc_service.update_npc_locations_by_time(
                game_state.current_time, game_state
            )
            
            # 添加欢迎消息
            game_state.add_message("系统", "游戏开始！欢迎来到这个世界。", "system")
            
            # 缓存状态
            StateService._state_cache[session_id] = game_state
            
            print(f"✅ 游戏初始化完成:")
            print(f"  📍 初始位置: {game_state.player_location}")
            print(f"  ⏰ 初始时间: {game_state.current_time}")
            print(f"  👤 玩家性格: {game_state.player_personality}")
            print(f"  🎭 NPC位置: {game_state.npc_locations}")
            
            return game_state
            
        except Exception as e:
            print(f"❌ 初始化游戏失败: {e}")
            import traceback
            traceback.print_exc()
            return self._create_default_state(session_id)
    
    def save_game_state(self, session_id: str, game_state: GameStateModel):
        """
        保存游戏状态
        
        Args:
            session_id: 会话ID
            game_state: 游戏状态
        """
        StateService._state_cache[session_id] = game_state
        print(f"💾 [StateService] 游戏状态已保存 - 会话ID: {session_id}")
    
    def update_game_state(self, session_id: str, updates: Dict[str, Any]) -> GameStateModel:
        """
        更新游戏状态
        
        Args:
            session_id: 会话ID
            updates: 更新内容
            
        Returns:
            更新后的游戏状态
        """
        game_state = self.get_game_state(session_id)
        
        # 应用更新
        for key, value in updates.items():
            if hasattr(game_state, key):
                setattr(game_state, key, value)
        
        # 更新缓存
        StateService._state_cache[session_id] = game_state
        
        return game_state
    
    def add_message(self, session_id: str, speaker: str, message: str, message_type: str = "normal"):
        """
        添加消息到游戏状态
        
        Args:
            session_id: 会话ID
            speaker: 说话者
            message: 消息内容
            message_type: 消息类型
        """
        game_state = self.get_game_state(session_id)
        game_state.add_message(speaker, message, message_type)
        
        # 更新缓存
        StateService._state_cache[session_id] = game_state
    
    def update_player_location(self, session_id: str, new_location: str):
        """
        更新玩家位置
        
        Args:
            session_id: 会话ID
            new_location: 新位置
        """
        game_state = self.get_game_state(session_id)
        game_state.update_location(new_location)
        
        # 更新缓存
        StateService._state_cache[session_id] = game_state
    
    def update_game_time(self, session_id: str, new_time: str):
        """
        更新游戏时间
        
        Args:
            session_id: 会话ID
            new_time: 新时间
        """
        game_state = self.get_game_state(session_id)
        game_state.update_time(new_time)
        
        # 更新缓存
        StateService._state_cache[session_id] = game_state
    
    def clear_session(self, session_id: str):
        """
        清除会话状态
        
        Args:
            session_id: 会话ID
        """
        if session_id in StateService._state_cache:
            del StateService._state_cache[session_id]
            print(f"🗑️ [StateService] 已清除会话状态 - 会话ID: {session_id}")
    
    def get_all_sessions(self) -> Dict[str, GameStateModel]:
        """
        获取所有会话状态
        
        Returns:
            所有会话状态
        """
        return StateService._state_cache.copy()
    
    def _create_default_state(self, session_id: str) -> GameStateModel:
        """
        创建默认状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            默认游戏状态
        """
        print(f"🔧 [StateService] 创建默认状态 - 会话ID: {session_id}")
        
        game_state = GameStateModel(session_id)
        
        # 使用配置文件的初始配置
        initial_config = INITIAL_GAME_STATE.copy()
        game_state.player_location = initial_config.get("player_location", "linkai_room")
        game_state.current_time = initial_config.get("current_time", "07:00")
        game_state.player_personality = initial_config.get("player_personality", "普通")
        game_state.npc_locations = {}
        game_state.npc_dialogue_histories = {}
        game_state.messages = []
        
        StateService._state_cache[session_id] = game_state
        return game_state 