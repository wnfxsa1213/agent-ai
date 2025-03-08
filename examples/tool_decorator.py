"""
工具装饰器示例
"""

import os
import sys
import time
import requests
from datetime import datetime

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent_framework import Agent, tool

@tool(name="calculator", description="计算数学表达式，例如: 1 + 2 * 3")
def calculator(expression: str) -> str:
    """
    计算数学表达式
    
    Args:
        expression (str): 数学表达式
        
    Returns:
        str: 计算结果
    """
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算失败: {str(e)}"

@tool(name="get_current_time", description="获取当前时间")
def get_current_time() -> str:
    """
    获取当前时间
    
    Returns:
        str: 当前时间
    """
    return f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

@tool(name="get_weather", description="获取指定城市的天气信息")
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息
    
    Args:
        city (str): 城市名称
        
    Returns:
        str: 天气信息
    """
    try:
        # 这里使用一个模拟的天气API
        # 在实际应用中，你应该使用真实的天气API
        weather_data = {
            "北京": "晴天，温度25°C",
            "上海": "多云，温度28°C",
            "广州": "小雨，温度30°C",
            "深圳": "阴天，温度29°C"
        }
        
        if city in weather_data:
            return f"{city}的天气: {weather_data[city]}"
        else:
            return f"抱歉，没有找到{city}的天气信息"
    except Exception as e:
        return f"获取天气失败: {str(e)}"

@tool(name="search_web", description="搜索网络信息")
def search_web(query: str) -> str:
    """
    搜索网络信息
    
    Args:
        query (str): 搜索查询
        
    Returns:
        str: 搜索结果
    """
    # 这里使用一个模拟的搜索结果
    # 在实际应用中，你应该使用真实的搜索API
    return f"关于\"{query}\"的搜索结果:\n1. 模拟搜索结果1\n2. 模拟搜索结果2\n3. 模拟搜索结果3"

def main():
    """
    主函数
    """
    # 创建智能体
    agent = Agent(
        name="多功能助手",
        description="一个可以帮助你解决各种问题的智能助手",
        tools=[
            calculator.tool,
            get_current_time.tool,
            get_weather.tool,
            search_web.tool
        ]
    )
    
    print(f"欢迎使用 {agent.name}！")
    print(f"{agent.description}")
    print("可用工具:")
    for tool in agent.tools:
        print(f"- {tool.name}: {tool.description}")
    print("\n输入 'exit' 退出")
    
    while True:
        user_input = input("\n请输入问题: ")
        
        if user_input.lower() in ['exit', 'quit', '退出']:
            print("谢谢使用，再见！")
            break
            
        start_time = time.time()
        response = agent.run(user_input)
        end_time = time.time()
        
        print(f"\n{response}")
        print(f"响应时间: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    main() 