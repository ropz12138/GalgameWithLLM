"""
Routers层 - 路由层，定义API路由
"""

from .game_router import game_router
from .debug_router import debug_router
from .llm_router import llm_router
from .auth_router import auth_router

__all__ = [
    "game_router",
    "debug_router", 
    "llm_router",
    "auth_router"
] 