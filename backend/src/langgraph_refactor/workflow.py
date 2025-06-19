"""
LangGraph工作流图构建
"""
import sys
import os
from typing import Dict, Any, Literal

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(os.path.dirname(SRC_DIR))
sys.path.append(PROJECT_ROOT)
sys.path.append(SRC_DIR)

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph_refactor.game_state import GameState, create_initial_state
from langgraph_refactor.nodes import (
    supervisor_node,
    move_handler_node,
    dialogue_handler_node,
    exploration_handler_node,
    general_handler_node,
    compound_handler_node
)


def create_system_update_node(state: GameState) -> Dict[str, Any]:
    """
    系统更新节点 - 在每个行动完成后更新系统状态
    """
    from datetime import datetime
    
    # 更新最后更新时间
    current_timestamp = datetime.now().strftime("%H:%M:%S")
    
    # 清空当前行动，准备接收下一个行动
    return {
        "last_update_time": current_timestamp,
        "current_action": "",
        "action_target": None,
        "next_node": None
    }


def route_to_next_node(state: GameState) -> Literal["move_handler", "dialogue_handler", "exploration_handler", "general_handler", "compound_handler", "__end__"]:
    """
    路由函数 - 根据supervisor的决策路由到下一个节点
    """
    next_node = state.get("next_node")
    
    if next_node in ["move_handler", "dialogue_handler", "exploration_handler", "general_handler", "compound_handler"]:
        return next_node
    else:
        return "__end__"


def create_game_workflow() -> StateGraph:
    """
    创建游戏工作流图
    """
    # 创建状态图
    workflow = StateGraph(GameState)
    
    # 添加节点
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("move_handler", move_handler_node)
    workflow.add_node("dialogue_handler", dialogue_handler_node)
    workflow.add_node("exploration_handler", exploration_handler_node)
    workflow.add_node("general_handler", general_handler_node)
    workflow.add_node("compound_handler", compound_handler_node)
    workflow.add_node("system_update", create_system_update_node)
    
    # 设置入口 - 从supervisor开始
    workflow.add_edge(START, "supervisor")
    
    # 从supervisor根据决策路由到不同的处理节点
    workflow.add_conditional_edges(
        "supervisor",
        route_to_next_node,
        {
            "move_handler": "move_handler",
            "dialogue_handler": "dialogue_handler", 
            "exploration_handler": "exploration_handler",
            "general_handler": "general_handler",
            "compound_handler": "compound_handler",
            "__end__": "system_update"  # 如果没有有效的下一个节点，进行系统更新
        }
    )
    
    # 定义处理节点的路由函数
    def route_from_handler(state: GameState) -> Literal["compound_handler", "system_update"]:
        """从处理节点路由到复合处理或系统更新"""
        if state.get("compound_actions"):
            return "compound_handler"
        return "system_update"
    
    # 从各个处理节点根据是否有compound_actions路由
    workflow.add_conditional_edges(
        "move_handler",
        route_from_handler,
        {
            "compound_handler": "compound_handler",
            "system_update": "system_update"
        }
    )
    
    workflow.add_conditional_edges(
        "dialogue_handler", 
        route_from_handler,
        {
            "compound_handler": "compound_handler",
            "system_update": "system_update"
        }
    )
    
    workflow.add_conditional_edges(
        "exploration_handler",
        route_from_handler,
        {
            "compound_handler": "compound_handler", 
            "system_update": "system_update"
        }
    )
    
    workflow.add_conditional_edges(
        "general_handler",
        route_from_handler,
        {
            "compound_handler": "compound_handler",
            "system_update": "system_update"
        }
    )
    
    # compound_handler完成后总是进入系统更新
    workflow.add_edge("compound_handler", "system_update")
    
    # 系统更新后结束工作流
    workflow.add_edge("system_update", END)
    
    # 编译工作流（带持久化支持）
    return workflow.compile(checkpointer=MemorySaver())


def create_game_graph_with_config():
    """
    创建带配置的游戏图实例
    """
    return create_game_workflow()


# 全局游戏图实例
game_graph = None

def get_game_graph():
    """
    获取全局游戏图实例（单例模式）
    """
    global game_graph
    if game_graph is None:
        game_graph = create_game_workflow()
    return game_graph


def reset_game_graph():
    """
    重置游戏图实例
    """
    global game_graph
    game_graph = None


