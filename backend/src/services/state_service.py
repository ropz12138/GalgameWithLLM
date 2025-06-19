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

from models.game_state_model import GameStateModel
from langgraph_refactor.workflow import get_game_state as get_langgraph_state, initialize_new_game


class StateService:
    """状态服务类"""
    
    def __init__(self):
        self._state_cache: Dict[str, GameStateModel] = {}
    
    def get_game_state(self, session_id: str = "default") -> GameStateModel:
        """
        获取游戏状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            游戏状态模型
        """
        try:
            # 从LangGraph获取状态
            langgraph_state = get_langgraph_state(session_id)
            
            # 转换为模型对象
            game_state = GameStateModel.from_dict(langgraph_state)
            
            # 缓存状态
            self._state_cache[session_id] = game_state
            
            return game_state
            
        except Exception as e:
            print(f"获取游戏状态失败: {e}")
            # 返回缓存的状态或创建新状态
            if session_id in self._state_cache:
                return self._state_cache[session_id]
            else:
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
            # 调用LangGraph的初始化
            initialize_new_game(session_id)
            
            # 获取初始状态
            game_state = self.get_game_state(session_id)
            
            return game_state
            
        except Exception as e:
            print(f"初始化游戏失败: {e}")
            return self._create_default_state(session_id)
    
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
        self._state_cache[session_id] = game_state
        
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
        self._state_cache[session_id] = game_state
    
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
        self._state_cache[session_id] = game_state
    
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
        self._state_cache[session_id] = game_state
    
    def clear_session(self, session_id: str):
        """
        清除会话状态
        
        Args:
            session_id: 会话ID
        """
        if session_id in self._state_cache:
            del self._state_cache[session_id]
    
    def get_all_sessions(self) -> Dict[str, GameStateModel]:
        """
        获取所有会话状态
        
        Returns:
            所有会话状态
        """
        return self._state_cache.copy()
    
    def _create_default_state(self, session_id: str) -> GameStateModel:
        """
        创建默认状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            默认游戏状态
        """
        game_state = GameStateModel(session_id)
        self._state_cache[session_id] = game_state
        return game_state 