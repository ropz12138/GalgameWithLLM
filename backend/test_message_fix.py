#!/usr/bin/env python3
"""
测试消息重复问题修复
"""
import asyncio
import sys
import os

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(SCRIPT_DIR, "src")
sys.path.append(SRC_DIR)

from langgraph_refactor.workflow import execute_game_action, get_game_state


async def test_message_fix():
    """测试消息重复问题修复"""
    session_id = "test_message_fix"
    
    print("🧪 开始测试消息重复问题修复")
    print("=" * 50)
    
    # 测试1：执行第一个行动
    print("\n📝 测试1：执行第一个行动")
    result1 = await execute_game_action("前往客厅", session_id)
    messages1 = result1.get("state", {}).get("messages", [])
    print(f"  消息数量: {len(messages1)}")
    for i, msg in enumerate(messages1):
        speaker = msg.get("speaker", "")
        message = msg.get("message", "")[:30]
        print(f"    {i+1}. {speaker}: {message}...")
    
    # 测试2：执行第二个行动
    print("\n📝 测试2：执行第二个行动")
    result2 = await execute_game_action("和林若曦说话：你好", session_id)
    messages2 = result2.get("state", {}).get("messages", [])
    print(f"  消息数量: {len(messages2)}")
    for i, msg in enumerate(messages2):
        speaker = msg.get("speaker", "")
        message = msg.get("message", "")[:30]
        print(f"    {i+1}. {speaker}: {message}...")
    
    # 测试3：执行第三个行动
    print("\n📝 测试3：执行第三个行动")
    result3 = await execute_game_action("回我房间", session_id)
    messages3 = result3.get("state", {}).get("messages", [])
    print(f"  消息数量: {len(messages3)}")
    for i, msg in enumerate(messages3):
        speaker = msg.get("speaker", "")
        message = msg.get("message", "")[:30]
        print(f"    {i+1}. {speaker}: {message}...")
    
    # 检查是否有重复消息
    print("\n🔍 检查消息重复情况:")
    all_messages = []
    for msg in messages3:
        msg_key = f"{msg.get('speaker', '')}: {msg.get('message', '')}"
        all_messages.append(msg_key)
    
    unique_messages = list(set(all_messages))
    print(f"  总消息数: {len(all_messages)}")
    print(f"  唯一消息数: {len(unique_messages)}")
    
    if len(all_messages) == len(unique_messages):
        print("  ✅ 没有发现重复消息")
    else:
        print("  ❌ 发现重复消息")
        duplicates = [msg for msg in all_messages if all_messages.count(msg) > 1]
        print(f"  重复消息: {duplicates}")
    
    print("\n" + "=" * 50)
    print("🧪 测试完成")


if __name__ == "__main__":
    asyncio.run(test_message_fix()) 