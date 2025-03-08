"""
配置管理器模块
"""

import os
import configparser
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    配置管理器类，用于加载和管理配置
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path (str, optional): 配置文件路径，如果为None，则使用默认路径
        """
        self.config = configparser.ConfigParser()
        
        # 默认配置文件路径
        if config_path is None:
            self.config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                "config.ini"
            )
        else:
            self.config_path = config_path
            
        # 加载配置
        self.load_config()
        
    def load_config(self) -> None:
        """
        加载配置文件
        """
        if os.path.exists(self.config_path):
            try:
                self.config.read(self.config_path)
                logger.info(f"已加载配置文件: {self.config_path}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
                # 加载默认配置
                self._load_default_config()
        else:
            logger.warning(f"配置文件不存在: {self.config_path}，将使用默认配置")
            # 加载默认配置
            self._load_default_config()
    
    def _load_default_config(self) -> None:
        """
        加载默认配置
        """
        # API配置
        self.config["API"] = {
            "openai_api_key": "",
            "openai_api_base": "https://api.openai.com/v1",
            "openai_model": "gpt-4o",
            "openai_timeout": "30",
            "openai_temperature": "0.7",
            "openai_max_tokens": "2000",
            "openai_top_p": "1.0",
            "openai_frequency_penalty": "0.0",
            "openai_presence_penalty": "0.0",
            "claude_api_key": "",
            "claude_api_base": "https://api.anthropic.com/v1/",
            "claude_model": "claude-3-opus-20240229",
            "claude_timeout": "30",
            "claude_temperature": "0.7",
            "claude_max_tokens": "2000",
            "max_retries": "3",
            "retry_delay": "2",
            "proxy": "",
            "default_model": "openai"
        }
        
        # 缓存配置
        self.config["CACHE"] = {
            "enabled": "true",
            "expiry_days": "7",
            "directory": "./cache"
        }
        
        # 记忆配置
        self.config["MEMORY"] = {
            "short_term_capacity": "10",
            "long_term_enabled": "true",
            "long_term_db_path": "./memory/agent_memory.db",
            "vector_dimension": "1536"
        }
        
        # 日志配置
        self.config["LOGGING"] = {
            "level": "INFO",
            "file": "./logs/agent.log",
            "max_file_size": "10485760",
            "backup_count": "5",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
        
        # 工具配置
        self.config["TOOLS"] = {
            "auto_load": "true",
            "tools_dir": "./tools"
        }
        
        # 执行配置
        self.config["EXECUTION"] = {
            "timeout": "60",
            "max_iterations": "10",
            "allow_parallel": "true",
            "max_parallel_tasks": "5"
        }
        
        # 保存默认配置
        try:
            with open(self.config_path, 'w') as f:
                self.config.write(f)
            logger.info(f"已保存默认配置到: {self.config_path}")
        except Exception as e:
            logger.error(f"保存默认配置失败: {e}")
    
    def get(self, section: str, option: str, fallback: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            section (str): 配置节
            option (str): 配置项
            fallback (Any, optional): 默认值
            
        Returns:
            Any: 配置值
        """
        return self.config.get(section, option, fallback=fallback)
    
    def getint(self, section: str, option: str, fallback: int = None) -> int:
        """
        获取整数配置项
        
        Args:
            section (str): 配置节
            option (str): 配置项
            fallback (int, optional): 默认值
            
        Returns:
            int: 配置值
        """
        return self.config.getint(section, option, fallback=fallback)
    
    def getfloat(self, section: str, option: str, fallback: float = None) -> float:
        """
        获取浮点数配置项
        
        Args:
            section (str): 配置节
            option (str): 配置项
            fallback (float, optional): 默认值
            
        Returns:
            float: 配置值
        """
        return self.config.getfloat(section, option, fallback=fallback)
    
    def getboolean(self, section: str, option: str, fallback: bool = None) -> bool:
        """
        获取布尔配置项
        
        Args:
            section (str): 配置节
            option (str): 配置项
            fallback (bool, optional): 默认值
            
        Returns:
            bool: 配置值
        """
        return self.config.getboolean(section, option, fallback=fallback)
    
    def set(self, section: str, option: str, value: Any) -> None:
        """
        设置配置项
        
        Args:
            section (str): 配置节
            option (str): 配置项
            value (Any): 配置值
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, option, str(value))
    
    def save(self) -> None:
        """
        保存配置到文件
        """
        try:
            with open(self.config_path, 'w') as f:
                self.config.write(f)
            logger.info(f"已保存配置到: {self.config_path}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def get_api_key(self, provider: str = None) -> str:
        """
        获取API密钥
        
        Args:
            provider (str, optional): 提供商名称，如果为None，则使用默认提供商
            
        Returns:
            str: API密钥
        """
        if provider is None:
            provider = self.get("API", "default_model", "openai")
        
        # 从环境变量获取API密钥
        env_var = f"{provider.upper()}_API_KEY"
        api_key = os.environ.get(env_var)
        
        # 如果环境变量中没有，则从配置文件获取
        if not api_key:
            api_key = self.get("API", f"{provider}_api_key", "")
        
        return api_key
    
    def get_model_config(self, provider: str = None) -> Dict[str, Any]:
        """
        获取模型配置
        
        Args:
            provider (str, optional): 提供商名称，如果为None，则使用默认提供商
            
        Returns:
            Dict[str, Any]: 模型配置
        """
        if provider is None:
            provider = self.get("API", "default_model", "openai")
        
        config = {
            "api_key": self.get_api_key(provider),
            "api_base": self.get("API", f"{provider}_api_base", ""),
            "model": self.get("API", f"{provider}_model", ""),
            "timeout": self.getint("API", f"{provider}_timeout", 30),
            "temperature": self.getfloat("API", f"{provider}_temperature", 0.7),
            "max_tokens": self.getint("API", f"{provider}_max_tokens", 2000),
        }
        
        # OpenAI特有配置
        if provider == "openai":
            config.update({
                "top_p": self.getfloat("API", "openai_top_p", 1.0),
                "frequency_penalty": self.getfloat("API", "openai_frequency_penalty", 0.0),
                "presence_penalty": self.getfloat("API", "openai_presence_penalty", 0.0),
            })
        
        return config 