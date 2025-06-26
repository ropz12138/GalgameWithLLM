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
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 避免重复初始化
        if not hasattr(self, '_initialized'):
            from .message_service import MessageService
            self.message_service = MessageService()
            self._initialized = True
    
    async def get_game_state(self, session_id: str = "default", user_id: int = None, story_id: int = None) -> GameStateModel:
        """
        获取游戏状态 - 直接从数据库获取
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            story_id: 故事ID
            
        Returns:
            游戏状态模型
        """
        try:
            print(f"🔍 [StateService] 从数据库获取游戏状态: 用户={user_id}, 故事={story_id}, 会话={session_id}")
            
            # 直接从数据库恢复或创建状态
            return await self._create_or_restore_state(session_id, user_id, story_id)
            
        except Exception as e:
            print(f"❌ 获取游戏状态失败: {e}")
            return await self._create_default_state(session_id, story_id)
    
    async def _create_or_restore_state(self, session_id: str, user_id: int = None, story_id: int = None) -> GameStateModel:
        """
        创建或从数据库恢复游戏状态
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            story_id: 故事ID
            
        Returns:
            游戏状态模型
        """
        try:
            # 如果有用户ID和故事ID，尝试从数据库恢复状态
            if user_id and story_id:
                print(f"🔄 [StateService] 从数据库恢复状态: 用户={user_id}, 故事={story_id}, 会话={session_id}")
                
                latest_state = await self.message_service.get_latest_game_state(user_id, story_id, session_id)
                
                if latest_state.get("current_time") or latest_state.get("player_location"):
                    print(f"✅ [StateService] 从数据库恢复状态成功")
                    
                    # 创建游戏状态并使用数据库中的数据
                    game_state = GameStateModel(session_id, story_id)
                    
                    # 使用数据库中的时间和位置，如果没有则使用默认值
                    initial_config = INITIAL_GAME_STATE.copy()
                    
                    # 设置时间
                    if latest_state.get("current_time"):
                        game_state.current_time = latest_state["current_time"]
                        print(f"  ⏰ 恢复时间: {game_state.current_time}")
                    else:
                        game_state.current_time = initial_config.get("current_time", "07:00")
                        print(f"  ⏰ 使用默认时间: {game_state.current_time}")
                    
                    # 设置位置
                    if latest_state.get("player_location"):
                        game_state.player_location = latest_state["player_location"]
                        print(f"  📍 恢复位置: {game_state.player_location}")
                    else:
                        game_state.player_location = initial_config.get("player_location", "linkai_room")
                        print(f"  📍 使用默认位置: {game_state.player_location}")
                    
                    # 设置其他默认属性
                    game_state.player_personality = initial_config.get("player_personality", "普通")
                    
                    # 初始化NPC位置
                    from .npc_service import NPCService
                    npc_service = NPCService()
                    game_state.npc_locations = npc_service.update_npc_locations_by_time(
                        game_state.current_time, game_state
                    )
                    
                    # 初始化其他属性
                    game_state.npc_dialogue_histories = {}
                    game_state.messages = []
                    
                    print(f"✅ [StateService] 状态恢复完成:")
                    print(f"  📍 当前位置: {game_state.player_location}")
                    print(f"  ⏰ 当前时间: {game_state.current_time}")
                    print(f"  👤 玩家性格: {game_state.player_personality}")
                    
                    return game_state
                else:
                    print(f"⚠️ [StateService] 数据库中没有找到状态数据，创建新状态")
            
            # 如果没有数据库数据或参数不足，创建默认状态
            return await self._create_default_state(session_id, story_id)
            
        except Exception as e:
            print(f"❌ [StateService] 恢复状态失败: {e}")
            import traceback
            traceback.print_exc()
            return await self._create_default_state(session_id, story_id)
    
    async def _create_default_state(self, session_id: str, story_id: int = None) -> GameStateModel:
        """
        创建默认状态
        
        Args:
            session_id: 会话ID
            story_id: 故事ID
            
        Returns:
            默认游戏状态
        """
        print(f"🔧 [StateService] 创建默认状态 - 会话ID: {session_id}, 故事ID: {story_id}")
        
        game_state = GameStateModel(session_id, story_id)
        
        # 使用配置文件的初始配置
        initial_config = INITIAL_GAME_STATE.copy()
        game_state.player_location = initial_config.get("player_location", "linkai_room")
        game_state.current_time = initial_config.get("current_time", "07:00")
        game_state.player_personality = initial_config.get("player_personality", "普通")
        game_state.npc_locations = {}
        game_state.npc_dialogue_histories = {}
        game_state.messages = []
        
        return game_state
    
    def initialize_game(self, session_id: str = "default", story_id: int = None) -> GameStateModel:
        """
        初始化游戏
        
        Args:
            session_id: 会话ID
            story_id: 故事ID
            
        Returns:
            初始化的游戏状态
        """
        try:
            print(f"🎮 [StateService] 初始化游戏 - 会话ID: {session_id}, 故事ID: {story_id}")
            
            # 创建新的游戏状态
            game_state = GameStateModel(session_id, story_id)
            
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
            # 创建一个简单的默认状态
            return GameStateModel(session_id, story_id)
    
    def save_game_state(self, session_id: str, game_state: GameStateModel, story_id: int = None):
        """
        保存游戏状态 - 移除缓存功能，仅保留接口兼容性
        
        Args:
            session_id: 会话ID
            game_state: 游戏状态
            story_id: 故事ID
        """
        print(f"💾 [StateService] 游戏状态保存请求 - 会话ID: {session_id}, 故事ID: {story_id}")
        # 注意：不再保存到缓存，状态完全依赖数据库持久化
    
    async def update_game_state(self, session_id: str, updates: Dict[str, Any], story_id: int = None) -> GameStateModel:
        """
        更新游戏状态
        
        Args:
            session_id: 会话ID
            updates: 更新内容
            story_id: 故事ID
            
        Returns:
            更新后的游戏状态
        """
        # 重新从数据库获取最新状态
        game_state = await self.get_game_state(session_id, story_id=story_id)
        
        # 应用更新
        for key, value in updates.items():
            if hasattr(game_state, key):
                setattr(game_state, key, value)
        
        return game_state
    
    async def add_message(self, session_id: str, speaker: str, message: str, message_type: str = "normal"):
        """
        添加消息到游戏状态
        
        Args:
            session_id: 会话ID
            speaker: 说话者
            message: 消息内容
            message_type: 消息类型
        """
        # 重新从数据库获取最新状态
        game_state = await self.get_game_state(session_id)
        game_state.add_message(speaker, message, message_type)
        
        # 注意：不再更新缓存，状态变更依赖数据库持久化
    
    async def update_player_location(self, session_id: str, new_location: str):
        """
        更新玩家位置
        
        Args:
            session_id: 会话ID
            new_location: 新位置
        """
        # 重新从数据库获取最新状态
        game_state = await self.get_game_state(session_id)
        game_state.update_location(new_location)
        
        # 注意：不再更新缓存，状态变更依赖数据库持久化
    
    async def update_game_time(self, session_id: str, new_time: str):
        """
        更新游戏时间
        
        Args:
            session_id: 会话ID
            new_time: 新时间
        """
        # 重新从数据库获取最新状态
        game_state = await self.get_game_state(session_id)
        game_state.update_time(new_time)
        
        # 注意：不再更新缓存，状态变更依赖数据库持久化
    
    def clear_session(self, session_id: str, story_id: int = None):
        """
        清除会话状态 - 移除缓存功能，仅保留接口兼容性
        
        Args:
            session_id: 会话ID
            story_id: 故事ID
        """
        print(f"🗑️ [StateService] 清除会话状态请求 - 会话ID: {session_id}, 故事ID: {story_id}")
        # 注意：不再操作缓存，如需清除数据应操作数据库
    
    def get_all_sessions(self) -> Dict[str, GameStateModel]:
        """
        获取所有会话状态 - 移除缓存功能，返回空字典
        
        Returns:
            空字典（不再支持获取所有会话）
        """
        print("⚠️ [StateService] get_all_sessions 已移除缓存支持，返回空字典")
        return {} 