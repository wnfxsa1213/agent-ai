"""
通用智能体框架 (Universal Agent Framework)
一个灵活、可扩展的通用智能体框架，旨在简化各种AI智能体的开发和部署。
"""

__version__ = "0.1.0"

# 导出主要的类和函数
from core.agent import Agent
from models.tool import Tool
from models.message import Message, Role
from core.config_manager import ConfigManager

# 便捷函数
def create_agent(name, description=None, model=None, tools=None):
    """
    创建一个新的智能体实例
    
    Args:
        name (str): 智能体名称
        description (str, optional): 智能体描述
        model (str, optional): 使用的模型名称
        tools (list, optional): 工具列表
        
    Returns:
        Agent: 智能体实例
    """
    return Agent(name=name, description=description, model=model, tools=tools) 