"""
LangGraph核心节点实现
"""
import sys
import os
import re
import json
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(os.path.dirname(SRC_DIR))
sys.path.append(PROJECT_ROOT)
sys.path.append(SRC_DIR)

from langgraph_refactor.game_state import GameState, create_message, create_game_event
from services.llm_service import LLMService
from data.locations import all_locations_data, location_connections, location_name_map
from data.characters import all_actresses

# 创建LLM服务实例
llm_service = LLMService()


class SubAction(BaseModel):
    """子行动的结构化定义"""
    type: Literal["move", "talk", "explore", "general"] = Field(
        description="子行动类型"
    )
    action: str = Field(description="具体行动描述")


class ActionRouter(BaseModel):
    """行动路由器的结构化输出"""
    action_type: Literal["move", "talk", "explore", "general", "compound"] = Field(
        description="玩家行动类型：move(移动), talk(对话), explore(探索), general(其他), compound(复合指令)"
    )
    confidence: float = Field(description="判断置信度，0-1之间")
    reason: str = Field(description="判断理由")
    sub_actions: Optional[List[SubAction]] = Field(
        default=None,
        description="复合指令的子行动列表"
    )


def supervisor_node(state: GameState) -> Dict[str, Any]:
    """
    督导节点 - 分析玩家输入并路由到相应处理节点
    """
    print(f"\n🎯 执行节点: supervisor_node")
    print(f"📍 节点位置: Graph入口节点 (路由决策)")
    print(f"🔄 当前行动: {state.get('current_action', '无')}")
    
    llm = llm_service.get_llm_instance()
    
    # 更新NPC位置（基于时间）
    print(f"⏰ 更新NPC位置 (当前时间: {state['current_time']})")
    updated_npc_locations = update_npc_locations_by_time(state["current_time"], state)
    print(f"  📍 更新后NPC位置: {updated_npc_locations}")
    
    # 如果没有当前行动，只更新NPC位置后直接结束
    if not state.get("current_action", "").strip():
        print(f"  ⚠️  无行动输入，直接结束")
        return {
            "next_node": None,
            "npc_locations": updated_npc_locations
        }
    
    # 构建系统提示
    system_prompt = f"""
你是一个游戏主控制器，需要分析玩家的行动并决定如何处理。

当前游戏状态：
- 玩家位置：{state["player_location"]}
- 游戏时间：{state["current_time"]}
- 玩家性格：{state["player_personality"]}

可用的行动类型：
1. move - 玩家想要移动到其他地点
2. talk - 玩家想要与NPC对话  
3. explore - 玩家想要探索当前环境或进行其他行动
4. general - 无法明确分类的行动
5. compound - 复合指令（包含多个连续行动）

【重要判断规则】
1. **对话优先原则**：如果输入以"和XXX说话："、"对XXX说："等格式开头，无论对话内容提到什么行动，都应该识别为单纯的"talk"类型，而不是复合指令。

2. **复合指令识别**：只有当玩家明确表达要执行多个独立行动时（通常用逗号、然后、接着等连接词分隔），才识别为compound类型。

【示例对比】
❌ 错误识别为复合指令：
- "和林若曦说话：我要去卫生间洗漱" → 这是单纯的talk，不是compound
- "告诉张雨晴：我先走了，明天见" → 这是单纯的talk，不是compound

✅ 正确识别为复合指令：
- "起床，去卫生间洗漱" → 这是compound（没有对话格式，有多个独立行动）
- "和林若曦告别，然后去客厅" → 这是compound（先对话，再移动）

✅ 正确识别为单纯对话：
- "和林若曦说话：早啊老姐" → talk类型
- "对张雨晴说：我去刷牙了" → talk类型
- "告诉林若曦：（揉揉眼睛）那你自己打着吧，我去刷牙洗脸" → talk类型

【复合指令格式】（仅在确认为compound时使用）
{{
  "action_type": "compound",
  "sub_actions": [
    {{"type": "action_type", "action": "具体行动描述"}}
  ]
}}

请仔细分析玩家的行动意图，优先考虑是否为对话类型。
"""
    
    user_input = f"玩家行动：{state['current_action']}"
    
    print(f"\n🤖 LLM调用 - supervisor_node路由决策")
    print(f"📤 输入 (System):")
    print(f"  {system_prompt[:200]}...")
    print(f"📤 输入 (Human): {user_input}")
    
    # 使用LLM进行路由决策
    router = llm.with_structured_output(ActionRouter)
    try:
        result = router.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ])
        
        print(f"📥 LLM输出:")
        print(f"  🎯 行动类型: {result.action_type}")
        print(f"  📊 置信度: {result.confidence}")
        print(f"  💭 判断理由: {result.reason}")
        
        # 处理复合指令
        if result.action_type == "compound" and result.sub_actions:
            print(f"  🔀 复合指令，包含{len(result.sub_actions)}个子行动:")
            for i, sub_action in enumerate(result.sub_actions):
                # 适配新的SubAction对象结构
                if hasattr(sub_action, 'type') and hasattr(sub_action, 'action'):
                    action_type = sub_action.type
                    action_text = sub_action.action
                else:
                    action_type = sub_action.get('type', 'unknown')
                    action_text = sub_action.get('action', '')
                print(f"    {i+1}. {action_type}: {action_text}")
            
            # 返回复合指令处理结果
            return {
                "next_node": "compound_handler",
                "npc_locations": updated_npc_locations,
                "messages": [create_message("玩家", state["current_action"])],
                "compound_actions": result.sub_actions,  # 存储子行动列表
                "game_events": [create_game_event(
                    "compound_route_decision",
                    action_type=result.action_type,
                    confidence=result.confidence,
                    reason=result.reason,
                    sub_actions_count=len(result.sub_actions)
                )]
            }
        
        # 处理单一指令
        next_node_map = {
            "move": "move_handler",
            "talk": "dialogue_handler", 
            "explore": "exploration_handler",
            "general": "general_handler"
        }
        
        next_node = next_node_map.get(result.action_type, "general_handler")
        
        print(f"  ➡️  路由到节点: {next_node}")
        
        return {
            "next_node": next_node,
            "npc_locations": updated_npc_locations,
            "messages": [create_message("玩家", state["current_action"])],
            "game_events": [create_game_event(
                "route_decision",
                action_type=result.action_type,
                confidence=result.confidence,
                reason=result.reason
            )]
        }
        
    except Exception as e:
        print(f"❌ LLM调用失败: {e}")
        print(f"  ➡️  降级到节点: general_handler")
        return {
            "next_node": "general_handler",
            "npc_locations": updated_npc_locations,
            "messages": [create_message("系统", "处理出现问题，将使用通用处理方式", "error")]
        }


