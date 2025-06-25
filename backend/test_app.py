#!/usr/bin/env python3
"""
测试应用启动脚本
"""
import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.services.game_service import GameService
    print("✅ GameService导入成功")
    
    # 测试创建GameService实例
    game_service = GameService()
    print("✅ GameService实例创建成功")
    
    # 测试初始化游戏
    result = game_service.initialize_game("test_session")
    print("✅ 游戏初始化成功")
    print(f"📍 初始位置: {result.get('player_location')}")
    print(f"⏰ 初始时间: {result.get('current_time')}")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc() 