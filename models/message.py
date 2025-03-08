"""
消息模型模块
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class Role(Enum):
    """
    消息角色枚举
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"

class Message:
    """
    消息类，表示智能体与用户之间的消息
    """
    
    def __init__(
        self, 
        role: Role, 
        content: str, 
        name: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_call_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        初始化消息
        
        Args:
            role (Role): 消息角色
            content (str): 消息内容
            name (str, optional): 消息发送者名称
            tool_calls (List[Dict[str, Any]], optional): 工具调用列表
            tool_call_id (str, optional): 工具调用ID
            metadata (Dict[str, Any], optional): 元数据
        """
        self.role = role
        self.content = content
        self.name = name
        self.tool_calls = tool_calls or []
        self.tool_call_id = tool_call_id
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        message_dict = {
            "role": self.role.value,
            "content": self.content,
        }
        
        if self.name:
            message_dict["name"] = self.name
            
        if self.tool_calls:
            message_dict["tool_calls"] = self.tool_calls
            
        if self.tool_call_id:
            message_dict["tool_call_id"] = self.tool_call_id
            
        return message_dict
    
    def to_openai_message(self) -> Dict[str, Any]:
        """
        转换为OpenAI消息格式
        
        Returns:
            Dict[str, Any]: OpenAI消息格式
        """
        return self.to_dict()
    
    def to_claude_message(self) -> Dict[str, Any]:
        """
        转换为Claude消息格式
        
        Returns:
            Dict[str, Any]: Claude消息格式
        """
        # Claude使用不同的格式
        if self.role == Role.SYSTEM:
            return {"role": "system", "content": self.content}
        elif self.role == Role.USER:
            return {"role": "user", "content": self.content}
        elif self.role == Role.ASSISTANT:
            return {"role": "assistant", "content": self.content}
        elif self.role == Role.TOOL or self.role == Role.FUNCTION:
            # Claude目前不直接支持工具消息，将其转换为用户消息
            return {
                "role": "user", 
                "content": f"工具结果: {self.content}"
            }
        else:
            return {"role": "user", "content": self.content}
    
    def to_json(self) -> str:
        """
        转换为JSON字符串
        
        Returns:
            str: JSON字符串
        """
        message_dict = self.to_dict()
        message_dict["timestamp"] = self.timestamp
        message_dict["metadata"] = self.metadata
        return json.dumps(message_dict, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        从字典创建消息
        
        Args:
            data (Dict[str, Any]): 字典数据
            
        Returns:
            Message: 消息实例
        """
        role = Role(data.get("role", "user"))
        content = data.get("content", "")
        name = data.get("name")
        tool_calls = data.get("tool_calls", [])
        tool_call_id = data.get("tool_call_id")
        metadata = data.get("metadata", {})
        
        message = cls(
            role=role,
            content=content,
            name=name,
            tool_calls=tool_calls,
            tool_call_id=tool_call_id,
            metadata=metadata
        )
        
        if "timestamp" in data:
            message.timestamp = data["timestamp"]
            
        return message
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """
        从JSON字符串创建消息
        
        Args:
            json_str (str): JSON字符串
            
        Returns:
            Message: 消息实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def system(cls, content: str, metadata: Optional[Dict[str, Any]] = None) -> 'Message':
        """
        创建系统消息
        
        Args:
            content (str): 消息内容
            metadata (Dict[str, Any], optional): 元数据
            
        Returns:
            Message: 系统消息
        """
        return cls(role=Role.SYSTEM, content=content, metadata=metadata)
    
    @classmethod
    def user(cls, content: str, metadata: Optional[Dict[str, Any]] = None) -> 'Message':
        """
        创建用户消息
        
        Args:
            content (str): 消息内容
            metadata (Dict[str, Any], optional): 元数据
            
        Returns:
            Message: 用户消息
        """
        return cls(role=Role.USER, content=content, metadata=metadata)
    
    @classmethod
    def assistant(cls, content: str, metadata: Optional[Dict[str, Any]] = None) -> 'Message':
        """
        创建助手消息
        
        Args:
            content (str): 消息内容
            metadata (Dict[str, Any], optional): 元数据
            
        Returns:
            Message: 助手消息
        """
        return cls(role=Role.ASSISTANT, content=content, metadata=metadata)
    
    @classmethod
    def tool(cls, content: str, tool_call_id: str, metadata: Optional[Dict[str, Any]] = None) -> 'Message':
        """
        创建工具消息
        
        Args:
            content (str): 消息内容
            tool_call_id (str): 工具调用ID
            metadata (Dict[str, Any], optional): 元数据
            
        Returns:
            Message: 工具消息
        """
        return cls(
            role=Role.TOOL, 
            content=content, 
            tool_call_id=tool_call_id,
            metadata=metadata
        ) 