def move_handler_node(state: GameState) -> Dict[str, Any]:
    """
    移动处理节点
    """
    print(f"\n🎯 执行节点: move_handler_node")
    print(f"📍 节点位置: 移动处理分支")
    
    current_location = state["player_location"]
    action = state["current_action"]
    
    print(f"🚶 处理移动: {action}")
    print(f"📍 当前位置: {current_location}")
    
    # 🆕 获取所有地点信息（不仅仅是直接可达的）
    all_location_info = []
    for loc_key, loc_data in all_locations_data.items():
        all_location_info.append({
            "key": loc_key, 
            "name": loc_data["name"],
            "is_directly_reachable": loc_key in location_connections.get(current_location, [])
        })
    
    # 构造LLM prompt
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.messages import SystemMessage, HumanMessage
    llm = llm_service.get_llm_instance()
    
    # 获取玩家身份信息
    from data.game_config import PLAYER_NAME
    player_name = PLAYER_NAME
    
    system_prompt = f"""
你是一个游戏世界的行动解析器。

【玩家信息】
玩家姓名：{player_name}
当前位置：{all_locations_data.get(current_location, {}).get('name', current_location)}

【所有地点】
{all_location_info}

【解析规则】
请根据玩家输入，判断玩家想去哪个地点。可以选择任何存在的地点，即使不能直接到达。
注意理解玩家的指代：
- "我的房间" = "{player_name}房间"
- "回家"、"回房间" = "{player_name}房间"
- "我家" = "{player_name}房间"

如果无法判断，请destination_key返回空字符串。
严格返回如下JSON格式：
{{
  "destination_key": "xxx",
  "destination_name": "xxx",
  "reason": "xxx"
}}
"""
    user_input = f"玩家输入：{action}"
    parser = JsonOutputParser()
    try:
        response = parser.invoke(llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]))
        print(f"📥 LLM判定目标地点: {response}")
    except Exception as e:
        print(f"❌ LLM判定目标地点失败: {e}")
        return {
            "messages": [create_message("系统", "无法理解你要去哪里，请明确指定目标地点。")]
        }
    
    dest_key = response.get("destination_key", "")
    dest_name = response.get("destination_name", "")
    reason = response.get("reason", "")
    
    # 校验目标地点
    if not dest_key or dest_key not in all_locations_data:
        print(f"❌ LLM返回的目标地点无效: {dest_key}")
        return {
            "messages": [create_message("系统", f"无法理解你要去哪里，请明确指定目标地点。\nLLM解析理由：{reason}")]
        }
    
    # 检查是否已在目标地点
    norm_current = location_name_map.get(current_location, current_location)
    if dest_key == norm_current:
        dest_cn = all_locations_data[dest_key]['name']
        print(f"⚠️  已在目标地点: {dest_cn}")
        return {
            "messages": [create_message("系统", f"您已经在 {dest_cn} 了。")]
        }
    
    # 🆕 路径规划 - 检查是否能直接到达，如果不能则规划路径
    available_destinations = location_connections.get(current_location, [])
    
    if dest_key in available_destinations:
        # 可以直接到达
        print(f"✅ 可直接到达目标地点")
        dest_cn = all_locations_data[dest_key]['name']
        desc = all_locations_data[dest_key].get('description', '')
        
        # 计算移动耗时
        time_cost = calculate_move_time(current_location, dest_key, state["player_personality"])
        new_time = advance_game_time(state["current_time"], time_cost)
        
        print(f"✅ 移动成功:")
        print(f"  目标: {dest_cn}")
        print(f"  耗时: {time_cost}分钟")
        print(f"  新时间: {new_time}")
        
        return {
            "player_location": dest_key,
            "current_time": new_time,
            "messages": [create_message("系统", f"您成功移动到了 {dest_cn}。{desc}")],
            "game_events": [create_game_event(
                "player_move",
                from_location=current_location,
                to_location=dest_key,
                time_cost=time_cost
            )]
        }
    else:
        # 🆕 需要路径规划
        print(f"🗺️  目标地点无法直接到达，开始路径规划")
        
        # 查找路径
        path = find_path_to_destination(current_location, dest_key, location_connections)
        
        if not path:
            # 无法到达
            dest_cn = all_locations_data[dest_key]['name']
            print(f"❌ 无法到达目标地点: {dest_cn}")
            return {
                "messages": [create_message("系统", f"无法找到前往 {dest_cn} 的路径。")]
            }
        
        # 🆕 将路径转换为复合移动任务
        movement_subtasks = create_movement_subtasks(path)
        dest_cn = all_locations_data[dest_key]['name']
        
        print(f"🔀 创建多步移动任务到 {dest_cn}")
        
        # 返回复合任务，让复合处理节点执行
        # 将字典转换为SubAction对象（SubAction已在文件顶部定义）
        sub_actions = [
            SubAction(type="move", action=task["action"])
            for task in movement_subtasks
        ]
        
        return {
            "compound_actions": sub_actions,
            "messages": [create_message("系统", f"需要经过{len(path)}步才能到达 {dest_cn}，开始移动...")],
            "game_events": [create_game_event(
                "multi_step_move_planned",
                target_location=dest_key,
                path=path,
                total_steps=len(path)
            )]
        }


def dialogue_handler_node(state: GameState) -> Dict[str, Any]:
    """
    对话处理节点
    """
    print(f"\n🎯 执行节点: dialogue_handler_node")
    print(f"📍 节点位置: 对话处理分支")
    
    action = state["current_action"]
    player_location = state["player_location"]
    current_time = state["current_time"]
    
    print(f"🗣️  处理对话: {action}")
    print(f"📍 当前位置: {player_location}")
    
    # 解析对话信息
    npc_name, message = extract_dialogue_info(action)
    
    if not npc_name or not message:
        print(f"❌ 对话解析失败 - NPC: {npc_name}, 消息: {message}")
        return {
            "messages": [create_message("系统", "请明确指定要与谁对话以及说什么内容。")]
        }
    
    print(f"✅ 对话解析成功 - 目标NPC: {npc_name}, 消息: {message}")
    
    # 检查NPC是否在当前位置
    current_npcs = get_npcs_at_location(player_location, state["npc_locations"], current_time)
    npc_names = [npc["name"] for npc in current_npcs]
    
    print(f"📍 当前位置NPC: {npc_names}")
    
    if npc_name not in npc_names:
        print(f"❌ NPC不在当前位置: {npc_name}")
        return {
            "messages": [create_message(
                "系统", 
                f"{npc_name} 不在当前位置。当前位置的NPC有：{', '.join(npc_names) if npc_names else '无'}"
            )]
        }
    
    # 获取NPC信息
    npc_obj = next((a for a in all_actresses if a['name'] == npc_name), None)
    if not npc_obj:
        print(f"❌ 未找到NPC数据: {npc_name}")
        return {
            "messages": [create_message("系统", f"未找到NPC：{npc_name}")]
        }
    
    print(f"✅ 找到NPC: {npc_obj['name']}, 性格: {npc_obj['personality']}")
    
    # 获取对话历史
    dialogue_history = state["npc_dialogue_histories"].get(npc_name, [])
    print(f"📚 对话历史长度: {len(dialogue_history)}")
    
    # 生成NPC回复
    print(f"\n🤖 LLM调用 - NPC回复生成")
    npc_reply = generate_npc_reply(npc_obj, message, dialogue_history, state)
    print(f"📥 NPC回复: {npc_reply}")
    
    # 更新对话历史
    updated_history = dialogue_history + [
        {"speaker": "玩家", "message": message, "timestamp": current_time},
        {"speaker": npc_name, "message": npc_reply, "timestamp": current_time}
    ]
    
    # 计算对话耗时
    time_cost = calculate_dialogue_time(message, state["player_personality"])
    new_time = advance_game_time(current_time, time_cost)
    
    print(f"⏰ 对话耗时: {time_cost}分钟, 新时间: {new_time}")
    
    # 🆕 智能计划分析和重新制定
    print(f"\n🧠 智能计划分析 - 检查是否需要重新制定计划")
    plan_changes = analyze_dialogue_for_plan_changes(npc_obj, message, npc_reply, new_time, state)
    
    updated_npc_locations = state.get("npc_locations", {}).copy()
    updated_npc_locations.update(plan_changes.get("npc_location_updates", {}))
    
    # 生成对话后的五感反馈
    print(f"\n🤖 LLM调用 - 对话后五感反馈生成")
    dialogue_action = f"与{npc_name}对话：{message}"
    sensory_feedback = generate_exploration_feedback(
        dialogue_action, 
        all_locations_data.get(player_location, {}), 
        current_npcs, 
        new_time, 
        state["player_personality"]
    )
    print(f"📥 五感反馈: {sensory_feedback}")
    
    # 构建返回结果
    result = {
        "current_time": new_time,
        "messages": [
            create_message(npc_name, npc_reply),
            create_message("系统", sensory_feedback)  # 添加五感反馈消息
        ],
        "npc_dialogue_histories": {npc_name: updated_history},
        "npc_locations": updated_npc_locations,  # 更新NPC位置
        "game_events": [create_game_event(
            "dialogue",
            npc_name=npc_name,
            player_message=message,
            npc_reply=npc_reply,
            time_cost=time_cost
        )]
    }
    
    # 添加计划变更事件和心情变化
    if plan_changes.get("schedule_changed", False) or plan_changes.get("mood_changed", False):
        result["game_events"].extend(plan_changes.get("events", []))
        result["messages"].extend(plan_changes.get("system_messages", []))
        
        # 如果有心情变化，添加到状态更新中
        if plan_changes.get("mood_changed", False):
            npc_mood_updates = plan_changes.get("npc_mood_updates", {})
            if npc_mood_updates:
                # 获取当前游戏状态中的心情字典，并更新
                current_moods = state.get("npc_moods", {}).copy()
                current_moods.update(npc_mood_updates)
                result["npc_moods"] = current_moods
        
        # 如果有NPC动态数据更新，添加到状态中
        if plan_changes.get("npc_dynamic_updates"):
            result["npc_dynamic_data"] = plan_changes["npc_dynamic_updates"]
    
    return result


