"""
LangGraph重构版本的LLM文字游戏
"""

__version__ = "2.0.0"
__author__ = "Assistant"
__description__ = "基于LangGraph的LLM驱动文字游戏重构版本"

from .workflow import (
    get_game_graph,
    execute_game_action,
    get_game_state,
    initialize_new_game,
    stream_game_action
)

from .api_integration import create_langgraph_api_app

__all__ = [
    "get_game_graph",
    "execute_game_action", 
    "get_game_state",
    "initialize_new_game",
    "stream_game_action",
    "create_langgraph_api_app"
] 