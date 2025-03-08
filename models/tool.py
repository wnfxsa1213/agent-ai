"""
工具模型模块
"""

import inspect
from typing import Dict, Any, List, Callable, Optional, Union, get_type_hints
import json
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class Tool:
    """
    工具类，表示智能体可以使用的工具
    """
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        function: Callable,
        parameters: Optional[Dict[str, Any]] = None,
        required_parameters: Optional[List[str]] = None,
        return_direct: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        初始化工具
        
        Args:
            name (str): 工具名称
            description (str): 工具描述
            function (Callable): 工具函数
            parameters (Dict[str, Any], optional): 参数定义
            required_parameters (List[str], optional): 必需参数列表
            return_direct (bool, optional): 是否直接返回结果
            metadata (Dict[str, Any], optional): 元数据
        """
        self.name = name
        self.description = description
        self.function = function
        self.return_direct = return_direct
        self.metadata = metadata or {}
        
        # 如果没有提供参数定义，则从函数签名中提取
        if parameters is None:
            self.parameters = self._extract_parameters_from_function()
        else:
            self.parameters = parameters
            
        # 如果没有提供必需参数列表，则从参数定义中提取
        if required_parameters is None:
            self.required_parameters = self._extract_required_parameters()
        else:
            self.required_parameters = required_parameters
    
    def _extract_parameters_from_function(self) -> Dict[str, Any]:
        """
        从函数签名中提取参数定义
        
        Returns:
            Dict[str, Any]: 参数定义
        """
        parameters = {}
        signature = inspect.signature(self.function)
        type_hints = get_type_hints(self.function)
        
        for name, param in signature.parameters.items():
            # 跳过self参数
            if name == "self":
                continue
                
            param_type = type_hints.get(name, Any).__name__ if name in type_hints else "string"
            param_default = None if param.default is inspect.Parameter.empty else param.default
            
            parameters[name] = {
                "type": param_type,
                "description": "",
                "default": param_default
            }
            
        return parameters
    
    def _extract_required_parameters(self) -> List[str]:
        """
        从参数定义中提取必需参数列表
        
        Returns:
            List[str]: 必需参数列表
        """
        required = []
        signature = inspect.signature(self.function)
        
        for name, param in signature.parameters.items():
            # 跳过self参数
            if name == "self":
                continue
                
            # 如果参数没有默认值，则为必需参数
            if param.default is inspect.Parameter.empty:
                required.append(name)
                
        return required
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.parameters,
                "required": self.required_parameters
            }
        }
    
    def to_openai_tool(self) -> Dict[str, Any]:
        """
        转换为OpenAI工具格式
        
        Returns:
            Dict[str, Any]: OpenAI工具格式
        """
        return {
            "type": "function",
            "function": self.to_dict()
        }
    
    def to_json(self) -> str:
        """
        转换为JSON字符串
        
        Returns:
            str: JSON字符串
        """
        tool_dict = self.to_dict()
        tool_dict["metadata"] = self.metadata
        return json.dumps(tool_dict, ensure_ascii=False)
    
    def __call__(self, *args, **kwargs) -> Any:
        """
        调用工具函数
        
        Returns:
            Any: 工具函数返回值
        """
        try:
            return self.function(*args, **kwargs)
        except Exception as e:
            logger.error(f"工具 {self.name} 调用失败: {e}")
            return f"工具调用失败: {str(e)}"
    
    @classmethod
    def from_function(
        cls, 
        function: Callable, 
        name: Optional[str] = None, 
        description: Optional[str] = None,
        return_direct: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'Tool':
        """
        从函数创建工具
        
        Args:
            function (Callable): 工具函数
            name (str, optional): 工具名称
            description (str, optional): 工具描述
            return_direct (bool, optional): 是否直接返回结果
            metadata (Dict[str, Any], optional): 元数据
            
        Returns:
            Tool: 工具实例
        """
        if name is None:
            name = function.__name__
            
        if description is None:
            description = function.__doc__ or f"执行 {name} 函数"
            
        return cls(
            name=name,
            description=description,
            function=function,
            return_direct=return_direct,
            metadata=metadata
        )


def tool(
    name: Optional[str] = None, 
    description: Optional[str] = None,
    return_direct: bool = False,
    metadata: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    工具装饰器，用于将函数转换为工具
    
    Args:
        name (str, optional): 工具名称
        description (str, optional): 工具描述
        return_direct (bool, optional): 是否直接返回结果
        metadata (Dict[str, Any], optional): 元数据
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(function: Callable) -> Tool:
        """
        装饰器函数
        
        Args:
            function (Callable): 工具函数
            
        Returns:
            Tool: 工具实例
        """
        _name = name or function.__name__
        _description = description or function.__doc__ or f"执行 {_name} 函数"
        
        @wraps(function)
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)
        
        tool_instance = Tool(
            name=_name,
            description=_description,
            function=wrapper,
            return_direct=return_direct,
            metadata=metadata
        )
        
        wrapper.tool = tool_instance
        return wrapper
    
    return decorator 