"""
LangGraph版本的FastAPI集成
提供与原有API兼容的接口
"""
import sys
import os
import json
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(os.path.dirname(SRC_DIR))
sys.path.append(PROJECT_ROOT)
sys.path.append(SRC_DIR)

from langgraph_refactor.workflow import (
    execute_game_action,
    get_game_state, 
    initialize_new_game,
    stream_game_action,
    get_game_graph
)
from langgraph_refactor.game_state import create_initial_state
from data.locations import all_locations_data, location_connections
from data.characters import all_actresses


# 请求模型
class ActionRequest(BaseModel):
    action: str = Field(description="玩家行动")
    session_id: str = Field(default="default", description="会话ID")


class DialogueRequest(BaseModel):
    message: str = Field(description="对话消息")
    history: List[Dict] = Field(default=[], description="对话历史（兼容性字段）")


class GameStateResponse(BaseModel):
    player_location: str
    current_time: str
    location_description: str
    connected_locations: List[str]
    npcs_at_current_location: List[Dict[str, Any]]
    dialogue_history: List[Dict[str, str]]


def create_langgraph_api_app() -> FastAPI:
    """
    创建LangGraph版本的FastAPI应用
    """
    app = FastAPI(title="LLM文字游戏 (LangGraph版本)", version="2.0.0")
    
    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "LLM文字游戏 LangGraph版本",
            "version": "2.0.0",
            "status": "运行中"
        }
    
    @app.get("/api/game_state")
    async def get_current_game_state(session_id: str = "default"):
        """
        获取当前游戏状态（兼容原有API）
        """
        try:
            state = get_game_state(session_id)
            
            # 获取当前位置详情
            location_details = get_location_details_for_api(
                state["player_location"], 
                state["npc_locations"],
                state["current_time"]
            )
            
            # 构建完整的响应，兼容前端期望的数据格式
            response = {
                "player_location": state["player_location"],
                "current_time": state["current_time"],
                "location_description": location_details.get("description", ""),
                "connected_locations": [
                    all_locations_data.get(loc_key, {}).get("name", loc_key) 
                    for loc_key in location_details.get("connections", [])
                ],
                "npcs_at_current_location": location_details.get("npcs_present", []),
                "dialogue_history": convert_messages_to_dialogue_history(state["messages"])
            }
            
            # 确保npcs_at_current_location不为空时，包含必要的字段
            for npc in response["npcs_at_current_location"]:
                if "event" not in npc:
                    npc["event"] = npc.get("activity", "空闲")
                if "personality" not in npc:
                    npc["personality"] = "友善"
            
            return response
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取游戏状态失败: {str(e)}")
    
    @app.post("/api/process_action")
    async def process_player_action(request: ActionRequest):
        """
        处理玩家行动（LangGraph版本）
        """
        try:
            # 执行游戏行动
            result = await execute_game_action(request.action, request.session_id)
            
            if not result["success"]:
                # 如果处理失败，返回当前游戏状态
                current_state = get_game_state(request.session_id)
                location_details = get_location_details_for_api(
                    current_state["player_location"], 
                    current_state["npc_locations"],
                    current_state["current_time"]
                )
                
                return {
                    "player_location": current_state["player_location"],
                    "current_time": current_state["current_time"],
                    "location_description": location_details.get("description", ""),
                    "connected_locations": [
                        all_locations_data.get(loc_key, {}).get("name", loc_key) 
                        for loc_key in location_details.get("connections", [])
                    ],
                    "npcs_at_current_location": location_details.get("npcs_present", []),
                    "dialogue_history": convert_messages_to_dialogue_history(current_state["messages"])
                }
            
            # 获取更新后的游戏状态
            updated_state = get_game_state(request.session_id)
            
            # 获取当前位置详情
            location_details = get_location_details_for_api(
                updated_state["player_location"], 
                updated_state["npc_locations"],
                updated_state["current_time"]
            )
            
            # 返回完整的游戏状态（与/api/game_state格式一致）
            response = {
                "player_location": updated_state["player_location"],
                "current_time": updated_state["current_time"],
                "location_description": location_details.get("description", ""),
                "connected_locations": [
                    all_locations_data.get(loc_key, {}).get("name", loc_key) 
                    for loc_key in location_details.get("connections", [])
                ],
                "npcs_at_current_location": location_details.get("npcs_present", []),
                "dialogue_history": convert_messages_to_dialogue_history(updated_state["messages"])
            }
            
            # 确保npcs_at_current_location不为空时，包含必要的字段
            for npc in response["npcs_at_current_location"]:
                if "event" not in npc:
                    npc["event"] = npc.get("activity", "空闲")
                if "personality" not in npc:
                    npc["personality"] = "友善"
            
            return response
            
        except Exception as e:
            print(f"处理行动错误: {e}")
            # 如果出错，返回当前游戏状态
            current_state = get_game_state(request.session_id)
            location_details = get_location_details_for_api(
                current_state["player_location"], 
                current_state["npc_locations"],
                current_state["current_time"]
            )
            
            return {
                "player_location": current_state["player_location"],
                "current_time": current_state["current_time"],
                "location_description": location_details.get("description", ""),
                "connected_locations": [
                    all_locations_data.get(loc_key, {}).get("name", loc_key) 
                    for loc_key in location_details.get("connections", [])
                ],
                "npcs_at_current_location": location_details.get("npcs_present", []),
                "dialogue_history": convert_messages_to_dialogue_history(current_state["messages"])
            }
    
    @app.post("/api/stream_action") 
    async def stream_player_action(request: ActionRequest):
        """
        流式处理玩家行动
        """
        async def generate_stream():
            try:
                async for chunk in stream_game_action(request.action, request.session_id):
                    if "error" in chunk:
                        yield f"data: {json.dumps({'error': chunk['error']})}\n\n"
                    else:
                        yield f"data: {json.dumps(chunk)}\n\n"
                        
                # 发送完成信号
                yield f"data: {json.dumps({'status': 'completed'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
    
    @app.post("/api/continue_dialogue/{npc_name}")
    async def continue_dialogue_with_npc(npc_name: str, request: DialogueRequest):
        """
        继续与NPC对话（兼容原有API）
        """
        try:
            # 构造对话行动
            dialogue_action = f"和{npc_name}说：{request.message}"
            
            # 执行对话
            result = await execute_game_action(dialogue_action, "default")
            
            if not result["success"]:
                return {
                    "status": "error",
                    "npc_reply": "对话处理失败",
                    "game_state": get_game_state("default")
                }
            
            # 提取NPC回复
            npc_reply = extract_npc_reply_from_messages(result["messages"], npc_name)
            
            return {
                "status": "success",
                "npc_reply": npc_reply,
                "game_state": get_game_state("default")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "npc_reply": f"对话出错：{str(e)}",
                "game_state": get_game_state("default")
            }
    
    @app.get("/api/npc_dialogue_history/{npc_name}")
    async def get_npc_dialogue_history(npc_name: str, session_id: str = "default"):
        """
        获取与特定NPC的对话历史
        """
        try:
            state = get_game_state(session_id)
            dialogue_history = state.get("npc_dialogue_histories", {}).get(npc_name, [])
            
            return {
                "npc_name": npc_name,
                "dialogue_history": dialogue_history
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取对话历史失败: {str(e)}")
    
    @app.post("/api/initialize_game")
    async def initialize_game(session_id: str = "default"):
        """
        初始化新游戏
        """
        try:
            initial_state = initialize_new_game(session_id)
            return {
                "status": "success",
                "message": "游戏初始化成功",
                "game_state": initial_state
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"游戏初始化失败: {str(e)}")
    
    @app.get("/api/debug/workflow_state")
    async def debug_workflow_state(session_id: str = "default"):
        """
        调试：获取工作流状态
        """
        try:
            graph = get_game_graph()
            config = {"configurable": {"thread_id": session_id}}
            
            state = graph.get_state(config)
            
            return {
                "has_state": bool(state.values),
                "state": dict(state.values) if state.values else None,
                "next_steps": state.next if hasattr(state, 'next') else None
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取调试信息失败: {str(e)}")
    
    @app.get("/api/debug/locations")
    async def debug_locations():
        """
        调试：获取所有地点信息
        """
        # 预定义的静态地点列表
        static_locations = {
            "linkai_room", "linruoxi_room", "zhangyuqing_room", 
            "livingroom", "kitchen", "bathroom", "actor_dorm", 
            "main_studio", "green_screen_studio", "sound_studio",
            "makeup_room", "costume_room", "prop_warehouse",
            "director_office", "producer_office", "script_room",
            "editing_room", "meeting_room"
        }
        
        locations = {}
        total_static = 0
        total_dynamic = 0
        
        for key, location in all_locations_data.items():
            is_dynamic = key not in static_locations
            if is_dynamic:
                total_dynamic += 1
            else:
                total_static += 1
                
            locations[key] = {
                "name": location["name"],
                "description": location["description"],
                "connections": location_connections.get(key, []),
                "is_dynamic": is_dynamic,
                "type": "动态创建" if is_dynamic else "静态预设"
            }
        
        return {
            "locations": locations,
            "total_count": len(all_locations_data),
            "static_count": total_static,
            "dynamic_count": total_dynamic
        }
    
    @app.get("/api/debug/npc_locations")
    async def debug_npc_locations(session_id: str = "default"):
        """
        调试：获取所有NPC的当前位置和状态
        """
        try:
            # 获取当前游戏状态
            state = get_game_state(session_id)
            current_time = state.get("current_time", "09:00")
            player_location = state.get("player_location", "studio_entrance")
            npc_locations = state.get("npc_locations", {})
            
            # 获取每个NPC的详细信息
            npc_status = {}
            for actress in all_actresses:
                npc_name = actress["name"]
                
                # 🔧 修复：总是根据当前时间和计划表计算NPC的准确位置
                # 而不是依赖可能过时的npc_locations状态
                from langgraph_refactor.nodes import get_npc_current_location_and_event
                from datetime import datetime
                current_time_obj = datetime.strptime(current_time, "%H:%M").time()
                npc_location, npc_event = get_npc_current_location_and_event(npc_name, current_time_obj, state)
                
                # 获取NPC当前心情（从状态或者NPC数据中）
                npc_mood = state.get("npc_moods", {}).get(npc_name, actress.get("mood", "平静"))
                
                npc_status[npc_name] = {
                    "current_location": npc_location,
                    "current_event": npc_event,
                    "current_mood": npc_mood,  # 添加心情信息
                    "schedule": actress.get("schedule", [])
                }
            
            # 获取玩家当前位置的NPC
            from langgraph_refactor.nodes import get_npcs_at_location
            print(f"🔍 【API调试】获取玩家位置NPC")
            print(f"🔍 【API调试】玩家位置: {player_location}")
            print(f"🔍 【API调试】当前时间: {current_time}")
            print(f"🔍 【API调试】npc_locations状态: {npc_locations}")
            
            # 🔧 修复：传递空的npc_locations，让get_npcs_at_location函数根据时间重新计算
            # 而不是使用可能过时的状态数据
            npcs_at_player_location = get_npcs_at_location(player_location, {}, current_time, None)
            
            print(f"🔍 【API调试】计算得到的NPC: {[npc['name'] for npc in npcs_at_player_location]}")
            
            return {
                "current_time": current_time,
                "player_location": player_location,
                "npc_locations": npc_status,
                "npcs_at_player_location": npcs_at_player_location
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取NPC位置信息失败: {str(e)}")
    
    @app.get("/api/debug/npcs")
    async def debug_npcs():
        """
        调试：获取所有NPC信息
        """
        npcs = []
        for actress in all_actresses:
            npcs.append({
                "name": actress["name"],
                "personality": actress["personality"],
                "schedule": actress.get("schedule", []),
                "default_location": actress.get("default_location", "未知")
            })
        
        return {"npcs": npcs}
    
    @app.get("/api/debug/messages")
    async def debug_messages(session_id: str = "default"):
        """
        调试：查看原始messages和转换后的dialogue_history
        """
        try:
            # 获取原始游戏状态
            state = get_game_state(session_id)
            raw_messages = state.get("messages", [])
            
            # 转换为dialogue_history
            dialogue_history = convert_messages_to_dialogue_history(raw_messages)
            
            return {
                "session_id": session_id,
                "raw_messages_count": len(raw_messages),
                "dialogue_history_count": len(dialogue_history),
                "raw_messages": raw_messages[-10:],  # 只显示最近10条原始消息
                "dialogue_history": dialogue_history[-10:],  # 只显示最近10条对话历史
                "npc_dialogue_histories": state.get("npc_dialogue_histories", {})
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取调试消息失败: {str(e)}")
    
    return app


# 辅助函数
def get_location_details_for_api(location_name: str, npc_locations: Dict[str, str], current_time: str) -> Dict[str, Any]:
    """
    获取地点详情（用于API响应）
    """
    from langgraph_refactor.nodes import get_npcs_at_location
    
    location_data = all_locations_data.get(location_name, {})
    
    return {
        "name": location_data.get("name", location_name),
        "description": location_data.get("description", "未知地点"),
        "connections": location_connections.get(location_name, []),
        "npcs_present": get_npcs_at_location(location_name, npc_locations, current_time, None)
    }


def convert_messages_to_dialogue_history(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    将消息列表转换为对话历史格式（兼容原有API）
    改进：去重、过滤、格式化
    """
    dialogue_history = []
    seen_messages = set()  # 用于去重
    
    for msg in messages:
        speaker = msg.get("speaker", "未知")
        message = msg.get("message", "")
        timestamp = msg.get("timestamp", "")
        
        # 跳过空消息
        if not message.strip():
            continue
            
        # 创建消息唯一标识（speaker + message内容）
        message_key = f"{speaker}:{message}"
        
        # 如果已经存在相同的消息，跳过
        if message_key in seen_messages:
            continue
            
        seen_messages.add(message_key)
        
        # 只包含对话相关的消息（玩家、NPC、重要系统消息）
        if speaker in ["玩家"] or is_npc_speaker(speaker) or is_important_system_message(speaker, message):
            dialogue_history.append({
                "speaker": speaker,
                "message": message,
                "timestamp": timestamp
            })
    
    return dialogue_history


def is_npc_speaker(speaker: str) -> bool:
    """判断是否是NPC发言者"""
    from data.characters import all_actresses
    npc_names = [actress["name"] for actress in all_actresses]
    return speaker in npc_names


def is_important_system_message(speaker: str, message: str) -> bool:
    """判断是否是重要的系统消息（值得显示在对话历史中）"""
    if speaker != "系统":
        return False
        
    # 过滤掉一些不重要的系统消息
    unimportant_patterns = [
        "处理出现问题",
        "无法理解",
        "请明确指定",
        "不在当前位置",
        "已经在",
        "无法直接移动"
    ]
    
    for pattern in unimportant_patterns:
        if pattern in message:
            return False
            
    return True


def format_messages_for_response(messages: List[Dict[str, str]]) -> str:
    """
    格式化消息用于响应
    """
    if not messages:
        return ""
    
    formatted_messages = []
    for msg in messages:
        speaker = msg.get("speaker", "")
        content = msg.get("message", "")
        
        if speaker == "系统":
            formatted_messages.append(content)
        else:
            formatted_messages.append(f"{speaker}：{content}")
    
    return "\n".join(formatted_messages)


def extract_npc_reply_from_messages(messages: List[Dict[str, str]], npc_name: str) -> str:
    """
    从消息中提取特定NPC的回复
    """
    for msg in reversed(messages):  # 从最新的消息开始查找
        if msg.get("speaker") == npc_name:
            return msg.get("message", "")
    
    return f"{npc_name}没有回应"


# 创建应用实例
def create_app():
    """
    创建FastAPI应用实例
    """
    return create_langgraph_api_app()


if __name__ == "__main__":
    import uvicorn
    
    app = create_langgraph_api_app()
    
    print("🚀 启动LangGraph版本的游戏服务器...")
    print("📍 服务地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 