def exploration_handler_node(state: GameState) -> Dict[str, Any]:
    """
    探索处理节点
    """
    print(f"\n🎯 执行节点: exploration_handler_node")
    print(f"📍 节点位置: 探索处理分支")
    
    action = state["current_action"]
    player_location = state["player_location"]
    current_time = state["current_time"]
    
    print(f"🔍 处理探索: {action}")
    print(f"📍 当前位置: {player_location}")
    
    # 获取当前地点详情
    location_info = all_locations_data.get(player_location, {})
    
    # 获取当前地点的NPC
    current_npcs = get_npcs_at_location(player_location, state["npc_locations"], current_time)
    print(f"👥 当前地点NPC: {[npc['name'] for npc in current_npcs]}")
    
    # 生成探索反馈
    print(f"\n🤖 LLM调用 - 探索反馈生成")
    sensory_feedback = generate_exploration_feedback(
        action, location_info, current_npcs, current_time, state["player_personality"]
    )
    print(f"📥 探索反馈: {sensory_feedback}")
    
    # 计算探索耗时
    time_cost = calculate_exploration_time(action, state["player_personality"])
    new_time = advance_game_time(current_time, time_cost)
    
    print(f"⏰ 探索耗时: {time_cost}分钟, 新时间: {new_time}")
    
    return {
        "current_time": new_time,
        "messages": [create_message("系统", sensory_feedback)],
        "game_events": [create_game_event(
            "exploration",
            action=action,
            location=player_location,
            time_cost=time_cost
        )]
    }


def general_handler_node(state: GameState) -> Dict[str, Any]:
    """
    通用处理节点
    """
    print(f"\n🎯 执行节点: general_handler_node")
    print(f"📍 节点位置: 通用处理分支 (默认处理)")
    
    action = state["current_action"]
    
    print(f"🔧 通用处理: {action}")
    
    # 使用LLM生成通用响应
    llm = llm_service.get_llm_instance()
    
    system_prompt = f"""
你是游戏世界的叙述者。玩家在游戏中进行了一个行动，请根据当前情况给出合适的反馈。

当前状态：
- 玩家位置：{state["player_location"]}
- 游戏时间：{state["current_time"]}
- 玩家性格：{state["player_personality"]}

请简洁地描述这个行动的结果，保持游戏的沉浸感。
"""
    
    user_input = f"玩家行动：{action}"
    
    print(f"\n🤖 LLM调用 - 通用响应生成")
    print(f"📤 输入 (System): 游戏世界叙述者提示...")
    print(f"📤 输入 (Human): {user_input}")
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ])
        
        content = response.content
        print(f"📥 LLM输出: {content}")
        
    except Exception as e:
        content = f"您{action}。"
        print(f"❌ LLM调用失败: {e}")
        print(f"📥 降级输出: {content}")
    
    # 计算行动耗时
    time_cost = calculate_general_action_time(action, state["player_personality"])
    new_time = advance_game_time(state["current_time"], time_cost)
    
    print(f"⏰ 行动耗时: {time_cost}分钟, 新时间: {new_time}")
    
    # 生成行动后的五感反馈
    print(f"\n🤖 LLM调用 - 行动后五感反馈生成")
    sensory_feedback = generate_exploration_feedback(
        action, 
        all_locations_data.get(state["player_location"], {}), 
        get_npcs_at_location(state["player_location"], state["npc_locations"], new_time), 
        new_time, 
        state["player_personality"]
    )
    print(f"📥 五感反馈: {sensory_feedback}")
    
    return {
        "current_time": new_time,
        "messages": [create_message("系统", sensory_feedback)],  # 使用五感反馈替换原来的content
        "game_events": [create_game_event(
            "general_action",
            action=action,
            time_cost=time_cost
        )]
    }


# 辅助函数
def update_npc_locations_by_time(current_time: str, state: GameState = None) -> Dict[str, str]:
    """根据时间更新NPC位置"""
    from datetime import datetime
    
    npc_locations = {}
    current_time_obj = datetime.strptime(current_time, "%H:%M").time()
    
    for actress in all_actresses:
        location, _ = get_npc_current_location_and_event(actress["name"], current_time_obj, state)
        npc_locations[actress["name"]] = location
    
    return npc_locations


def get_npc_current_location_and_event(npc_name: str, current_time_obj, state: GameState = None):
    """获取NPC当前位置和事件"""
    from datetime import datetime
    
    print(f"🔍 【调试】获取{npc_name}的位置和事件")
    print(f"🔍 【调试】当前时间: {current_time_obj}")
    
    # 优先从游戏状态中获取动态更新的NPC数据
    npc_data = None
    if state and "npc_dynamic_data" in state:
        npc_data = state["npc_dynamic_data"].get(npc_name)
        print(f"🔍 【调试】从动态数据获取{npc_name}的数据: {npc_data is not None}")
    
    # 如果没有动态数据，回退到静态数据
    if not npc_data:
        npc_data = next((actress for actress in all_actresses if actress["name"] == npc_name), None)
        print(f"🔍 【调试】从静态数据获取{npc_name}的数据: {npc_data is not None}")
    
    if not npc_data:
        print(f"❌ 【调试】未找到{npc_name}的数据")
        return "未知地点", "未知活动"
    
    print(f"🔍 【调试】{npc_name}的计划表: {npc_data.get('schedule', [])}")
    
    for event_info in npc_data.get("schedule", []):
        try:
            start_time = datetime.strptime(event_info["start_time"], "%H:%M").time()
            end_time = datetime.strptime(event_info["end_time"], "%H:%M").time()
            
            print(f"🔍 【调试】检查计划: {event_info['start_time']}-{event_info['end_time']} 在{event_info['location']}：{event_info['event']}")
            print(f"🔍 【调试】时间匹配: {start_time} <= {current_time_obj} < {end_time} = {start_time <= current_time_obj < end_time}")
            
            if start_time <= current_time_obj < end_time:
                location = location_name_map.get(event_info["location"], event_info["location"])
                print(f"✅ 【调试】匹配成功! 地点映射: {event_info['location']} -> {location}")
                return location, event_info["event"]
        except ValueError as e:
            print(f"❌ 【调试】时间解析错误: {e}")
            continue
    
    default_location = npc_data.get("default_location", "未知地点")
    print(f"🔍 【调试】未匹配到计划，使用默认地点: {default_location}")
    return default_location, "空闲"


