"""
提示词模板类
"""
from typing import Dict, Any, List
from .prompt_manager import prompt_manager


class PromptTemplates:
    """提示词模板类"""
    
    @staticmethod
    def get_action_router_prompt(player_location: str, current_time: str, player_personality: str) -> str:
        """获取行动路由器提示词"""
        return prompt_manager.render_prompt('action_router', 
                                          player_location=player_location,
                                          current_time=current_time,
                                          player_personality=player_personality)
    
    @staticmethod
    def get_npc_dialogue_prompt(npc_name: str, personality: str, background: str, relations: str, 
                               mood: str, npc_location: str, npc_event: str, player_name: str,
                               current_time: str, location_details: str, location_description: str,
                               other_npcs_info: str, player_personality: str, history_str: str,
                               dialogue_summary: str, message: str) -> str:
        """获取NPC对话提示词"""
        return prompt_manager.render_prompt('npc_dialogue',
                                          npc_name=npc_name,
                                          personality=personality,
                                          background=background,
                                          relations=relations,
                                          mood=mood,
                                          npc_location=npc_location,
                                          npc_event=npc_event,
                                          player_name=player_name,
                                          current_time=current_time,
                                          location_details=location_details,
                                          location_description=location_description,
                                          other_npcs_info=other_npcs_info,
                                          player_personality=player_personality,
                                          history_str=history_str,
                                          dialogue_summary=dialogue_summary,
                                          message=message)
    
    @staticmethod
    def get_sensory_feedback_prompt(location_name: str, location_description: str, 
                                   current_time: str, npc_info: str, action: str) -> str:
        """获取五感反馈提示词"""
        return prompt_manager.render_prompt('sensory_feedback',
                                          location_name=location_name,
                                          location_description=location_description,
                                          current_time=current_time,
                                          npc_info=npc_info,
                                          action=action)
    
    @staticmethod
    def get_move_destination_prompt(player_name: str, current_location: str, 
                                   all_location_info: str, action: str) -> str:
        """获取移动目标解析提示词"""
        return prompt_manager.render_prompt('move_destination',
                                          player_name=player_name,
                                          current_location=current_location,
                                          all_location_info=all_location_info,
                                          action=action)
    
    @staticmethod
    def get_general_response_prompt(player_location: str, current_time: str, 
                                   player_personality: str, action: str) -> str:
        """获取通用响应提示词"""
        return prompt_manager.render_prompt('general_response',
                                          player_location=player_location,
                                          current_time=current_time,
                                          player_personality=player_personality,
                                          action=action)
    
    @staticmethod
    def get_schedule_update_prompt(available_locations: str, npc_name: str, 
                                  player_message: str, npc_reply: str, 
                                  current_time: str, current_schedule: str) -> str:
        """获取计划表更新分析提示词"""
        return prompt_manager.render_prompt('schedule_update',
                                          available_locations=available_locations,
                                          npc_name=npc_name,
                                          player_message=player_message,
                                          npc_reply=npc_reply,
                                          current_time=current_time,
                                          current_schedule=current_schedule)
    
    @staticmethod
    def get_time_estimation_prompt(action: str, personality: str) -> str:
        """获取时间估算提示词"""
        return prompt_manager.render_prompt('time_estimation',
                                          action=action,
                                          personality=personality) 