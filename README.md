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

## 示例智能体

### 专业写作助手

`examples/writing_assistant.py` 是一个功能齐全的写作智能体，可以帮助用户完成各种类型的文章写作任务。

#### 主要功能

1. **创作规划**
   - 生成大纲（支持多种格式和深度）
   - 文章结构建议（针对不同类型、目的、长度和受众）

2. **内容创作**
   - 扩展章节（可指定语气、长度和内容元素）
   - 生成标题（支持多种风格）
   - 生成摘要（可控制长度、侧重点和风格）
   - 生成关键词（支持不同类型和语言）

3. **文本优化**
   - 文本润色（支持多种风格、受众和关注点）
   - 语法检查（多级别检查）

4. **参考资料**
   - 生成参考文献（支持多种引用格式和筛选条件）
   - 搜索相关资料（多种来源和过滤选项）

5. **文件管理**
   - 保存文章（支持多种格式和选项）

更多详情请查看 `examples/writing_assistant_README.md`。

### 增强版写作助手

`examples/enhanced_writing_assistant.py` 是基于专业写作助手的升级版本，添加了向量数据库功能，能够智能利用用户提供的参考资料（如PDF、Word文档等）。

#### 新增功能

1. **参考资料处理**
   - 加载文档（支持PDF、Word、TXT等多种格式）
   - 构建向量数据库（自动分割和嵌入文本）
   - 管理参考资料库（创建、列出、删除数据库）

2. **智能检索与利用**
   - 语义搜索（基于含义而非关键词匹配）
   - 多库同时搜索（整合多个知识来源）
   - 带引用保存（自动生成规范的引用格式）

3. **实际应用场景**
   - 学术论文写作（自动引用相关研究）
   - 技术文档创作（基于官方文档撰写教程）
   - 研究报告（整合多个数据来源的分析）

更多详情请查看 `examples/ENHANCED_README.md`。

## 开发自己的智能体

1. 定义工具函数并使用 `@tool` 装饰器：

```python
from agent_framework import tool

@tool(name="my_tool", description="工具描述")
def my_tool(param1: str, param2: int = 0) -> str:
    """工具文档"""
    # 工具实现
    return "结果"
```

2. 创建智能体并添加工具：

```python
from agent_framework import Agent

agent = Agent(
    name="我的智能体",
    description="智能体描述",
    model="gpt-4",  # 或其他模型
    tools=[my_tool.tool]
)
```

3. 运行智能体：

```python
response = agent.run("用户输入")
print(response)
```

## 贡献

欢迎提交问题和拉取请求！ 