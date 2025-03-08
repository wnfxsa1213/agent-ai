"""
记忆管理器模块
"""

import os
import json
import sqlite3
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime
from collections import deque

from agent_framework.models.message import Message

logger = logging.getLogger(__name__)

class ShortTermMemory:
    """
    短期记忆类，用于存储最近的消息
    """
    
    def __init__(self, capacity: int = 10):
        """
        初始化短期记忆
        
        Args:
            capacity (int, optional): 容量
        """
        self.capacity = capacity
        self.messages = deque(maxlen=capacity)
    
    def add(self, message: Message) -> None:
        """
        添加消息
        
        Args:
            message (Message): 消息
        """
        self.messages.append(message)
    
    def get_all(self) -> List[Message]:
        """
        获取所有消息
        
        Returns:
            List[Message]: 消息列表
        """
        return list(self.messages)
    
    def clear(self) -> None:
        """
        清空短期记忆
        """
        self.messages.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            'capacity': self.capacity,
            'messages': [message.to_dict() for message in self.messages]
        }
    
    def to_json(self) -> str:
        """
        转换为JSON字符串
        
        Returns:
            str: JSON字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShortTermMemory':
        """
        从字典创建短期记忆
        
        Args:
            data (Dict[str, Any]): 字典数据
            
        Returns:
            ShortTermMemory: 短期记忆实例
        """
        memory = cls(capacity=data.get('capacity', 10))
        
        for message_data in data.get('messages', []):
            memory.add(Message.from_dict(message_data))
            
        return memory
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ShortTermMemory':
        """
        从JSON字符串创建短期记忆
        
        Args:
            json_str (str): JSON字符串
            
        Returns:
            ShortTermMemory: 短期记忆实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