def get_npcs_at_location(location_name: str, npc_locations: Dict[str, str], current_time: str) -> list:
    """获取指定地点的NPC列表"""
    from datetime import datetime
    
    print(f"🔍 【NPC位置调试】查找地点: {location_name}")
    print(f"🔍 【NPC位置调试】当前时间: {current_time}")
    
    npcs_here = []
    current_time_obj = datetime.strptime(current_time, "%H:%M").time()
    
    for actress in all_actresses:
        npc_name = actress["name"]
        
        # 🔧 修复：总是根据当前时间和计划表计算NPC的准确位置
        # 而不是依赖可能过时的npc_locations状态
        npc_loc, npc_event = get_npc_current_location_and_event(npc_name, current_time_obj)
        
        print(f"🔍 【NPC位置调试】{npc_name}: 计算位置={npc_loc}, 目标位置={location_name}, 匹配={npc_loc == location_name}")
        
        if npc_loc == location_name:
            npcs_here.append({
                "name": npc_name,
                "event": npc_event,
                "personality": actress["personality"],
                "mood": actress.get("mood", "平静")
            })
    
    print(f"🔍 【NPC位置调试】最终找到的NPC: {[npc['name'] for npc in npcs_here]}")
    return npcs_here


def extract_destination_from_action(action: str) -> Optional[str]:
    """从行动文本中提取目标地点"""
    # 简单的关键词匹配，可以后续用LLM优化
    keywords = ["去", "到", "前往", "移动到", "走到"]
    
    for keyword in keywords:
        if keyword in action:
            parts = action.split(keyword)
            if len(parts) > 1:
                destination = parts[1].strip()
                # 清理标点符号
                destination = destination.replace("。", "").replace("，", "").replace("、", "")
                return destination
    
    # 如果没有关键词，检查是否直接是地点名
    for location_key, location_data in all_locations_data.items():
        if location_data["name"] in action or location_key in action:
            return location_data["name"]
    
    return None


def extract_dialogue_info(action: str) -> tuple:
    """从行动文本中提取对话信息"""
    import re
    
    print(f"🔍 解析对话输入: {action}")
    
    # 匹配模式：和XXX说话：YYY 或 和XXX说：YYY 或 对XXX说：YYY
    patterns = [
        r"和([^说]+)说话[：:](.+)",          # "和林若曦说话：早啊老姐"
        r"(?:和|对|告诉|与)([^说：]+)说[：:](.+)",   # "和林若曦说：早啊老姐"
        r"和([^对话]+)对话[：:](.+)",         # "和林若曦对话：早啊老姐"
        r"跟([^讲]+)讲[：:](.+)"              # "跟林若曦讲：早啊老姐"
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, action)
        if match:
            npc_name = match.group(1).strip()
            message = match.group(2).strip()
            print(f"✅ 匹配成功 (模式{i+1}): NPC={npc_name}, 消息={message}")
            return npc_name, message
    
    print(f"❌ 无法解析对话格式")
    return None, None


def generate_npc_reply(npc_obj: dict, message: str, dialogue_history: list, state: GameState) -> str:
    """生成NPC回复"""
    llm = llm_service.get_llm_instance()
    
    # 获取NPC详细信息
    npc_name = npc_obj["name"]
    personality = npc_obj.get("personality", "")
    background = npc_obj.get("background", "")
    relations = npc_obj.get("relations", {})
    mood = npc_obj.get("mood", "平静")
    
    # 获取NPC当前位置和活动
    from datetime import datetime
    current_time_obj = datetime.strptime(state['current_time'], "%H:%M").time()
    npc_location, npc_event = get_npc_current_location_and_event(npc_name, current_time_obj)
    
    # 构建NPC计划表信息
    npc_schedule = npc_obj.get("schedule", [])
    current_schedule_str = "；".join([
        f"{item['start_time']}-{item['end_time']} 在{item['location']}：{item['event']}" 
        for item in npc_schedule
    ])
    
    # 构建计划变更历史
    plan_change_history = npc_obj.get("plan_change_history", [])
    if plan_change_history:
        history_str = ""
        for record in plan_change_history:
            history_str += (
                f"【变更时间】{record['time']}\n"
                f"【变更原因】{record['reason']}\n"
                f"【原计划表】{record['old_schedule']}\n"
                f"【新计划表】{record['new_schedule']}\n"
            )
    else:
        # 兼容老逻辑
        original_schedule_str = npc_obj.get("original_schedule_str")
        last_fail_reason = npc_obj.get("last_fail_reason")
        if original_schedule_str and last_fail_reason:
            history_str = (
                f"【原计划表】\n{original_schedule_str}\n"
                f"【变更原因】\n{last_fail_reason}\n"
                f"【新计划表】\n{current_schedule_str}\n"
            )
        else:
            history_str = f"你的今日计划：{current_schedule_str}\n"
    
    # 构建对话历史摘要
    dialogue_summary = ""
    if dialogue_history:
        recent_dialogues = dialogue_history[-6:]  # 最近3轮对话
        dialogue_summary = "\n<最近对话历史>\n" + "\n".join([
            f"{h.get('speaker', '未知')}：{h.get('message', '')}" 
            for h in recent_dialogues
        ]) + "\n</最近对话历史>\n"
    
    # 获取当前地点详细信息
    location_details = all_locations_data.get(state["player_location"], {})
    location_description = location_details.get("description", "")
    
    # 获取其他在场NPC信息
    current_npcs = get_npcs_at_location(state["player_location"], state["npc_locations"], state["current_time"])
    other_npcs = [npc for npc in current_npcs if npc["name"] != npc_name]
    other_npcs_info = ""
    if other_npcs:
        other_npcs_info = f"\n当前还有其他NPC在场：{', '.join([npc['name'] for npc in other_npcs])}"
    
    # 玩家信息
    from data.game_config import PLAYER_NAME
    player_name = PLAYER_NAME
    player_personality = state.get("player_personality", "普通")
    
    # 构建简化的system_prompt，移除旁听相关逻辑
    system_prompt = f"""<人物设定>
你是NPC {npc_name}
性格：{personality}
背景：{background}
关系：{relations}
当前心情：{mood}
你现在所在的位置是：{npc_location}，正在进行：{npc_event}
请用第一人称、自然、贴合性格地与玩家【{player_name}】对话。括号内表述自己的神态动作。
</人物设定>

<当前对话>
玩家【{player_name}】对你说：{message}
</当前对话>

<场景信息>
当前时间：{state['current_time']}
当前位置：{location_details.get('name', state['player_location'])}
位置描述：{location_description}
{other_npcs_info}
玩家性格：{player_personality}
</场景信息>

<计划表变更情况>
{history_str}
</计划表变更情况>

{dialogue_summary}

【规则】
1. 请根据你的性格特点、当前心情、所在位置和正在进行的活动，对玩家的话做出合适的回应
2. 保持角色的一致性，回复要自然生动
3. 直接回应玩家当前对你说的话"""
    
    user_input = f"请根据上述信息，对玩家的当前对话做出回应。"
    
    print(f"  📤 LLM输入 (System):")
    print(f"    角色: {npc_name}")
    print(f"    性格: {personality}")
    print(f"    背景: {background[:50]}..." if background else "    背景: 无")
    print(f"    心情: {mood}")
    print(f"    位置: {npc_location}")
    print(f"    活动: {npc_event}")
    print(f"    场景: {state['player_location']} @ {state['current_time']}")
    print(f"    计划表长度: {len(npc_schedule)}条")
    print(f"    对话历史长度: {len(dialogue_history)}条")
    print(f"  📤 LLM输入 (Human): {user_input}")
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ])
        
        reply_content = response.content
        print(f"  📥 LLM输出: {reply_content}")
        return reply_content
        
    except Exception as e:
        error_msg = f"（{npc_obj['name']}没有回应）"
        print(f"  ❌ LLM调用失败: {e}")
        print(f"  📥 降级输出: {error_msg}")
        return error_msg


