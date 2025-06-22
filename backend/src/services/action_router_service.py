"""
行动路由服务 - 分析玩家输入并路由到相应处理服务
"""
import sys
import os
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(os.path.dirname(SRC_DIR))
sys.path.append(PROJECT_ROOT)
sys.path.append(SRC_DIR)

from .llm_service import LLMService
from ..models.game_state_model import GameStateModel
from ..prompts.prompt_templates import PromptTemplates


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


class ActionRouterService:
    """行动路由服务类"""
    
    def __init__(self):
        self.llm_service = LLMService()
    
    async def route_action(self, action: str, game_state: GameStateModel) -> Dict[str, Any]:
        """
        分析玩家行动并返回路由结果
        
        Args:
            action: 玩家行动
            game_state: 游戏状态
            
        Returns:
            路由结果
        """
        print(f"\n🎯 [ActionRouterService] 分析行动: {action}")
        
        if not action or not action.strip():
            print(f"⚠️ 空行动输入")
            return {
                "action_type": "general",
                "confidence": 1.0,
                "reason": "空输入",
                "sub_actions": None
            }
        
        llm = self.llm_service.get_llm_instance()
        
        # 使用prompt_manager获取系统提示
        system_prompt = PromptTemplates.get_action_router_prompt(
            player_location=game_state.player_location,
            current_time=game_state.current_time,
            player_personality=game_state.player_personality
        )
        
        user_input = f"玩家行动：{action}"
        
        print(f"\n🤖 LLM调用 - 行动路由分析")
        print(f"📤 输入 (System):")
        print(f"  当前位置: {game_state.player_location}")
        print(f"  当前时间: {game_state.current_time}")
        print(f"  玩家性格: {game_state.player_personality}")
        print(f"📤 输入 (Human): {user_input}")
        
        # 使用LLM进行路由决策
        router = llm.with_structured_output(ActionRouter)
        try:
            result = await router.ainvoke([
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
            
            return {
                "action_type": result.action_type,
                "confidence": result.confidence,
                "reason": result.reason,
                "sub_actions": result.sub_actions
            }
            
        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            print(f"  ➡️ 降级到类型: general")
            return {
                "action_type": "general",
                "confidence": 0.5,
                "reason": f"LLM调用失败，降级处理: {str(e)}",
                "sub_actions": None
            }
    
    def is_dialogue_action(self, action: str) -> bool:
        """简单的对话行动检测"""
        dialogue_patterns = [
            "和", "说", "对", "告诉", "跟", "向"
        ]
        
        for pattern in dialogue_patterns:
            if pattern in action and ("说" in action or "：" in action or ":" in action):
                return True
        
        return False
    
    def is_movement_action(self, action: str) -> bool:
        """简单的移动行动检测"""
        movement_patterns = [
            "去", "到", "前往", "移动", "走"
        ]
        
        for pattern in movement_patterns:
            if pattern in action:
                return True
        
        return False
    
    def is_exploration_action(self, action: str) -> bool:
        """简单的探索行动检测"""
        exploration_patterns = [
            "看", "观察", "检查", "探索", "四处", "环顾", "寻找"
        ]
        
        for pattern in exploration_patterns:
            if pattern in action:
                return True
        
        return False 