"""
缓存管理器模块
"""

import os
import json
import hashlib
import time
from typing import Dict, Any, Optional, Union
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    """
    缓存管理器类，用于缓存API请求和响应
    """
    
    def __init__(self, cache_dir: Optional[str] = None, expiry_days: int = 7):
        """
        初始化缓存管理器
        
        Args:
            cache_dir (str, optional): 缓存目录，如果为None，则使用默认目录
            expiry_days (int, optional): 缓存过期天数
        """
        # 默认缓存目录
        if cache_dir is None:
            self.cache_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                "cache"
            )
        else:
            self.cache_dir = cache_dir
            
        self.expiry_days = expiry_days
        
        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
                logger.info(f"已创建缓存目录: {self.cache_dir}")
            except Exception as e:
                logger.error(f"创建缓存目录失败: {e}")
    
    def _generate_cache_key(self, data: Dict[str, Any]) -> str:
        """
        生成缓存键
        
        Args:
            data (Dict[str, Any]): 请求数据
            
        Returns:
            str: 缓存键
        """
        # 将数据转换为JSON字符串
        data_str = json.dumps(data, sort_keys=True)
        
        # 计算哈希值
        hash_obj = hashlib.md5(data_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """
        获取缓存文件路径
        
        Args:
            cache_key (str): 缓存键
            
        Returns:
            str: 缓存文件路径
        """
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        获取缓存
        
        Args:
            data (Dict[str, Any]): 请求数据
            
        Returns:
            Optional[Dict[str, Any]]: 缓存数据，如果不存在则返回None
        """
        cache_key = self._generate_cache_key(data)
        cache_path = self._get_cache_path(cache_key)
        
        # 检查缓存文件是否存在
        if not os.path.exists(cache_path):
            return None
        
        try:
            # 读取缓存文件
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查缓存是否过期
            timestamp = cache_data.get('timestamp', 0)
            expiry_time = timestamp + self.expiry_days * 24 * 60 * 60
            
            if time.time() > expiry_time:
                logger.info(f"缓存已过期: {cache_key}")
                # 删除过期缓存
                os.remove(cache_path)
                return None
            
            logger.info(f"命中缓存: {cache_key}")
            return cache_data.get('response')
        except Exception as e:
            logger.error(f"读取缓存失败: {e}")
            return None
    
    def set(self, data: Dict[str, Any], response: Dict[str, Any]) -> None:
        """
        设置缓存
        
        Args:
            data (Dict[str, Any]): 请求数据
            response (Dict[str, Any]): 响应数据
        """
        cache_key = self._generate_cache_key(data)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            # 创建缓存数据
            cache_data = {
                'timestamp': time.time(),
                'request': data,
                'response': response
            }
            
            # 写入缓存文件
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"已缓存响应: {cache_key}")
        except Exception as e:
            logger.error(f"缓存响应失败: {e}")
    
    def clear(self, days: Optional[int] = None) -> int:
        """
        清理过期缓存
        
        Args:
            days (int, optional): 过期天数，如果为None，则使用默认过期天数
            
        Returns:
            int: 清理的缓存文件数量
        """
        if days is None:
            days = self.expiry_days
            
        count = 0
        expiry_time = time.time() - days * 24 * 60 * 60
        
        try:
            # 遍历缓存目录
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue
                    
                file_path = os.path.join(self.cache_dir, filename)
                
                # 检查文件修改时间
                if os.path.getmtime(file_path) < expiry_time:
                    os.remove(file_path)
                    count += 1
            
            logger.info(f"已清理 {count} 个过期缓存文件")
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            
        return count
    
    def clear_all(self) -> int:
        """
        清理所有缓存
        
        Returns:
            int: 清理的缓存文件数量
        """
        count = 0
        
        try:
            # 遍历缓存目录
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue
                    
                file_path = os.path.join(self.cache_dir, filename)
                os.remove(file_path)
                count += 1
            
            logger.info(f"已清理所有缓存文件，共 {count} 个")
        except Exception as e:
            logger.error(f"清理所有缓存失败: {e}")
            
        return count 