def generate_exploration_feedback(action: str, location_info: dict, current_npcs: list, current_time: str, personality: str) -> str:
    """生成探索反馈 - 输出JSON格式的五感描述"""
    llm = llm_service.get_llm_instance()
    
    # 导入JsonOutputParser
    from langchain_core.output_parsers import JsonOutputParser
    
    npc_info = ""
    if current_npcs:
        npc_descriptions = [f"{npc['name']}正在{npc['event']}" for npc in current_npcs]
        npc_info = f"这里有：{', '.join(npc_descriptions)}"
    
    system_prompt = f"""
你是一个游戏世界的感知引擎。请根据以下信息，生成玩家行为后的感知反馈：

当前场景信息:
- 玩家所在位置: {location_info.get('name', '某个地点')}
- 位置描述: {location_info.get('description', '一个普通的地方')}
- 当前时间: {current_time}
- 当前NPC: {npc_info if npc_info else '无'}

玩家行为: {action}

请从以下几个维度描述玩家的感知体验:
- 视觉: 玩家看到了什么，用最简单的语言描述视线内的人和物以及位置关系
- 听觉: 玩家听到了什么声音，禁止提供对话者的内容。可以提供环境音，比如风声，鸟叫声，虫鸣声，水流声，汽车声等。
- 嗅觉: 玩家闻到了什么气味
- 触觉: 玩家感受到的触感

要求:
1. 描述要符合场景特点
2. 要有细节和画面感
3. 要考虑场景中NPC的存在
4. 要与玩家行为产生关联
5. 用中文回复

必须严格按照以下JSON格式回复:
{{
    "vision": "你看到...",
    "hearing": "你听到...",
    "smell": "你闻到...",
    "touch": "你摸到..."
}}
"""
    
    user_input = f"玩家行动：{action}"
    
    print(f"  📤 LLM输入 (System):")
    print(f"    地点: {location_info.get('name', '某个地点')}")
    print(f"    描述: {location_info.get('description', '一个普通的地方')[:50]}...")
    print(f"    NPC: {npc_info if npc_info else '无'}")
    print(f"  📤 LLM输入 (Human): {user_input}")
    
    try:
        # 使用JsonOutputParser来解析LLM响应
        parser = JsonOutputParser()
        response = parser.invoke(llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]))
        
        print(f"  📥 LLM原始输出: {response}")
        
        # 验证JSON格式
        if isinstance(response, dict) and any(key in response for key in ['vision', 'hearing', 'smell', 'touch']):
            print(f"  ✅ JSON格式验证成功")
            import json
            return json.dumps(response, ensure_ascii=False)
        else:
            print(f"  ⚠️  JSON格式不符合要求，使用降级方案")
            raise ValueError("JSON格式不符合要求")
        
    except Exception as e:
        print(f"  ❌ LLM调用或解析失败: {e}")
        print(f"  📥 生成降级JSON反馈")
        
        # 降级方案：生成标准格式的JSON
        fallback_json = {
            "vision": f"你看到{location_info.get('name', '周围环境')}的景象",
            "hearing": "你听到周围环境的声音",
            "smell": f"你闻到{location_info.get('name', '这里')}特有的气味",
            "touch": "你感受到周围环境的质感"
        }
        import json
        return json.dumps(fallback_json, ensure_ascii=False)


def calculate_move_time(from_location: str, to_location: str, personality: str) -> int:
    """计算移动耗时（分钟）"""
    base_time = 10  # 基础移动时间10分钟
    
    # 根据性格调整
    if personality == "急躁":
        base_time = int(base_time * 0.8)
    elif personality == "慢性子":
        base_time = int(base_time * 1.2)
    
    return base_time


