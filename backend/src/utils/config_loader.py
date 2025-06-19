"""
配置加载工具
"""
import json
import os
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """
    加载配置文件
    
    Returns:
        配置字典
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"配置文件未找到: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"配置文件格式错误: {e}")
        return {}


def get_game_config() -> Dict[str, Any]:
    """
    获取游戏配置
    
    Returns:
        游戏配置字典
    """
    config = load_config()
    return config.get('game_config', {})


def get_user_name() -> str:
    """
    获取用户姓名
    
    Returns:
        用户姓名
    """
    game_config = get_game_config()
    return game_config.get('user_name', '林凯')


def get_user_place() -> str:
    """
    获取用户初始位置
    
    Returns:
        用户初始位置
    """
    game_config = get_game_config()
    return game_config.get('user_place', 'linkai_room')


def get_init_time() -> str:
    """
    获取游戏初始时间
    
    Returns:
        游戏初始时间
    """
    game_config = get_game_config()
    return game_config.get('init_time', '07:00') 