"""
智能体核心模块
"""

import os
import json
import uuid
import time
from typing import Dict, Any, List, Optional, Union, Callable
import logging
from datetime import datetime
import re

from openai import OpenAI
from anthropic import Anthropic

from core.config_manager import ConfigManager
from models.message import Message, Role
from models.tool import Tool
from memory.memory_manager import MemoryManager
from cache.cache_manager import CacheManager
from utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger(name="agent_framework.agent")

class Agent:
    """
    智能体类，表示一个可以与用户交互的AI助手
    """
    
    def __init__(
        self, 
        name: str,
        description: Optional[str] = None,
        model: Optional[str] = None,
        tools: Optional[List[Tool]] = None,
        config_path: Optional[str] = None,
        memory_capacity: int = 10,
        enable_long_term_memory: bool = True,
        enable_cache: bool = True,
        system_prompt: Optional[str] = None
    ):
        """
        初始化智能体
        
        Args:
            name (str): 智能体名称
            description (str, optional): 智能体描述
            model (str, optional): 使用的模型名称
            tools (List[Tool], optional): 工具列表
            config_path (str, optional): 配置文件路径
            memory_capacity (int, optional): 短期记忆容量
            enable_long_term_memory (bool, optional): 是否启用长期记忆
            enable_cache (bool, optional): 是否启用缓存
            system_prompt (str, optional): 系统提示
        """
        self.name = name
        self.description = description or f"{name} 智能体"
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()
        
        # 加载配置
        self.config = ConfigManager(config_path=config_path)
        
        # 设置模型
        self.model = model or self.config.get("API", "default_model", "openai")
        
        # 初始化客户端
        self._init_clients()
        
        # 设置工具
        self.tools = tools or []
        
        # 初始化记忆管理器
        self.memory = MemoryManager(
            short_term_capacity=memory_capacity,
            long_term_enabled=enable_long_term_memory
        )
        
        # 设置会话ID
        self.conversation_id = str(uuid.uuid4())
        self.memory.set_conversation(self.conversation_id)
        
        # 初始化缓存管理器
        self.enable_cache = enable_cache
        if enable_cache:
            cache_dir = self.config.get("CACHE", "directory", "./cache")
            expiry_days = self.config.getint("CACHE", "expiry_days", 7)
            self.cache = CacheManager(cache_dir=cache_dir, expiry_days=expiry_days)
        else:
            self.cache = None
            
        # 设置系统提示
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
        # 添加系统消息
        self.memory.add(Message.system(self.system_prompt))
        
        logger.info(f"已初始化智能体: {self.name}")
    
    def _init_clients(self) -> None:
        """
        初始化API客户端
        """
        # 获取模型配置
        model_config = self.config.get_model_config(self.model)
        
        # 初始化OpenAI客户端
        if self.model == "openai":
            self.openai_client = OpenAI(
                api_key=model_config["api_key"],
                base_url=model_config["api_base"]
            )
        else:
            self.openai_client = None
            
        # 初始化Claude客户端
        if self.model == "claude":
            self.claude_client = Anthropic(
                api_key=model_config["api_key"]
            )
        else:
            self.claude_client = None
    
    def _get_default_system_prompt(self) -> str:
        """
        获取默认系统提示
        
        Returns:
            str: 默认系统提示
        """
        return f"""你是一个名为 {self.name} 的智能助手。
{self.description}

当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请尽可能地提供有用、安全和诚实的回答。如果你不知道某个问题的答案，请坦率地承认，而不要试图编造信息。"""
    
    def add_tool(self, tool: Tool) -> None:
        """
        添加工具
        
        Args:
            tool (Tool): 工具
        """
        self.tools.append(tool)
        logger.info(f"已添加工具: {tool.name}")
    
    def add_tools(self, tools: List[Tool]) -> None:
        """
        添加多个工具
        
        Args:
            tools (List[Tool]): 工具列表
        """
        self.tools.extend(tools)
        logger.info(f"已添加 {len(tools)} 个工具")
    
    def run(self, input_text: str) -> str:
        """
        运行智能体
        
        Args:
            input_text (str): 用户输入
            
        Returns:
            str: 智能体响应
        """
        # 添加用户消息
        user_message = Message.user(input_text)
        self.memory.add(user_message)
        
        # 获取所有消息
        messages = self.memory.get_messages()
        
        # 调用模型
        response = self._call_model(messages)
        
        # 处理工具调用
        if response.tool_calls:
            response = self._handle_tool_calls(response)
        
        # 添加助手消息
        self.memory.add(response)
        
        return response.content
    
    def _call_model(self, messages: List[Message]) -> Message:
        """
        调用模型
        
        Args:
            messages (List[Message]): 消息列表
            
        Returns:
            Message: 模型响应
        """
        # 获取模型配置
        model_config = self.config.get_model_config(self.model)
        
        # 准备请求数据
        request_data = {
            "model": model_config["model"],
            "messages": [message.to_dict() for message in messages],
            "temperature": model_config["temperature"],
            "max_tokens": model_config["max_tokens"]
        }
        
        # 如果有工具，则添加工具
        if self.tools:
            if self.model == "openai":
                request_data["tools"] = [tool.to_openai_tool() for tool in self.tools]
                request_data["tool_choice"] = "auto"
        
        # 检查缓存
        if self.enable_cache:
            cached_response = self.cache.get(request_data)
            if cached_response:
                logger.info("使用缓存的响应")
                return Message.from_dict(cached_response)
        
        # 调用模型
        try:
            if self.model == "openai":
                return self._call_openai(request_data)
            elif self.model == "claude":
                return self._call_claude(request_data, messages)
            else:
                raise ValueError(f"不支持的模型: {self.model}")
        except Exception as e:
            logger.error(f"调用模型失败: {e}")
            return Message.assistant(f"抱歉，我遇到了一个错误: {str(e)}")
    
    def _call_openai(self, request_data: Dict[str, Any]) -> Message:
        """
        调用OpenAI模型
        
        Args:
            request_data (Dict[str, Any]): 请求数据
            
        Returns:
            Message: 模型响应
        """
        logger.info(f"调用OpenAI模型: {request_data['model']}")
        
        response = self.openai_client.chat.completions.create(**request_data)
        
        # 解析响应
        message = response.choices[0].message
        
        # 创建消息
        assistant_message = Message(
            role=Role.ASSISTANT,
            content=message.content or "",
            tool_calls=message.tool_calls
        )
        
        # 缓存响应
        if self.enable_cache:
            self.cache.set(request_data, assistant_message.to_dict())
        
        return assistant_message
    
    def _call_claude(self, request_data: Dict[str, Any], messages: List[Message]) -> Message:
        """
        调用Claude模型
        
        Args:
            request_data (Dict[str, Any]): 请求数据
            messages (List[Message]): 消息列表
            
        Returns:
            Message: 模型响应
        """
        logger.info(f"调用Claude模型: {request_data['model']}")
        
        # Claude使用不同的消息格式
        claude_messages = [message.to_claude_message() for message in messages]
        
        # 创建Claude请求
        claude_request = {
            "model": request_data["model"],
            "messages": claude_messages,
            "temperature": request_data["temperature"],
            "max_tokens": request_data["max_tokens"]
        }
        
        response = self.claude_client.messages.create(**claude_request)
        
        # 创建消息
        assistant_message = Message(
            role=Role.ASSISTANT,
            content=response.content[0].text
        )
        
        # 缓存响应
        if self.enable_cache:
            self.cache.set(request_data, assistant_message.to_dict())
        
        return assistant_message
    
    def _handle_tool_calls(self, message: Message) -> Message:
        """
        处理工具调用
        
        Args:
            message (Message): 消息
            
        Returns:
            Message: 处理后的消息
        """
        if not message.tool_calls:
            return message
            
        logger.info(f"处理 {len(message.tool_calls)} 个工具调用")
        
        # 添加助手消息
        self.memory.add(message)
        
        # 处理每个工具调用
        for tool_call in message.tool_calls:
            function = tool_call.function
            tool_name = function.name
            tool_args = json.loads(function.arguments)
            tool_call_id = tool_call.id
            
            # 查找工具
            tool = next((t for t in self.tools if t.name == tool_name), None)
            
            if tool:
                try:
                    # 调用工具
                    logger.info(f"调用工具: {tool_name}")
                    result = tool(**tool_args)
                    
                    # 添加工具消息
                    tool_message = Message.tool(
                        content=str(result),
                        tool_call_id=tool_call_id
                    )
                    
                    self.memory.add(tool_message)
                except Exception as e:
                    # 添加错误消息
                    error_message = Message.tool(
                        content=f"工具调用失败: {str(e)}",
                        tool_call_id=tool_call_id
                    )
                    
                    self.memory.add(error_message)
            else:
                # 添加错误消息
                error_message = Message.tool(
                    content=f"找不到工具: {tool_name}",
                    tool_call_id=tool_call_id
                )
                
                self.memory.add(error_message)
        
        # 获取所有消息
        messages = self.memory.get_messages()
        
        # 再次调用模型
        return self._call_model(messages)
    
    def clear_memory(self) -> None:
        """
        清空短期记忆
        """
        self.memory.clear_short_term()
        
        # 添加系统消息
        self.memory.add(Message.system(self.system_prompt))
        
        logger.info("已清空短期记忆")
    
    def new_conversation(self) -> None:
        """
        开始新会话
        """
        self.conversation_id = str(uuid.uuid4())
        self.memory.set_conversation(self.conversation_id)
        
        # 添加系统消息
        self.memory.add(Message.system(self.system_prompt))
        
        logger.info(f"已开始新会话: {self.conversation_id}")
    
    def load_conversation(self, conversation_id: str) -> bool:
        """
        加载会话
        
        Args:
            conversation_id (str): 会话ID
            
        Returns:
            bool: 是否成功
        """
        self.conversation_id = conversation_id
        self.memory.set_conversation(conversation_id)
        
        logger.info(f"已加载会话: {conversation_id}")
        return True
    
    def get_conversations(self) -> List[Dict[str, Any]]:
        """
        获取所有会话
        
        Returns:
            List[Dict[str, Any]]: 会话列表
        """
        return self.memory.get_conversations()
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除会话
        
        Args:
            conversation_id (str): 会话ID
            
        Returns:
            bool: 是否成功
        """
        return self.memory.delete_conversation(conversation_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "created_at": self.created_at,
            "conversation_id": self.conversation_id,
            "system_prompt": self.system_prompt,
            "tools": [tool.to_dict() for tool in self.tools]
        }
    
    def to_json(self) -> str:
        """
        转换为JSON字符串
        
        Returns:
            str: JSON字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False) 