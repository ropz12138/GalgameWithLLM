"""
消息服务 - 处理游戏消息的数据库持久化
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc

from ..database.config import get_engine
from ..database.models import Message, Entity, MessageType
from ..utils.time_utils import TimeUtils


class MessageService:
    """消息服务 - 负责游戏消息的持久化和查询"""
    
    def __init__(self):
        self.engine = get_engine()
        self.Session = sessionmaker(bind=self.engine)
    
    async def save_user_input(
        self, 
        user_id: int, 
        story_id: int, 
        session_id: str, 
        content: str, 
        location: str, 
        game_time: datetime
    ) -> int:
        """保存用户输入消息"""
        try:
            session = self.Session()
            
            # 获取位置实体ID
            location_id = await self._get_location_entity_id(session, story_id, location)
            
            message = Message(
                user_id=user_id,
                story_id=story_id,
                session_id=session_id,
                message_type=1,  # user_input
                sub_type="player_action",
                content=content,
                location=location_id,
                game_time=game_time,
                message_metadata={}
            )
            
            session.add(message)
            session.commit()
            message_id = message.id
            session.close()
            
            print(f"✅ [MessageService] 保存用户输入: ID={message_id}, 内容='{content[:50]}...'")
            return message_id
            
        except Exception as e:
            print(f"❌ [MessageService] 保存用户输入失败: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return 0
    
    async def save_npc_dialogue(
        self, 
        user_id: int, 
        story_id: int, 
        session_id: str, 
        npc_name: str, 
        dialogue: str, 
        location: str, 
        game_time: datetime,
        metadata: Dict = None
    ) -> int:
        """保存NPC对话消息"""
        try:
            session = self.Session()
            
            # 获取位置和NPC实体ID
            location_id = await self._get_location_entity_id(session, story_id, location)
            npc_id = await self._get_npc_entity_id(session, story_id, npc_name)
            
            message = Message(
                user_id=user_id,
                story_id=story_id,
                session_id=session_id,
                message_type=2,  # npc_dialogue
                sub_type="dialogue",
                content=dialogue,
                related_entity=npc_id,
                location=location_id,
                game_time=game_time,
                message_metadata=metadata or {}
            )
            
            session.add(message)
            session.commit()
            message_id = message.id
            session.close()
            
            print(f"✅ [MessageService] 保存NPC对话: ID={message_id}, NPC={npc_name}, 内容='{dialogue[:50]}...'")
            return message_id
            
        except Exception as e:
            print(f"❌ [MessageService] 保存NPC对话失败: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return 0
    
    async def save_system_action(
        self, 
        user_id: int, 
        story_id: int, 
        session_id: str, 
        action_result: str, 
        location: str, 
        game_time: datetime,
        sub_type: str = "action_result",
        metadata: Dict = None
    ) -> int:
        """保存系统行动反馈消息"""
        try:
            session = self.Session()
            
            location_id = await self._get_location_entity_id(session, story_id, location)
            
            message = Message(
                user_id=user_id,
                story_id=story_id,
                session_id=session_id,
                message_type=3,  # system_action
                sub_type=sub_type,
                content=action_result,
                location=location_id,
                game_time=game_time,
                message_metadata=metadata or {}
            )
            
            session.add(message)
            session.commit()
            message_id = message.id
            session.close()
            
            print(f"✅ [MessageService] 保存系统行动: ID={message_id}, 类型={sub_type}, 内容='{action_result[:50]}...'")
            return message_id
            
        except Exception as e:
            print(f"❌ [MessageService] 保存系统行动失败: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return 0
    
    async def save_sensory_feedback(
        self, 
        user_id: int, 
        story_id: int, 
        session_id: str, 
        feedback: str, 
        location: str, 
        game_time: datetime,
        structured_data: Dict = None
    ) -> int:
        """保存五感反馈消息"""
        try:
            session = self.Session()
            
            location_id = await self._get_location_entity_id(session, story_id, location)
            
            message = Message(
                user_id=user_id,
                story_id=story_id,
                session_id=session_id,
                message_type=4,  # sensory_feedback
                sub_type="sensory",
                content=feedback,
                location=location_id,
                game_time=game_time,
                structured_data=structured_data,
                message_metadata={}
            )
            
            session.add(message)
            session.commit()
            message_id = message.id
            session.close()
            
            print(f"✅ [MessageService] 保存五感反馈: ID={message_id}, 内容='{feedback[:50]}...'")
            return message_id
            
        except Exception as e:
            print(f"❌ [MessageService] 保存五感反馈失败: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return 0
    
    async def save_system_info(
        self, 
        user_id: int, 
        story_id: int, 
        session_id: str, 
        info: str, 
        location: str, 
        game_time: datetime,
        sub_type: str = "info"
    ) -> int:
        """保存系统信息消息"""
        try:
            session = self.Session()
            
            location_id = await self._get_location_entity_id(session, story_id, location)
            
            message = Message(
                user_id=user_id,
                story_id=story_id,
                session_id=session_id,
                message_type=5,  # system_info
                sub_type=sub_type,
                content=info,
                location=location_id,
                game_time=game_time,
                message_metadata={}
            )
            
            session.add(message)
            session.commit()
            message_id = message.id
            session.close()
            
            print(f"✅ [MessageService] 保存系统信息: ID={message_id}, 类型={sub_type}, 内容='{info[:50]}...'")
            return message_id
            
        except Exception as e:
            print(f"❌ [MessageService] 保存系统信息失败: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return 0
    
    async def save_error_message(
        self, 
        user_id: int, 
        story_id: int, 
        session_id: str, 
        error: str, 
        location: str, 
        game_time: datetime
    ) -> int:
        """保存错误消息"""
        try:
            session = self.Session()
            
            location_id = await self._get_location_entity_id(session, story_id, location)
            
            message = Message(
                user_id=user_id,
                story_id=story_id,
                session_id=session_id,
                message_type=6,  # error_message
                sub_type="error",
                content=error,
                location=location_id,
                game_time=game_time,
                message_metadata={}
            )
            
            session.add(message)
            session.commit()
            message_id = message.id
            session.close()
            
            print(f"✅ [MessageService] 保存错误消息: ID={message_id}, 内容='{error[:50]}...'")
            return message_id
            
        except Exception as e:
            print(f"❌ [MessageService] 保存错误消息失败: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return 0
    
    async def get_session_history(
        self, 
        user_id: int, 
        story_id: int, 
        session_id: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取会话历史消息"""
        try:
            session = self.Session()
            
            messages = session.query(Message).filter(
                Message.user_id == user_id,
                Message.story_id == story_id,
                Message.session_id == session_id
            ).order_by(desc(Message.created_at)).limit(limit).all()
            
            result = [msg.to_dict() for msg in messages]
            session.close()
            
            print(f"✅ [MessageService] 获取会话历史: 用户={user_id}, 会话={session_id}, 消息数={len(result)}")
            return result
            
        except Exception as e:
            print(f"❌ [MessageService] 获取会话历史失败: {e}")
            if 'session' in locals():
                session.close()
            return []
    
    async def _get_location_entity_id(self, session, story_id: int, location_key: str) -> Optional[int]:
        """获取位置实体ID"""
        try:
            entity = session.query(Entity).filter(
                Entity.story_id == story_id,
                Entity.entity_type == 2,  # location
                Entity.key_name == location_key
            ).first()
            
            return entity.id if entity else None
            
        except Exception as e:
            print(f"❌ [MessageService] 获取位置实体ID失败: {e}")
            return None
    
    async def _get_npc_entity_id(self, session, story_id: int, npc_name: str) -> Optional[int]:
        """获取NPC实体ID"""
        try:
            # 尝试通过名称匹配
            entity = session.query(Entity).filter(
                Entity.story_id == story_id,
                Entity.entity_type == 1,  # npc
                Entity.name == npc_name
            ).first()
            
            return entity.id if entity else None
            
        except Exception as e:
            print(f"❌ [MessageService] 获取NPC实体ID失败: {e}")
            return None
    
    async def get_story_messages(
        self, 
        user_id: int, 
        story_id: int, 
        session_id: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        获取故事的消息历史
        
        Args:
            user_id: 用户ID
            story_id: 故事ID
            session_id: 会话ID（可选，为None时获取所有会话）
            limit: 限制返回数量
            offset: 偏移量
            
        Returns:
            包含消息列表和总数的字典
        """
        try:
            session = self.Session()
            
            # 构建查询条件
            query = session.query(Message).filter(
                Message.user_id == user_id,
                Message.story_id == story_id
            )
            
            if session_id:
                query = query.filter(Message.session_id == session_id)
            
            # 获取总数
            total_count = query.count()
            
            # 获取消息列表，按创建时间升序排列
            messages = query.order_by(Message.created_at.asc()).offset(offset).limit(limit).all()
            
            # 转换为字典格式，包含关联信息
            result_messages = []
            for msg in messages:
                msg_dict = msg.to_dict()
                
                # 添加消息类型名称
                try:
                    msg_type = session.query(MessageType).filter(MessageType.id == msg.message_type).first()
                    msg_dict['message_type_name'] = msg_type.type_name if msg_type else 'unknown'
                except:
                    msg_dict['message_type_name'] = 'unknown'
                
                # 添加相关实体名称
                if msg.related_entity:
                    try:
                        entity = session.query(Entity).filter(Entity.id == msg.related_entity).first()
                        msg_dict['related_entity_name'] = entity.name if entity else None
                    except:
                        msg_dict['related_entity_name'] = None
                
                # 添加位置名称
                if msg.location:
                    try:
                        location_entity = session.query(Entity).filter(Entity.id == msg.location).first()
                        msg_dict['location_name'] = location_entity.name if location_entity else None
                    except:
                        msg_dict['location_name'] = None
                
                result_messages.append(msg_dict)
            
            session.close()
            
            print(f"✅ [MessageService] 获取故事消息历史: 用户={user_id}, 故事={story_id}, 会话={session_id or 'ALL'}, 总数={total_count}, 返回={len(result_messages)}")
            
            return {
                "messages": result_messages,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + len(result_messages)) < total_count
            }
            
        except Exception as e:
            print(f"❌ [MessageService] 获取故事消息历史失败: {e}")
            if 'session' in locals():
                session.close()
            return {
                "messages": [],
                "total_count": 0,
                "limit": limit,
                "offset": offset,
                "has_more": False,
                "error": str(e)
            }
    
    async def get_latest_game_state(
        self, 
        user_id: int, 
        story_id: int, 
        session_id: str
    ) -> Dict[str, Any]:
        """
        从数据库获取最新的游戏状态
        
        Args:
            user_id: 用户ID
            story_id: 故事ID
            session_id: 会话ID
            
        Returns:
            包含最新游戏时间和玩家位置的字典
        """
        try:
            session = self.Session()
            
            # 获取最新的一条消息来确定游戏时间
            latest_message = session.query(Message).filter(
                Message.user_id == user_id,
                Message.story_id == story_id,
                Message.session_id == session_id
            ).order_by(desc(Message.game_time)).first()
            
            # 获取最新的移动消息来确定玩家位置
            latest_movement = session.query(Message).filter(
                Message.user_id == user_id,
                Message.story_id == story_id,
                Message.session_id == session_id,
                Message.message_type == 3,  # system_action
                Message.sub_type == "movement"
            ).order_by(desc(Message.game_time)).first()
            
            result = {
                "current_time": None,
                "player_location": None,
                "last_message_time": None
            }
            
            # 设置游戏时间
            if latest_message and latest_message.game_time:
                # 转换为字符串格式
                game_time = latest_message.game_time
                if hasattr(game_time, 'strftime'):
                    # 如果是datetime对象，格式化为字符串
                    # 使用游戏时间格式：只保留时分
                    result["current_time"] = TimeUtils.format_game_time(game_time, include_date=True)
                    result["last_message_time"] = latest_message.created_at.isoformat() if latest_message.created_at else None
                else:
                    # 如果已经是字符串
                    result["current_time"] = str(game_time)
                    result["last_message_time"] = latest_message.created_at.isoformat() if latest_message.created_at else None
            
            # 设置玩家位置
            if latest_movement and latest_movement.location:
                try:
                    # 根据移动消息的metadata获取新位置
                    metadata = latest_movement.message_metadata or {}
                    new_location = metadata.get("new_location")
                    
                    if new_location:
                        result["player_location"] = new_location
                    else:
                        # 如果metadata中没有新位置，尝试从location实体中获取
                        location_entity = session.query(Entity).filter(Entity.id == latest_movement.location).first()
                        if location_entity:
                            result["player_location"] = location_entity.key_name
                except Exception as e:
                    print(f"⚠️ 解析移动位置失败: {e}")
            
            # 如果没有找到移动记录，尝试从最新的任何消息中获取位置
            if not result["player_location"] and latest_message and latest_message.location:
                try:
                    location_entity = session.query(Entity).filter(Entity.id == latest_message.location).first()
                    if location_entity:
                        result["player_location"] = location_entity.key_name
                except Exception as e:
                    print(f"⚠️ 解析最新消息位置失败: {e}")
            
            session.close()
            
            print(f"✅ [MessageService] 获取最新游戏状态: 用户={user_id}, 会话={session_id}")
            print(f"    当前时间: {result['current_time']}")
            print(f"    玩家位置: {result['player_location']}")
            print(f"    最后消息时间: {result['last_message_time']}")
            
            return result
            
        except Exception as e:
            print(f"❌ [MessageService] 获取最新游戏状态失败: {e}")
            if 'session' in locals():
                session.close()
            return {
                "current_time": None,
                "player_location": None,
                "last_message_time": None,
                "error": str(e)
            }


# 创建全局实例
message_service = MessageService() 