#!/usr/bin/env python3
"""
测试NPC位置计算和显示的调试脚本
"""
import sys
import os
import requests
import json

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_npc_location_debug():
    """测试NPC位置计算和显示"""
    print("🔧 测试NPC位置计算和显示")
    print("=" * 50)
    
    base_url = "http://localhost:8001/api"
    
    try:
        # 1. 获取初始游戏状态
        print("\n1️⃣ 获取初始游戏状态...")
        response = requests.get(f"{base_url}/game_state")
        if response.status_code == 200:
            game_state = response.json()
            print(f"✅ 初始游戏状态:")
            print(f"  - 玩家位置: {game_state.get('player_location')}")
            print(f"  - 当前时间: {game_state.get('current_time')}")
            print(f"  - 当前地点NPC: {[npc['name'] for npc in game_state.get('npcs_at_current_location', [])]}")
        else:
            print(f"❌ 获取游戏状态失败: {response.status_code}")
            return
        
        # 2. 获取控制台NPC状态信息
        print("\n2️⃣ 获取控制台NPC状态信息...")
        response = requests.get(f"{base_url}/debug/npc_status")
        if response.status_code == 200:
            npc_status = response.json()
            print(f"✅ 控制台NPC状态:")
            print(f"  - 当前时间: {npc_status.get('current_time')}")
            print(f"  - 玩家位置: {npc_status.get('player_location')}")
            print(f"  - 玩家位置NPC: {[npc['name'] for npc in npc_status.get('npcs_at_player_location', [])]}")
            print(f"  - 所有NPC位置: {npc_status.get('npc_locations', {})}")
        else:
            print(f"❌ 获取NPC状态失败: {response.status_code}")
            return
        
        # 3. 模拟林若曦修改计划表的场景
        print("\n3️⃣ 模拟林若曦修改计划表...")
        # 这里可以添加一个API调用来修改林若曦的计划表
        # 暂时只是打印信息
        
        # 4. 再次获取游戏状态
        print("\n4️⃣ 再次获取游戏状态...")
        response = requests.get(f"{base_url}/game_state")
        if response.status_code == 200:
            game_state_after = response.json()
            print(f"✅ 修改后游戏状态:")
            print(f"  - 玩家位置: {game_state_after.get('player_location')}")
            print(f"  - 当前时间: {game_state_after.get('current_time')}")
            print(f"  - 当前地点NPC: {[npc['name'] for npc in game_state_after.get('npcs_at_current_location', [])]}")
        else:
            print(f"❌ 获取游戏状态失败: {response.status_code}")
            return
        
        # 5. 再次获取控制台NPC状态信息
        print("\n5️⃣ 再次获取控制台NPC状态信息...")
        response = requests.get(f"{base_url}/debug/npc_status")
        if response.status_code == 200:
            npc_status_after = response.json()
            print(f"✅ 修改后控制台NPC状态:")
            print(f"  - 当前时间: {npc_status_after.get('current_time')}")
            print(f"  - 玩家位置: {npc_status_after.get('player_location')}")
            print(f"  - 玩家位置NPC: {[npc['name'] for npc in npc_status_after.get('npcs_at_player_location', [])]}")
            print(f"  - 所有NPC位置: {npc_status_after.get('npc_locations', {})}")
        else:
            print(f"❌ 获取NPC状态失败: {response.status_code}")
            return
        
        # 6. 对比结果
        print("\n6️⃣ 对比结果...")
        initial_npcs = [npc['name'] for npc in game_state.get('npcs_at_current_location', [])]
        console_npcs = [npc['name'] for npc in npc_status.get('npcs_at_player_location', [])]
        
        print(f"  - 页面显示的NPC: {initial_npcs}")
        print(f"  - 控制台显示的NPC: {console_npcs}")
        
        if set(initial_npcs) != set(console_npcs):
            print(f"❌ 发现差异!")
            print(f"  - 页面有但控制台没有: {set(initial_npcs) - set(console_npcs)}")
            print(f"  - 控制台有但页面没有: {set(console_npcs) - set(initial_npcs)}")
        else:
            print(f"✅ 页面和控制台显示的NPC一致")
        
        print("\n🎯 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_npc_location_debug() 