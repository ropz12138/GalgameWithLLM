"""
故事控制器 - 处理故事相关的API请求
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import sys
import os

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_ROOT)

from data.characters import all_actresses
from data.locations import all_locations_data, location_connections


class StoryController:
    """故事控制器类"""
    
    def __init__(self):
        pass
    
    def get_all_story_info(self) -> Dict[str, Any]:
        """
        获取所有故事信息
        
        Returns:
            包含所有NPC和位置信息的字典
        """
        try:
            # 获取所有NPC信息
            npcs_info = []
            for npc in all_actresses:
                npc_info = {
                    "name": npc.get("name", ""),
                    "personality": npc.get("personality", ""),
                    "background": npc.get("background", ""),
                    "mood": npc.get("mood", "平静"),
                    "relations": npc.get("relations", {}),
                    "schedule": npc.get("schedule", [])
                }
                npcs_info.append(npc_info)
            
            # 获取所有位置信息
            locations_info = []
            for location_key, location_data in all_locations_data.items():
                location_info = {
                    "key": location_key,
                    "name": location_data.get("name", ""),
                    "en_name": location_data.get("en_name", location_key),
                    "description": location_data.get("description", ""),
                    "connections": location_connections.get(location_key, [])
                }
                locations_info.append(location_info)
            
            # 获取游戏配置信息
            from ..utils.config_loader import get_game_config
            game_config = get_game_config()
            
            story_info = {
                "npcs": npcs_info,
                "locations": locations_info,
                "game_config": {
                    "user_name": game_config.get("user_name", "林凯"),
                    "user_place": game_config.get("user_place", "linkai_room"),
                    "init_time": game_config.get("init_time", "2024-01-15 07:00")
                }
            }
            
            return {
                "success": True,
                "data": story_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取故事信息失败: {str(e)}"
            } 