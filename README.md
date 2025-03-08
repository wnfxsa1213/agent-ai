# 通用智能体框架 (Universal Agent Framework)

这是一个灵活、可扩展的通用智能体框架，旨在简化各种AI智能体的开发和部署。该框架支持多种大语言模型(LLM)后端，包括但不限于OpenAI、Claude、本地模型等，并提供了丰富的工具集成能力。

## 主要特性

- **多模型支持**：支持OpenAI、Claude、本地模型等多种LLM后端
- **工具集成**：简单的工具注册和调用机制
- **记忆管理**：内置短期和长期记忆管理
- **状态追踪**：智能体状态的持久化和恢复
- **可观测性**：详细的日志和监控功能
- **可扩展性**：模块化设计，易于扩展新功能
- **缓存系统**：高效的请求缓存，减少API调用
- **异步支持**：支持异步操作，提高性能

## 快速开始

```python
from agent_framework import Agent, Tool

# 创建一个简单的工具
def calculator(expression):
    return eval(expression)

# 注册工具
tool = Tool(
    name="calculator",
    description="计算数学表达式",
    function=calculator
)

# 创建智能体
agent = Agent(
    name="math_assistant",
    description="数学助手",
    model="gpt-4",
    tools=[tool]
)

# 运行智能体
response = agent.run("计算 (3 + 4) * 5")
print(response)
```

## 安装

```bash
pip install -r requirements.txt
```

## 配置

在`config.ini`文件中配置您的API密钥和其他设置。

## 贡献

欢迎提交问题和拉取请求！ 