class LongTermMemory:
    """
    长期记忆类，用于存储历史消息
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化长期记忆
        
        Args:
            db_path (str, optional): 数据库路径，如果为None，则使用默认路径
        """
        # 默认数据库路径
        if db_path is None:
            memory_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                "memory"
            )
            
            # 确保目录存在
            if not os.path.exists(memory_dir):
                try:
                    os.makedirs(memory_dir)
                    logger.info(f"已创建记忆目录: {memory_dir}")
                except Exception as e:
                    logger.error(f"创建记忆目录失败: {e}")
            
            self.db_path = os.path.join(memory_dir, "agent_memory.db")
        else:
            self.db_path = db_path
            
        # 初始化数据库
        self._init_db()
    
    def _init_db(self) -> None:
        """
        初始化数据库
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建消息表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                name TEXT,
                timestamp TEXT,
                metadata TEXT
            )
            ''')
            
            # 创建会话表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TEXT,
                updated_at TEXT,
                metadata TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info(f"已初始化长期记忆数据库: {self.db_path}")
        except Exception as e:
            logger.error(f"初始化长期记忆数据库失败: {e}")
    
    def add(self, message: Message, conversation_id: str) -> None:
        """
        添加消息
        
        Args:
            message (Message): 消息
            conversation_id (str): 会话ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 插入消息
            cursor.execute(
                '''
                INSERT INTO messages (conversation_id, role, content, name, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (
                    conversation_id,
                    message.role.value,
                    message.content,
                    message.name,
                    message.timestamp,
                    json.dumps(message.metadata, ensure_ascii=False)
                )
            )
            
            # 更新会话的更新时间
            cursor.execute(
                '''
                UPDATE conversations SET updated_at = ? WHERE id = ?
                ''',
                (datetime.now().isoformat(), conversation_id)
            )
            
            # 如果会话不存在，则创建
            if cursor.rowcount == 0:
                cursor.execute(
                    '''
                    INSERT INTO conversations (id, title, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (
                        conversation_id,
                        f"会话 {conversation_id}",
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        '{}'
                    )
                )
            
            conn.commit()
            conn.close()
            
            logger.info(f"已添加消息到长期记忆: {conversation_id}")
        except Exception as e:
            logger.error(f"添加消息到长期记忆失败: {e}")
    
    def get_conversation(self, conversation_id: str) -> List[Message]:
        """
        获取会话消息
        
        Args:
            conversation_id (str): 会话ID
            
        Returns:
            List[Message]: 消息列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询消息
            cursor.execute(
                '''
                SELECT role, content, name, timestamp, metadata
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id
                ''',
                (conversation_id,)
            )
            
            messages = []
            for row in cursor.fetchall():
                role, content, name, timestamp, metadata = row
                
                message = Message(
                    role=role,
                    content=content,
                    name=name,
                    metadata=json.loads(metadata) if metadata else {}
                )
                
                message.timestamp = timestamp
                messages.append(message)
            
            conn.close()
            
            logger.info(f"已获取会话消息: {conversation_id}, 共 {len(messages)} 条")
            return messages
        except Exception as e:
            logger.error(f"获取会话消息失败: {e}")
            return []
    
    def get_conversations(self) -> List[Dict[str, Any]]:
        """
        获取所有会话
        
        Returns:
            List[Dict[str, Any]]: 会话列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询会话
            cursor.execute(
                '''
                SELECT id, title, created_at, updated_at, metadata
                FROM conversations
                ORDER BY updated_at DESC
                '''
            )
            
            conversations = []
            for row in cursor.fetchall():
                id, title, created_at, updated_at, metadata = row
                
                conversations.append({
                    'id': id,
                    'title': title,
                    'created_at': created_at,
                    'updated_at': updated_at,
                    'metadata': json.loads(metadata) if metadata else {}
                })
            
            conn.close()
            
            logger.info(f"已获取所有会话，共 {len(conversations)} 个")
            return conversations
        except Exception as e:
            logger.error(f"获取所有会话失败: {e}")
            return []
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除会话
        
        Args:
            conversation_id (str): 会话ID
            
        Returns:
            bool: 是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 删除消息
            cursor.execute(
                '''
                DELETE FROM messages WHERE conversation_id = ?
                ''',
                (conversation_id,)
            )
            
            # 删除会话
            cursor.execute(
                '''
                DELETE FROM conversations WHERE id = ?
                ''',
                (conversation_id,)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"已删除会话: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False
    
    def clear_all(self) -> bool:
        """
        清空所有记忆
        
        Returns:
            bool: 是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 删除所有消息
            cursor.execute('DELETE FROM messages')
            
            # 删除所有会话
            cursor.execute('DELETE FROM conversations')
            
            conn.commit()
            conn.close()
            
            logger.info("已清空所有长期记忆")
            return True
        except Exception as e:
            logger.error(f"清空所有长期记忆失败: {e}")
            return False


class MemoryManager:
    """
    记忆管理器类，用于管理智能体的短期和长期记忆
    """
    
    def __init__(
        self, 
        short_term_capacity: int = 10,
        long_term_enabled: bool = True,
        long_term_db_path: Optional[str] = None
    ):
        """
        初始化记忆管理器
        
        Args:
            short_term_capacity (int, optional): 短期记忆容量
            long_term_enabled (bool, optional): 是否启用长期记忆
            long_term_db_path (str, optional): 长期记忆数据库路径
        """
        self.short_term = ShortTermMemory(capacity=short_term_capacity)
        self.long_term_enabled = long_term_enabled
        
        if long_term_enabled:
            self.long_term = LongTermMemory(db_path=long_term_db_path)
        else:
            self.long_term = None
            
        self.current_conversation_id = None
    
    def add(self, message: Message) -> None:
        """
        添加消息
        
        Args:
            message (Message): 消息
        """
        # 添加到短期记忆
        self.short_term.add(message)
        
        # 如果启用了长期记忆，则添加到长期记忆
        if self.long_term_enabled and self.current_conversation_id:
            self.long_term.add(message, self.current_conversation_id)
    
    def get_messages(self) -> List[Message]:
        """
        获取短期记忆中的所有消息
        
        Returns:
            List[Message]: 消息列表
        """
        return self.short_term.get_all()
    
    def clear_short_term(self) -> None:
        """
        清空短期记忆
        """
        self.short_term.clear()
    
    def set_conversation(self, conversation_id: str) -> None:
        """
        设置当前会话ID
        
        Args:
            conversation_id (str): 会话ID
        """
        self.current_conversation_id = conversation_id
        
        # 如果启用了长期记忆，则加载会话消息到短期记忆
        if self.long_term_enabled and conversation_id:
            self.clear_short_term()
            
            for message in self.long_term.get_conversation(conversation_id):
                self.short_term.add(message)
    
    def get_conversations(self) -> List[Dict[str, Any]]:
        """
        获取所有会话
        
        Returns:
            List[Dict[str, Any]]: 会话列表
        """
        if self.long_term_enabled:
            return self.long_term.get_conversations()
        else:
            return []
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除会话
        
        Args:
            conversation_id (str): 会话ID
            
        Returns:
            bool: 是否成功
        """
        if self.long_term_enabled:
            return self.long_term.delete_conversation(conversation_id)
        else:
            return False
    
    def clear_all(self) -> bool:
        """
        清空所有记忆
        
        Returns:
            bool: 是否成功
        """
        self.clear_short_term()
        
        if self.long_term_enabled:
            return self.long_term.clear_all()
        else:
            return True 