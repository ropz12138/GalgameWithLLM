#!/usr/bin/env python3
"""
测试配置加载功能
"""
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config_loader import get_user_name, get_user_place, get_init_time, get_game_config

def test_config_loading():
    """测试配置加载功能"""
    print("🔧 测试配置加载功能")
    print("=" * 50)
    
    try:
        # 测试获取游戏配置
        game_config = get_game_config()
        print(f"✅ 游戏配置: {game_config}")
        
        # 测试获取用户姓名
        user_name = get_user_name()
        print(f"✅ 用户姓名: {user_name}")
        
        # 测试获取用户初始位置
        user_place = get_user_place()
        print(f"✅ 用户初始位置: {user_place}")
        
        # 测试获取初始时间
        init_time = get_init_time()
        print(f"✅ 游戏初始时间: {init_time}")
        
        print("\n🎯 配置加载测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 配置加载测试失败: {e}")
        return False

if __name__ == "__main__":
    test_config_loading() 