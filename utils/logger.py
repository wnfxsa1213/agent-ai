"""
日志工具模块
"""

import os
import logging
import logging.handlers
import colorlog
from typing import Optional

def setup_logger(
    name: str = "agent_framework",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name (str, optional): 日志记录器名称
        level (int, optional): 日志级别
        log_file (str, optional): 日志文件路径
        max_file_size (int, optional): 日志文件最大大小
        backup_count (int, optional): 备份文件数量
        format_string (str, optional): 日志格式字符串
        
    Returns:
        logging.Logger: 日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除现有处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 默认日志格式
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 控制台处理器（带颜色）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 颜色映射
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s" + format_string,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果提供了日志文件路径）
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except Exception as e:
                logger.warning(f"无法创建日志目录: {e}")
        
        # 创建轮转文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger 