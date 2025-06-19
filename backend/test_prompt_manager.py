#!/usr/bin/env python3
"""
测试提示词管理系统
"""
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.prompts.prompt_manager import prompt_manager
from src.prompts.prompt_templates import PromptTemplates

def test_prompt_manager():
    """测试提示词管理器"""
    print("🔧 测试提示词管理系统")
    print("=" * 50)
    
    try:
        # 1. 测试模板加载
        print("\n1️⃣ 测试模板加载...")
        templates = prompt_manager.list_templates()
        print(f"✅ 已加载模板: {templates}")
        
        # 2. 测试模板信息获取
        print("\n2️⃣ 测试模板信息获取...")
        for template_name in templates:
            info = prompt_manager.get_template_info(template_name)
            if info:
                print(f"📋 {template_name}: {info['description']} (v{info['version']})")
        
        # 3. 测试提示词渲染
        print("\n3️⃣ 测试提示词渲染...")
        
        # 测试行动路由器提示词
        action_prompt = prompt_manager.render_prompt('action_router',
                                                   player_location="林凯房间",
                                                   current_time="07:00",
                                                   player_personality="普通")
        print(f"✅ 行动路由器提示词长度: {len(action_prompt)} 字符")
        
        # 测试五感反馈提示词
        sensory_prompt = prompt_manager.render_prompt('sensory_feedback',
                                                     location_name="林凯房间",
                                                     location_description="典型的理工男的房间",
                                                     current_time="07:00",
                                                     npc_info="无",
                                                     action="起床")
        print(f"✅ 五感反馈提示词长度: {len(sensory_prompt)} 字符")
        
        # 4. 测试使用历史
        print("\n4️⃣ 测试使用历史...")
        history = prompt_manager.get_prompt_history()
        print(f"✅ 提示词使用历史记录数: {len(history)}")
        
        # 5. 测试PromptTemplates类
        print("\n5️⃣ 测试PromptTemplates类...")
        
        # 测试获取行动路由器提示词
        action_prompt_v2 = PromptTemplates.get_action_router_prompt(
            player_location="林凯房间",
            current_time="07:00",
            player_personality="普通"
        )
        print(f"✅ PromptTemplates行动路由器提示词长度: {len(action_prompt_v2)} 字符")
        
        # 测试获取五感反馈提示词
        sensory_prompt_v2 = PromptTemplates.get_sensory_feedback_prompt(
            location_name="林凯房间",
            location_description="典型的理工男的房间",
            current_time="07:00",
            npc_info="无",
            action="起床"
        )
        print(f"✅ PromptTemplates五感反馈提示词长度: {len(sensory_prompt_v2)} 字符")
        
        print("\n🎯 提示词管理系统测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 提示词管理系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_prompt_manager() 