# 工作流执行辅助函数
async def execute_game_action(action: str, session_id: str = "default") -> Dict[str, Any]:
    """
    执行游戏行动
    
    Args:
        action: 玩家行动
        session_id: 会话ID
    
    Returns:
        游戏执行结果
    """
    graph = get_game_graph()
    
    # 配置会话
    config = {"configurable": {"thread_id": session_id}}
    
    # 打印Graph结构信息
    print("\n" + "="*80)
    print(f"🎮 开始执行游戏行动: {action}")
    print(f"📝 会话ID: {session_id}")
    print("="*80)
    
    # 打印Graph结构
    print("\n📊 LangGraph结构信息:")
    print("-"*50)
    try:
        graph_info = graph.get_graph()
        print(f"🔵 节点列表 ({len(graph_info.nodes)}个):")
        for i, node in enumerate(graph_info.nodes, 1):
            print(f"  {i}. {node}")
        
        print(f"\n🔗 边连接 ({len(graph_info.edges)}个):")
        for i, edge in enumerate(graph_info.edges, 1):
            print(f"  {i}. {edge}")
    except Exception as e:
        print(f"❌ 获取Graph信息失败: {e}")
    
    try:
        # 获取当前状态
        current_state = graph.get_state(config)
        
        print(f"\n📍 当前状态信息:")
        print("-"*30)
        if current_state.values:
            state_summary = {
                "player_location": current_state.values.get("player_location", "未知"),
                "current_time": current_state.values.get("current_time", "未知"),
                "session_id": current_state.values.get("session_id", "未知")
            }
            print(f"  状态: {state_summary}")
        else:
            print("  状态: 无现有状态，将创建初始状态")
        
        # 如果没有现有状态，创建初始状态
        if not current_state.values:
            print("\n🚀 创建初始游戏状态...")
            initial_state = create_initial_state(session_id)
            initial_state["current_action"] = action
            print(f"  ✅ 初始状态创建完成，NPC位置数量: {len(initial_state.get('npc_locations', {}))}")
        else:
            # 更新当前行动
            initial_state = {
                **current_state.values,
                "current_action": action
            }
            print(f"  ✅ 使用现有状态，更新行动为: {action}")
        
        print(f"\n🔄 开始执行LangGraph工作流...")
        print("-"*40)
        
        # 执行工作流并捕获执行过程 - 只执行一次
        execution_steps = []
        final_result = None
        
        async for step in graph.astream(initial_state, config=config, stream_mode="updates"):
            execution_steps.append(step)
            print(f"\n📍 执行步骤 {len(execution_steps)}:")
            for node_name, node_output in step.items():
                print(f"  🎯 节点: {node_name}")
                if "messages" in node_output:
                    print(f"  💬 消息数量: {len(node_output['messages'])}")
                    for msg in node_output["messages"]:
                        print(f"    📢 {msg.get('speaker', '未知')}: {msg.get('message', '')[:100]}...")
                if "next_node" in node_output:
                    next_node = node_output["next_node"]
                    print(f"  ➡️  下一节点: {next_node if next_node else '结束'}")
                if "game_events" in node_output:
                    print(f"  🎪 游戏事件数量: {len(node_output['game_events'])}")
        
        # 获取最终状态（不重复执行）
        final_state = graph.get_state(config)
        final_result = final_state.values if final_state.values else initial_state
        
        print(f"\n✅ 工作流执行完成!")
        print(f"  📊 总执行步骤: {len(execution_steps)}")
        print(f"  💬 总消息数量: {len(final_result.get('messages', []))}")
        print(f"  🎪 总事件数量: {len(final_result.get('game_events', []))}")
        
        print("\n" + "="*80)
        print("🎮 游戏行动执行完成")
        print("="*80)
        
        return {
            "success": True,
            "state": final_result,
            "messages": final_result.get("messages", []),
            "game_events": final_result.get("game_events", []),
            "execution_steps": execution_steps
        }
        
    except Exception as e:
        print(f"\n❌ 执行游戏行动时出错: {e}")
        print("="*80)
        return {
            "success": False,
            "error": str(e),
            "messages": [{"speaker": "系统", "message": "处理行动时出现错误", "type": "error"}]
        }


def get_game_state(session_id: str = "default") -> Dict[str, Any]:
    """
    获取游戏状态
    
    Args:
        session_id: 会话ID
    
    Returns:
        当前游戏状态
    """
    graph = get_game_graph()
    config = {"configurable": {"thread_id": session_id}}
    
    try:
        current_state = graph.get_state(config)
        
        if current_state.values:
            state = current_state.values
            
            # 格式化返回状态
            return {
                "player_location": state.get("player_location", "未知地点"),
                "current_time": state.get("current_time", "未知时间"),
                "player_personality": state.get("player_personality", "普通"),
                "messages": state.get("messages", []),
                "npc_locations": state.get("npc_locations", {}),
                "game_events": state.get("game_events", []),
                "session_id": state.get("session_id", session_id)
            }
        else:
            # 返回初始状态
            return create_initial_state(session_id)
            
    except Exception as e:
        print(f"获取游戏状态时出错: {e}")
        return create_initial_state(session_id)


def initialize_new_game(session_id: str = "default") -> Dict[str, Any]:
    """
    初始化新游戏
    
    Args:
        session_id: 会话ID
    
    Returns:
        初始游戏状态
    """
    graph = get_game_graph()
    config = {"configurable": {"thread_id": session_id}}
    
    # 创建初始状态
    initial_state = create_initial_state(session_id)
    
    try:
        # 设置初始状态
        graph.update_state(config, initial_state)
        return initial_state
        
    except Exception as e:
        print(f"初始化新游戏时出错: {e}")
        return initial_state


# 流式执行支持
async def stream_game_action(action: str, session_id: str = "default"):
    """
    流式执行游戏行动
    
    Args:
        action: 玩家行动
        session_id: 会话ID
    
    Yields:
        执行过程中的中间状态
    """
    graph = get_game_graph()
    config = {"configurable": {"thread_id": session_id}}
    
    try:
        # 获取当前状态
        current_state = graph.get_state(config)
        
        if not current_state.values:
            initial_state = create_initial_state(session_id)
            initial_state["current_action"] = action
        else:
            initial_state = {
                **current_state.values,
                "current_action": action
            }
        
        # 流式执行
        async for chunk in graph.astream(initial_state, config=config, stream_mode="updates"):
            yield chunk
            
    except Exception as e:
        print(f"流式执行游戏行动时出错: {e}")
        yield {"error": str(e)}


if __name__ == "__main__":
    # 测试工作流创建
    try:
        workflow = create_game_workflow()
        print("✅ LangGraph工作流创建成功")
        
        # 打印工作流结构
        print("\n工作流节点:")
        for node in workflow.get_graph().nodes:
            print(f"  - {node}")
            
        print("\n工作流边:")
        for edge in workflow.get_graph().edges:
            print(f"  - {edge}")
            
    except Exception as e:
        print(f"❌ 工作流创建失败: {e}") 