def calculate_dialogue_time(message: str, personality: str) -> int:
    """计算对话耗时（分钟）"""
    base_time = min(len(message) // 10 + 3, 15)  # 根据消息长度，3-15分钟
    
    # 根据性格调整
    if personality == "健谈":
        base_time = int(base_time * 1.5)
    elif personality == "内向":
        base_time = int(base_time * 0.7)
    
    return base_time


def calculate_exploration_time(action: str, personality: str) -> int:
    """计算探索耗时（分钟）"""
    base_time = 5  # 基础探索时间5分钟
    
    # 根据行动类型调整
    if any(word in action for word in ["仔细", "详细", "认真"]):
        base_time = 10
    elif any(word in action for word in ["快速", "简单", "匆忙"]):
        base_time = 3
    
    return base_time


def calculate_general_action_time(action: str, personality: str) -> int:
    """计算通用行动耗时（分钟）"""
    return 5  # 默认5分钟


def advance_game_time(current_time: str, minutes: int) -> str:
    """推进游戏时间"""
    from datetime import datetime, timedelta
    
    try:
        time_obj = datetime.strptime(current_time, "%H:%M")
        new_time = time_obj + timedelta(minutes=minutes)
        return new_time.strftime("%H:%M")
    except ValueError:
        return current_time


def analyze_dialogue_for_plan_changes(npc_obj: dict, player_message: str, npc_reply: str, current_time: str, state: GameState) -> Dict[str, Any]:
    """
    智能分析对话内容，判断是否需要重新制定NPC计划表
    """
    llm = llm_service.get_llm_instance()
    npc_name = npc_obj["name"]
    
    print(f"  🔍 分析NPC: {npc_name}")
    print(f"  💬 玩家消息: {player_message}")
    print(f"  💬 NPC回复: {npc_reply}")
    
    # 🆕 首先分析是否需要创建新地点
    location_result = analyze_dialogue_for_location_creation(npc_obj, player_message, npc_reply, current_time)
    
    # 获取当前计划表
    current_schedule = npc_obj.get("schedule", [])
    schedule_str = "；".join([
        f"{item['start_time']}-{item['end_time']} 在{item['location']}：{item['event']}" 
        for item in current_schedule
    ])
    
    # 获取当前心情
    current_mood = npc_obj.get("mood", "平静")
    
    # 获取所有可用的地点信息
    available_locations = []
    for key, location_data in all_locations_data.items():
        available_locations.append(f"{location_data['name']}({key})")
    locations_str = "、".join(available_locations)
    
    # 构建分析提示
    analysis_prompt = f"""
分析以下对话内容，判断NPC是否需要改变计划和心情：

【对话分析】
玩家【林凯】说：{player_message}
{npc_name}回复：{npc_reply}

【NPC当前信息】
姓名：{npc_name}
性格：{npc_obj.get('personality', '')}
当前时间：{current_time}
当前心情：{current_mood}
当前计划表：{schedule_str}

【地点创建情况】
{"已创建新地点：" + location_result.get("location_name", "") if location_result.get("location_created", False) else "无新地点创建"}

【重要：可用地点列表】
当前游戏中所有可用的地点（包括初始地点和动态创建的地点）：
{locations_str}

【分析要求】
请判断以下情况：
1. NPC是否同意了玩家的邀请或建议？
2. 是否涉及地点变更（如一起去某个地方）？
3. 是否需要修改后续的计划安排？
4. 如果需要跟随玩家，应该去哪个地点？
5. 对话是否影响了NPC的心情？应该变成什么心情？

【重要约束】
- target_location字段必须严格从上述可用地点列表中选择
- 只能使用地点key（括号内的英文标识），不能使用地点中文名称
- 如果对话中提到的地点不在可用列表中，请选择最相近的现有地点
- 绝对不能创建或使用不存在的地点key

【回答格式】
请严格按照以下JSON格式回答：
{{
    "needs_replan": true/false,
    "needs_follow_player": true/false,
    "target_location": "目标地点key（如果需要跟随，必须从可用地点列表中选择）",
    "reason": "分析原因",
    "new_activity": "新活动描述（如果有）",
    "mood_changed": true/false,
    "new_mood": "新心情描述（如果心情改变）",
    "mood_reason": "心情变化原因（如果心情改变）"
}}
"""
    
    print(f"  📤 LLM分析提示:")
    print(f"    对话: {player_message} -> {npc_reply}")
    print(f"    当前计划: {schedule_str}")
    print(f"    当前心情: {current_mood}")
    print(f"    地点创建: {location_result.get('location_created', False)}")
    print(f"    可用地点: {locations_str}")
    
    try:
        # 使用JsonOutputParser来解析LLM响应
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_core.messages import SystemMessage, HumanMessage
        
        parser = JsonOutputParser()
        response = parser.invoke(llm.invoke([
            SystemMessage(content=analysis_prompt),
            HumanMessage(content="请分析以上对话并返回JSON格式的结果。")
        ]))
        
        print(f"  📥 LLM分析结果: {response}")
        
        # 验证JSON格式
        if not isinstance(response, dict):
            print(f"  ⚠️  分析结果不是有效的JSON，跳过计划重制")
            return {
                "schedule_changed": False, 
                "mood_changed": False,
                "location_created": location_result.get("location_created", False)
            }
        
        needs_replan = response.get("needs_replan", False)
        needs_follow = response.get("needs_follow_player", False)
        target_location = response.get("target_location", "")
        reason = response.get("reason", "")
        new_activity = response.get("new_activity", "")
        mood_changed = response.get("mood_changed", False)
        new_mood = response.get("new_mood", "")
        mood_reason = response.get("mood_reason", "")
        
        # 验证target_location是否在可用地点列表中
        if needs_follow and target_location:
            if target_location not in all_locations_data:
                print(f"  ⚠️  LLM返回的target_location '{target_location}' 不在可用地点列表中")
                print(f"  🔧 尝试修正为最相近的地点...")
                
                # 尝试找到最相近的地点
                if "player" in target_location.lower() or "林凯" in target_location or "房间" in target_location:
                    # 如果是玩家房间，使用linkai_room
                    target_location = "linkai_room"
                    print(f"  ✅ 修正target_location为: {target_location}")
                else:
                    # 默认使用linkai_room
                    target_location = "linkai_room"
                    print(f"  ✅ 默认修正target_location为: {target_location}")
        
        result = {
            "schedule_changed": False,
            "mood_changed": False,
            "location_created": location_result.get("location_created", False),
            "npc_location_updates": {},
            "npc_mood_updates": {},
            "events": [],
            "system_messages": []
        }
        
        # 如果创建了新地点，添加系统消息
        if location_result.get("location_created", False):
            result["system_messages"].append(create_message(
                "系统",
                f"[智能地点创建] {location_result.get('result', '')}",
                "info"
            ))
            result["events"].append(create_game_event(
                "location_creation",
                location_name=location_result.get("location_name", ""),
                reason=location_result.get("reason", "")
            ))
        
        # 处理心情变化
        if mood_changed and new_mood:
            print(f"  💭 {npc_name}的心情变化: {current_mood} -> {new_mood}")
            print(f"  📝 心情变化原因: {mood_reason}")
            
            # 更新NPC心情
            npc_obj["mood"] = new_mood
            result["mood_changed"] = True
            result["npc_mood_updates"][npc_name] = new_mood
            
            result["system_messages"].append(create_message(
                "系统",
                f"{npc_name}的心情发生了变化：{mood_reason}",
                "info"
            ))
            result["events"].append(create_game_event(
                "mood_change",
                npc_name=npc_name,
                old_mood=current_mood,
                new_mood=new_mood,
                reason=mood_reason
            ))
        
        # 如果需要跟随玩家
        if needs_follow and target_location:
            print(f"  ✅ {npc_name}将跟随玩家前往: {target_location}")
            result["npc_location_updates"][npc_name] = target_location
            result["system_messages"].append(create_message(
                "系统", 
                f"{npc_name}决定跟着你一起前往目标地点。",
                "info"
            ))
            result["events"].append(create_game_event(
                "npc_follow",
                npc_name=npc_name,
                target_location=target_location,
                reason=reason
            ))
        
        # 如果需要重新制定计划
        if needs_replan:
            print(f"  🔄 开始重新制定{npc_name}的计划表")
            print(f"  📝 重制原因: {reason}")
            
            new_schedule = generate_new_npc_schedule(
                npc_obj, 
                current_time, 
                reason,
                new_activity,
                target_location
            )
            
            if new_schedule and new_schedule != current_schedule:
                # 更新NPC的计划表
                npc_obj["schedule"] = new_schedule
                
                # 将修改后的NPC数据保存到游戏状态中
                npc_dynamic_updates = {npc_name: npc_obj.copy()}
                result["npc_dynamic_updates"] = npc_dynamic_updates
                
                # 记录计划变更历史
                if "plan_change_history" not in npc_obj:
                    npc_obj["plan_change_history"] = []
                
                old_schedule_str = "；".join([
                    f"{item['start_time']}-{item['end_time']} 在{item['location']}：{item['event']}" 
                    for item in current_schedule
                ])
                
                new_schedule_str = "；".join([
                    f"{item['start_time']}-{item['end_time']} 在{item['location']}：{item['event']}" 
                    for item in new_schedule
                ])
                
                npc_obj["plan_change_history"].append({
                    "time": current_time,
                    "reason": reason,
                    "old_schedule": old_schedule_str,
                    "new_schedule": new_schedule_str
                })
                
                result["schedule_changed"] = True
                result["system_messages"].append(create_message(
                    "系统",
                    f"{npc_name}重新制定了计划表。",
                    "info"
                ))
                result["events"].append(create_game_event(
                    "schedule_replan",
                    npc_name=npc_name,
                    reason=reason,
                    old_schedule=old_schedule_str,
                    new_schedule=new_schedule_str
                ))
                
                print(f"  ✅ 计划表重制完成")
                print(f"    原计划: {old_schedule_str}")
                print(f"    新计划: {new_schedule_str}")
            else:
                print(f"  ⚠️  新计划表与当前计划表相同，跳过更新")
        
        return result
        
    except Exception as e:
        print(f"  ❌ 计划分析失败: {e}")
        return {
            "schedule_changed": False,
            "mood_changed": False,
            "location_created": location_result.get("location_created", False)
        }


def generate_new_npc_schedule(npc_obj: dict, current_time: str, reason: str, new_activity: str = "", target_location: str = "") -> List[Dict]:
    """
    根据对话内容生成新的NPC计划表
    """
    llm = llm_service.get_llm_instance()
    npc_name = npc_obj["name"]
    
    print(f"    🗓️  生成新计划表 - NPC: {npc_name}")
    
    # 获取当前计划表
    current_schedule = npc_obj.get("schedule", [])
    current_schedule_str = "；".join([
        f"{item['start_time']}-{item['end_time']} 在{item['location']}：{item['event']}" 
        for item in current_schedule
    ])
    
    # 获取可用地点信息
    from data.locations import all_locations_data
    available_locations = list(all_locations_data.keys())
    
    replan_prompt = f"""
请为NPC重新制定计划表。

【NPC信息】
姓名：{npc_name}
性格：{npc_obj.get('personality', '')}
背景：{npc_obj.get('background', '')}

【当前状态】
当前时间：{current_time}
当前计划表：{current_schedule_str}

【变更原因】
{reason}

【新活动要求】
{new_activity if new_activity else '无特殊要求'}

【目标地点】
{target_location if target_location else '无指定地点'}

【可用地点】
{', '.join(available_locations)}

【要求】
1. 重新安排{current_time}之后的所有活动
2. 考虑NPC的性格特点和背景
3. 如果有新活动要求，优先安排
4. 如果有目标地点，确保包含在计划中
5. 时间安排要合理，不要冲突

请返回JSON格式的计划表：
[
    {{
        "start_time": "HH:MM",
        "end_time": "HH:MM", 
        "location": "地点key",
        "event": "活动描述"
    }}
]
"""
    
    try:
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_core.messages import SystemMessage, HumanMessage
        
        parser = JsonOutputParser()
        response = parser.invoke(llm.invoke([
            SystemMessage(content=replan_prompt),
            HumanMessage(content="请生成新的计划表。")
        ]))
        
        print(f"    📥 LLM生成的新计划表: {response}")
        
        # 验证JSON格式
        if isinstance(response, list) and all(
            isinstance(item, dict) and 
            all(key in item for key in ["start_time", "end_time", "location", "event"])
            for item in response
        ):
            return response
        else:
            print(f"    ❌ 新计划表格式无效，保持原计划")
            return current_schedule
            
    except Exception as e:
        print(f"    ❌ 生成新计划表失败: {e}")
        return current_schedule


def create_new_location(location_description: str, location_name: str = "", connected_to: str = None) -> str:
    """
    动态创建新地点
    """
    llm = llm_service.get_llm_instance()
    from langchain_core.messages import SystemMessage, HumanMessage
    
    print(f"\n🏗️  创建新地点")
    print(f"  📝 描述: {location_description}")
    print(f"  🏷️  名称: {location_name}")
    
    from data.locations import all_locations_data, location_connections, location_name_map
    
    # 🆕 动态获取默认连接地点（第一个地点）
    if connected_to is None:
        if all_locations_data:
            default_connected_to = list(all_locations_data.keys())[0]
            print(f"  🔗 连接到: {default_connected_to} (默认：第一个地点)")
        else:
            default_connected_to = "unknown"
            print(f"  ⚠️  无可用地点，跳过连接设置")
    else:
        default_connected_to = connected_to
        print(f"  🔗 连接到: {connected_to} (指定)")
    
    try:
        # 如果没有提供名称，让LLM生成
        if not location_name.strip():
            print(f"  🤖 生成地点名称...")
            name_prompt = f"""
根据以下描述，为这个地点生成一个合适的中文名称：

描述：{location_description}

要求：
1. 名称要简洁明了（2-6个字）
2. 能够体现地点的主要功能或特色
3. 符合家庭或生活环境的设定
4. 用中文回复，只返回地点名称

示例：书房、阳台、储物间
"""
            
            name_response = llm.invoke([
                SystemMessage(content=name_prompt),
                HumanMessage(content="请生成地点名称。")
            ])
            
            location_name = name_response.content.strip()
            print(f"  ✅ 生成的地点名称: {location_name}")
        
        # 生成英文key
        print(f"  🤖 生成英文key...")
        key_prompt = f"""
为地点"{location_name}"生成一个合适的英文key：

要求：
1. 全小写字母
2. 单词间用下划线连接
3. 简洁明了
4. 能体现地点特色
5. 只返回英文key，不要其他内容

示例：study_room, balcony, storage_room
"""
        
        key_response = llm.invoke([
            SystemMessage(content=key_prompt),
            HumanMessage(content="请生成英文key。")
        ])
        
        location_key = key_response.content.strip().lower()
        print(f"  ✅ 生成的英文key: {location_key}")
        
        # 确保key的唯一性
        original_key = location_key
        counter = 1
        while location_key in all_locations_data:
            location_key = f"{original_key}_{counter}"
            counter += 1
            print(f"  ⚠️  key冲突，调整为: {location_key}")
        
        # 生成完整的地点描述
        print(f"  🤖 生成完整描述...")
        full_description_prompt = f"""
为地点"{location_name}"生成一个生动详细的描述：

基础信息：{location_description}

要求：
1. 描述要有画面感和细节
2. 包含视觉、嗅觉等感官元素
3. 符合家庭生活环境的设定
4. 长度适中（50-100字）
5. 用中文回复

参考风格：宽敞的客厅，柔软的沙发和温暖的灯光营造出舒适的氛围。茶几上散落着杂志和遥控器。
"""
        
        description_response = llm.invoke([
            SystemMessage(content=full_description_prompt),
            HumanMessage(content="请生成地点描述。")
        ])
        
        full_description = description_response.content.strip()
        print(f"  ✅ 生成的完整描述: {full_description}")
        
        # 创建新地点数据
        new_location = {
            "name": location_name,
            "en_name": location_key,
            "description": full_description
        }
        print(f"  📦 新地点数据: {new_location}")
        
        # 添加到游戏世界
        all_locations_data[location_key] = new_location
        print(f"  ✅ 已添加到游戏世界，总地点数: {len(all_locations_data)}")
        
        # 更新名称映射
        location_name_map[location_key] = location_key
        location_name_map[location_name] = location_key
        print(f"  ✅ 已更新名称映射")
        
        # 设置连接关系
        print(f"  🔗 设置连接关系...")
        if default_connected_to != "unknown" and default_connected_to in all_locations_data:
            # 双向连接
            if default_connected_to not in location_connections:
                location_connections[default_connected_to] = []
            if location_key not in location_connections[default_connected_to]:
                location_connections[default_connected_to].append(location_key)
            
            location_connections[location_key] = [default_connected_to]
            print(f"    ✅ 已建立双向连接: {location_key} <-> {default_connected_to}")
        else:
            print(f"    ⚠️  跳过连接设置：连接地点不存在或无效")
        
        result = f"成功创建新地点：{location_name}({location_key}) - {full_description}"
        print(f"  🎉 创建完成: {result}")
        
        return result
        
    except Exception as e:
        error_msg = f"创建地点失败: {str(e)}"
        print(f"  ❌ {error_msg}")
        return error_msg


def analyze_dialogue_for_location_creation(npc_obj: dict, player_message: str, npc_reply: str, current_time: str) -> Dict[str, Any]:
    """
    分析对话内容，判断是否需要创建新地点
    """
    llm = llm_service.get_llm_instance()
    npc_name = npc_obj["name"]
    
    print(f"  🏗️  分析是否需要创建新地点")
    
    # 获取现有地点信息
    from data.locations import all_locations_data
    locations_info = "、".join([f"{loc['name']}({key})" for key, loc in all_locations_data.items()])
    
    analysis_prompt = f"""
分析以下对话内容，判断是否需要创建新地点：

【对话分析】
玩家【林凯】说：{player_message}
{npc_name}回复：{npc_reply}

【NPC信息】
姓名：{npc_name}
性格：{npc_obj.get('personality', '')}
当前时间：{current_time}

【现有地点】
{locations_info}

【分析要求】
请判断：
1. 对话中是否涉及需要特定场所的活动（如吃饭、健身、学习、约会等）？
2. 现有地点是否能满足这些活动需求？
3. 如果需要新地点，这个地点应该是什么类型？

【回答格式】
请严格按照以下JSON格式回答：
{{
    "need_new_location": true/false,
    "reason": "判断原因",
    "location_description": "新地点描述（如果需要）",
    "location_name": "建议的地点名称（如果需要）",
    "activity_type": "活动类型（如果需要）"
}}
"""
    
    try:
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_core.messages import SystemMessage, HumanMessage
        
        parser = JsonOutputParser()
        response = parser.invoke(llm.invoke([
            SystemMessage(content=analysis_prompt),
            HumanMessage(content="请分析对话并返回JSON格式的结果。")
        ]))
        
        print(f"    📥 地点需求分析结果: {response}")
        
        if isinstance(response, dict) and response.get("need_new_location", False):
            location_desc = response.get("location_description", "")
            location_name = response.get("location_name", "")
            reason = response.get("reason", "")
            
            if location_desc:
                print(f"    ✅ 需要创建新地点: {location_name}")
                print(f"    📝 理由: {reason}")
                
                # 创建新地点
                # 🆕 智能分析应该连接到哪个地点
                from data.locations import all_locations_data
                available_locations = list(all_locations_data.keys())
                
                connection_prompt = f"""
根据新地点的描述和功能，选择最合适的连接地点：

【新地点信息】
名称：{location_name}
描述：{location_desc}

【可选连接地点】
{', '.join(available_locations)}

【地点详情】
{chr(10).join([f"- {key}: {loc['name']} - {loc.get('description', '')}" for key, loc in all_locations_data.items()])}

请选择一个最合理的连接地点（用英文key回答），考虑：
1. 功能相关性（如餐厅连接厨房）
2. 位置逻辑性（如卧室连接客厅）
3. 使用便利性

只返回地点的英文key，不要其他内容。
"""
                
                try:
                    connection_response = llm.invoke([
                        SystemMessage(content=connection_prompt),
                        HumanMessage(content="请选择连接地点。")
                    ])
                    
                    suggested_connection = connection_response.content.strip()
                    print(f"    🤖 LLM建议连接到: {suggested_connection}")
                    
                    # 验证建议的连接地点是否存在
                    if suggested_connection in all_locations_data:
                        result = create_new_location(location_desc, location_name, suggested_connection)
                    else:
                        print(f"    ⚠️  LLM建议的连接地点不存在，使用默认连接")
                        result = create_new_location(location_desc, location_name)
                        
                except Exception as e:
                    print(f"    ❌ LLM连接分析失败: {e}，使用默认连接")
                    result = create_new_location(location_desc, location_name)
                
                return {
                    "location_created": True,
                    "location_name": location_name,
                    "result": result,
                    "reason": reason
                }
        
        print(f"    ℹ️  无需创建新地点")
        return {"location_created": False}
        
    except Exception as e:
        print(f"    ❌ 地点需求分析失败: {e}")
        return {"location_created": False}


def find_path_to_destination(start_location: str, target_location: str, all_connections: Dict[str, List[str]]) -> List[str]:
    """
    使用BFS算法查找从起点到目标地点的最短路径
    
    Args:
        start_location: 起始地点
        target_location: 目标地点  
        all_connections: 地点连接关系字典
    
    Returns:
        List[str]: 路径列表，包含从起点到终点的所有地点（不包含起点）
                  如果无法到达则返回空列表
    """
    print(f"\n🗺️  路径规划: {start_location} -> {target_location}")
    
    # 如果起点就是终点
    if start_location == target_location:
        print(f"  ✅ 已在目标地点")
        return []
    
    # 如果可以直接到达
    if target_location in all_connections.get(start_location, []):
        print(f"  ✅ 可直接到达")
        return [target_location]
    
    # BFS搜索路径
    from collections import deque
    
    queue = deque([(start_location, [start_location])])  # (当前位置, 路径)
    visited = {start_location}
    
    while queue:
        current_location, path = queue.popleft()
        
        # 检查所有连接的地点
        for next_location in all_connections.get(current_location, []):
            if next_location == target_location:
                # 找到目标地点
                final_path = path + [target_location]
                route = final_path[1:]  # 去掉起点
                print(f"  ✅ 找到路径: {' -> '.join(final_path)}")
                print(f"  📍 移动步骤: {route}")
                return route
            
            if next_location not in visited:
                visited.add(next_location)
                queue.append((next_location, path + [next_location]))
    
    # 无法到达
    print(f"  ❌ 无法找到到达路径")
    return []


def create_movement_subtasks(path: List[str]) -> List[Dict[str, str]]:
    """
    将路径转换为移动子任务列表
    
    Args:
        path: 路径列表
    
    Returns:
        List[Dict]: 移动子任务列表
    """
    subtasks = []
    for i, location in enumerate(path):
        # 使用地点的中文名称而不是key
        location_name = all_locations_data.get(location, {}).get('name', location)
        subtasks.append({
            "type": "move",
            "action": f"前往{location_name}",
            "target_location": location,
            "step": i + 1,
            "total_steps": len(path)
        })
    
    print(f"  🔀 创建{len(subtasks)}个移动子任务:")
    for i, task in enumerate(subtasks):
        print(f"    {i+1}. {task['action']}")
    
    return subtasks


def compound_handler_node(state: GameState) -> Dict[str, Any]:
    """
    复合指令处理节点 - 依次执行多个子行动
    """
    print(f"\n🎯 执行节点: compound_handler_node")
    print(f"📍 节点位置: 复合指令处理分支")
    
    compound_actions = state.get("compound_actions", [])
    if not compound_actions:
        print(f"❌ 无复合子行动，降级处理")
        return {
            "messages": [create_message("系统", "复合指令处理出错，请重新输入。")]
        }
    
    print(f"🔀 开始处理复合指令，共{len(compound_actions)}个子行动")
    
    # 累积结果
    all_messages = []
    all_events = []
    cumulative_state = state.copy()
    
    for i, sub_action in enumerate(compound_actions):
        # 适配新的SubAction对象结构
        if hasattr(sub_action, 'type') and hasattr(sub_action, 'action'):
            # 如果是SubAction对象
            action_type = sub_action.type
            action_text = sub_action.action
        else:
            # 如果是字典（向后兼容）
            action_type = sub_action.get("type", "")
            action_text = sub_action.get("action", "")
        
        print(f"\n  📋 执行子行动 {i+1}/{len(compound_actions)}: {action_type} - {action_text}")
        
        # 更新当前子行动到状态中
        cumulative_state["current_action"] = action_text
        
        # 根据类型调用对应的处理节点
        if action_type == "move":
            result = move_handler_node(cumulative_state)
        elif action_type == "talk":
            result = dialogue_handler_node(cumulative_state)
        elif action_type == "explore":
            result = exploration_handler_node(cumulative_state)
        elif action_type == "general":
            result = general_handler_node(cumulative_state)
        else:
            print(f"    ⚠️  未知子行动类型: {action_type}，使用通用处理")
            result = general_handler_node(cumulative_state)
        
        print(f"    ✅ 子行动 {i+1} 完成")
        
        # 累积消息和事件
        sub_messages = result.get("messages", [])
        sub_events = result.get("game_events", [])
        
        all_messages.extend(sub_messages)
        all_events.extend(sub_events)
        
        # 更新累积状态（为下一个子行动准备）
        if "player_location" in result:
            cumulative_state["player_location"] = result["player_location"]
        if "current_time" in result:
            cumulative_state["current_time"] = result["current_time"]
        if "npc_locations" in result:
            cumulative_state["npc_locations"] = result["npc_locations"]
        if "npc_dialogue_histories" in result:
            if "npc_dialogue_histories" not in cumulative_state:
                cumulative_state["npc_dialogue_histories"] = {}
            cumulative_state["npc_dialogue_histories"].update(result["npc_dialogue_histories"])
        if "npc_moods" in result:
            if "npc_moods" not in cumulative_state:
                cumulative_state["npc_moods"] = {}
            cumulative_state["npc_moods"].update(result["npc_moods"])
    
    print(f"\n🎉 复合指令执行完成!")
    print(f"  📊 总消息数: {len(all_messages)}")
    print(f"  🎪 总事件数: {len(all_events)}")
    
    # 构建最终结果
    final_result = {
        "messages": all_messages,
        "game_events": all_events + [create_game_event(
            "compound_action_completed",
            total_sub_actions=len(compound_actions),
            final_location=cumulative_state.get("player_location"),
            final_time=cumulative_state.get("current_time")
        )],
        # 清理compound_actions，避免状态污染
        "compound_actions": []
    }
    
    # 添加状态更新
    if "player_location" in cumulative_state:
        final_result["player_location"] = cumulative_state["player_location"]
    if "current_time" in cumulative_state:
        final_result["current_time"] = cumulative_state["current_time"]
    if "npc_locations" in cumulative_state:
        final_result["npc_locations"] = cumulative_state["npc_locations"]
    if "npc_dialogue_histories" in cumulative_state:
        final_result["npc_dialogue_histories"] = cumulative_state["npc_dialogue_histories"]
    if "npc_moods" in cumulative_state:
        final_result["npc_moods"] = cumulative_state["npc_moods"]
    
    return final_result 