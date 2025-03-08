# 通用智能体框架 (Universal Agent Framework)

这是一个灵活、可扩展的通用智能体框架，旨在简化各种AI智能体的开发和部署。该框架支持多种大语言模型(LLM)后端，包括但不限于OpenAI、Claude等，并提供了丰富的工具集成能力和向量数据库支持。

## 主要特性

- **多模型支持**：支持OpenAI、Claude等多种LLM后端
- **工具集成**：简单的工具注册和调用机制，支持`@tool`装饰器
- **记忆管理**：内置短期和长期记忆管理，支持会话历史保存和恢复
- **向量数据库**：支持集成参考资料，进行语义搜索和智能引用
- **状态管理**：智能体状态的持久化和恢复
- **可观测性**：详细的日志和监控功能
- **可扩展性**：模块化设计，易于扩展新功能
- **缓存系统**：高效的请求缓存，减少API调用
- **异步支持**：支持异步操作，提高性能

## 快速开始

### 基本用法

```python
from agent_framework import Agent, tool

# 使用装饰器创建工具
@tool(name="calculator", description="计算数学表达式")
def calculator(expression: str) -> str:
    """计算数学表达式并返回结果"""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算错误: {str(e)}"

# 创建智能体
agent = Agent(
    name="math_assistant",
    description="数学助手",
    model="gpt-4o",  # 或其他支持的模型
    tools=[calculator.tool]
)

# 运行智能体
response = agent.run("计算 (3 + 4) * 5")
print(response)
```

### 配置模型

```python
# 从配置文件创建智能体
agent = Agent(
    name="我的助手",
    description="个性化助手",
    config_path="./my_config.ini"  # 自定义配置文件路径
)

# 或者直接指定模型
agent = Agent(
    name="我的助手",
    model="claude-3-opus-20240229"  # 使用Claude模型
)
```

## 安装

```bash
# 创建虚拟环境
conda create -n agent_framework python=3.10
conda activate agent_framework

# 安装依赖
pip install -r requirements.txt

# 设置OpenAI API密钥(或在config.ini中设置)
export OPENAI_API_KEY=your-api-key
```

## 配置

在`config.ini`文件中配置您的API密钥和其他设置:

```ini
[API]
# OpenAI配置
openai_api_key = your-api-key
openai_api_base = https://api.openai.com/v1
openai_model = gpt-4o

# Claude配置 
claude_api_key = your-claude-api-key
claude_model = claude-3-opus-20240229

# 通用API配置
default_model = openai

[embeddings]
provider = openai  # 可选：openai 或 local
api_key = your-openai-api-key
model = text-embedding-3-small  # OpenAI嵌入模型
```

## 内置示例智能体

### 1. 专业写作助手

全功能写作助手，支持各类文章创作需求。

```python
from agent_framework.examples.writing_assistant import main
main()
```

#### 主要功能

- **创作规划**: 大纲生成、结构建议
- **内容创作**: 章节扩展、标题生成、摘要生成
- **文本优化**: 文本润色、语法检查
- **参考资料**: 参考文献生成、资料搜索
- **文件管理**: 多格式文章保存

### 2. 增强版写作助手

基于专业写作助手，增加了向量数据库和参考资料处理功能。

```python
from agent_framework.examples.enhanced_writing_assistant import main
main()
```

#### 新增功能

- **参考资料处理**: 加载PDF/Word/文本文档
- **智能引用**: 自动提取和引用相关资料
- **语义搜索**: 基于语义而非关键词匹配
- **多库检索**: 在多个文档库中同时搜索

## 开发自己的智能体

### 1. 定义工具

```python
from agent_framework.models.tool import tool

@tool(name="weather", description="获取指定城市的天气信息")
def get_weather(city: str, days: int = 1) -> str:
    """获取指定城市未来几天的天气预报"""
    # 实际实现...
    return f"{city}未来{days}天天气: 晴朗，温度22-28°C"
```

### 2. 创建智能体

```python
from agent_framework import Agent

agent = Agent(
    name="天气助手",
    description="提供全球天气信息的助手",
    model="gpt-4o",
    tools=[get_weather.tool],
    system_prompt="你是一个专业的天气助手，回答用户关于天气的问题。"
)
```

### 3. 自定义系统提示

```python
system_prompt = """你是一个专业的{domain}助手。
你的职责是：
1. 回答用户关于{domain}的问题
2. 提供准确、清晰的信息
3. 使用友好的语气

请根据用户的需求，提供最相关的帮助。"""

agent = Agent(
    name="专业助手",
    model="gpt-4o",
    system_prompt=system_prompt.format(domain="编程")
)
```

### 4. 管理会话

```python
# 获取所有会话
conversations = agent.get_conversations()

# 加载特定会话
agent.load_conversation("conversation_id")

# 开始新会话
agent.new_conversation()

# 删除会话
agent.delete_conversation("conversation_id")
```

## 高级用法

### 向量数据库集成

```python
from agent_framework.examples.reference_tools import (
    load_document, semantic_search
)

agent = Agent(
    name="文档助手",
    model="gpt-4o",
    tools=[
        load_document.tool,  # 加载文档工具
        semantic_search.tool  # 语义搜索工具
    ]
)

# 加载文档
agent.run("加载文档 ./my_document.pdf 创建数据库 my_db")

# 搜索信息
agent.run("在my_db中搜索'人工智能的伦理问题'")
```

### 多模型混合使用

```python
# 配置不同端点
agent_gpt4 = Agent(name="GPT-4助手", model="gpt-4o")
agent_claude = Agent(name="Claude助手", model="claude-3-opus-20240229")

# 根据任务选择模型
def process_query(query):
    if "创意" in query or "写作" in query:
        return agent_claude.run(query)  # Claude更适合创意任务
    else:
        return agent_gpt4.run(query)  # GPT-4适合其他任务
```

## 项目结构 