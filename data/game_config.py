# 游戏配置文件
# 用于集中管理玩家角色名称和初始地点等全局设置

def get_user_name():
    """从配置文件获取用户姓名"""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))
        from utils.config_loader import get_user_name as get_config_user_name
        return get_config_user_name()
    except ImportError:
        return "林凯"  # 默认值

PLAYER_NAME = get_user_name()  # 从配置文件获取玩家角色名称
PLAYER_ROOM_NAME = f"{PLAYER_NAME}的房间"  # 玩家房间中文名
PLAYER_ROOM_EN_NAME = "user_room"  # 玩家房间英文key
