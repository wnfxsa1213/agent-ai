"""
简单智能体示例
"""

import os
import sys
import time
from datetime import datetime

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent_framework import Agent, Tool

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

def get_current_time() -> str:
    """
    获取当前时间
    
    Returns:
        str: 当前时间
    """
    return f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def main():
    """
    主函数
    """
    # 创建工具
    calc_tool = Tool(
        name="calculator",
        description="计算数学表达式，例如: 1 + 2 * 3",
        function=calculator
    )
    
    time_tool = Tool(
        name="get_current_time",
        description="获取当前时间",
        function=get_current_time
    )
    
    # 创建智能体
    agent = Agent(
        name="数学助手",
        description="一个可以帮助你解决数学问题的智能助手",
        tools=[calc_tool, time_tool]
    )
    
    print(f"欢迎使用 {agent.name}！")
    print(f"{agent.description}")
    print("输入 'exit' 退出")
    
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