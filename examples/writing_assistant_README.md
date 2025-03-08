# 专业写作助手 (Professional Writing Assistant)

这是一个基于通用智能体框架开发的功能丰富的写作助手，能够帮助用户完成各种类型的文章写作任务。从创作规划到内容创作，从文本优化到参考资料管理，它提供了全方位的写作支持功能。

## 功能概览

### 1. 创作规划功能

#### 生成大纲 (`generate_outline`)
- **功能**：根据主题和文章类型生成结构化大纲
- **参数**：
  - `topic`: 文章主题
  - `article_type`: 文章类型，如"blog", "academic", "news"等
  - `sections`: 主要章节数量（1-10）
  - `depth`: 大纲层级深度（1-3）
  - `format`: 大纲格式，如"层级"、"数字"、"要点"、"罗马数字"
- **示例**：`为"人工智能在医疗领域的应用"生成一个学术论文大纲，包含5个章节，深度为3级，使用层级格式`

#### 文章结构建议 (`suggest_structure`)
- **功能**：为特定类型的文章提供结构建议和写作指导
- **参数**：
  - `article_type`: 文章类型，多种类型可选
  - `purpose`: 写作目的，如"一般", "教育", "说服", "娱乐", "分析"等
  - `length`: 文章长度，如"简短", "标准", "长篇"
  - `target_audience`: 目标受众，如"通用", "专业人士", "学生", "管理层"等
- **示例**：`为技术文档建议一个结构，写作目的是教育，长度是标准，目标受众是初学者`

### 2. 内容创作功能

#### 扩展章节 (`expand_section`)
- **功能**：扩展文章的某个章节，生成详细内容
- **参数**：
  - `topic`: 文章主题
  - `section_title`: 章节标题
  - `article_type`: 文章类型
  - `tone`: 语气风格，如"专业"、"幽默"、"严肃"等
  - `length`: 扩展长度，如"简短"、"中等"、"详细"
  - `include_elements`: 需包含的元素列表，如["例子", "数据", "观点"]等
- **示例**：`扩展"人工智能伦理"的"隐私问题"章节，使用专业语气，详细长度，包含例子和数据`

#### 生成标题 (`generate_titles`)
- **功能**：为文章生成吸引人的标题
- **参数**：
  - `topic`: 文章主题
  - `article_type`: 文章类型
  - `count`: 生成标题数量（1-10）
  - `title_style`: 标题风格，如"标准"、"疑问句"、"数字列表"、"吸引眼球"等
- **示例**：`为"远程工作的优缺点"生成5个疑问句风格的博客标题`

#### 生成摘要 (`generate_summary`)
- **功能**：为文章生成摘要
- **参数**：
  - `text`: 文章内容
  - `length`: 摘要长度，如"短"、"中等"、"长"
  - `focus`: 摘要侧重点，如"全面"、"观点"、"方法"、"结论"、"背景"
  - `style`: 摘要风格，如"简洁"、"详细"、"学术"、"通俗"
- **示例**：`为这篇文章生成一个中等长度的摘要，侧重于结论，使用简洁风格`

#### 生成关键词 (`generate_keywords`)
- **功能**：为文章生成关键词
- **参数**：
  - `text`: 文章内容
  - `count`: 关键词数量（1-15）
  - `keyword_type`: 关键词类型，如"主题词"、"SEO优化词"、"技术术语"、"混合"
  - `language`: 关键词语言，如"中文"、"英文"、"双语"
- **示例**：`为这篇文章生成8个SEO优化词，使用中文`

### 3. 文本优化功能

#### 文本润色 (`polish_text`)
- **功能**：润色和改进文本，提升质量
- **参数**：
  - `text`: 原始文本
  - `style`: 目标风格，如"专业"、"通俗"、"学术"、"幽默"、"正式"等
  - `target_audience`: 目标受众
  - `focus_areas`: 润色重点关注的方面，如["流畅度", "简洁性", "专业术语", "说服力"]等
- **示例**：`以学术风格润色这段文字，目标受众是研究人员，重点关注专业术语和表达准确性`

#### 语法检查 (`check_grammar`)
- **功能**：检查文本的语法和拼写错误
- **参数**：
  - `text`: 待检查的文本
  - `check_level`: 检查级别，可选值: "基础", "标准", "严格"
- **示例**：`用严格级别检查这段文字："这个想法很好，但是表达的不够清楚，需要进一步的解释和阐述。"`

### 4. 参考资料功能

#### 生成参考文献 (`generate_references`)
- **功能**：生成参考文献列表
- **参数**：
  - `topic`: 文章主题
  - `style`: 引用样式，如"APA", "MLA", "Chicago", "GB/T 7714", "IEEE"等
  - `count`: 期望生成的参考文献数量（1-20）
  - `source_types`: 参考文献类型，如["期刊论文", "专著", "网页", "会议论文"]等
  - `year_range`: 参考文献年份范围，如"近五年", "近十年", "2010-2020"
  - `language`: 参考文献语言，如"中文", "英文", "双语"
- **示例**：`为"人工智能安全"主题生成10条APA格式的参考文献，文献类型包括期刊论文和专著，年份范围为近五年，使用英文`

#### 搜索参考资料 (`search_reference`)
- **功能**：搜索相关参考资料
- **参数**：
  - `query`: 搜索查询
  - `source`: 资料来源，如"web", "academic", "news", "books"等
  - `language`: 搜索结果语言
  - `result_count`: 返回结果数量（1-20）
  - `filter_criteria`: 过滤条件字典
- **示例**：`搜索"气候变化对农业的影响"，资料来源为学术数据库，语言为中文，返回8条结果`

### 5. 文件管理功能

#### 保存文章 (`save_article`)
- **功能**：保存文章到文件
- **参数**：
  - `title`: 文章标题
  - `content`: 文章内容
  - `format`: 文件格式，如"txt", "md", "html", "json", "csv"
  - `folder`: 保存的文件夹路径
  - `add_timestamp`: 是否在文件名中添加时间戳
  - `encoding`: 文件编码，默认为utf-8
- **示例**：`将"人工智能发展史"的文章保存为markdown格式，添加时间戳`

## 使用示例

### 基本使用

```python
from agent_framework import Agent
from agent_framework.examples.writing_assistant import (
    generate_outline, expand_section, polish_text, check_grammar,
    generate_titles, generate_summary, generate_references,
    generate_keywords, suggest_structure, save_article, search_reference
)

# 创建写作助手智能体
agent = Agent(
    name="专业写作助手",
    description="一个可以帮助你完成各种类型文章写作的智能助手",
    model="gpt-4o",
    tools=[
        generate_outline.tool,
        expand_section.tool,
        polish_text.tool,
        check_grammar.tool,
        generate_titles.tool,
        generate_summary.tool,
        generate_references.tool,
        generate_keywords.tool,
        suggest_structure.tool,
        save_article.tool,
        search_reference.tool
    ]
)

# 运行写作助手
agent.run("请为我的学术论文'人工智能在教育中的应用'生成一个详细大纲")
```

### 完整写作流程示例

```python
# 1. 生成大纲
outline = agent.run("为'可持续发展与城市规划'生成一个学术论文大纲，深度为3级，使用数字格式")

# 2. 生成标题
titles = agent.run("为'可持续发展与城市规划'的学术论文生成5个吸引人的标题")

# 3. 扩展章节
intro = agent.run("扩展'可持续发展与城市规划'论文中的'可持续城市的定义与特征'章节，使用专业语气，详细长度，包含例子和数据")

# 4. 检查语法
checked_intro = agent.run("检查以下文本的语法: " + intro)

# 5. 润色文本
polished_intro = agent.run("以学术风格润色以下文本，目标受众是研究人员: " + checked_intro)

# 6. 生成参考文献
references = agent.run("为'可持续发展与城市规划'生成10条APA格式的参考文献，年份范围为近五年")

# 7. 保存文章
agent.run("将标题为'可持续发展与城市规划'的文章保存为markdown格式，内容是: " + polished_intro + "\n\n" + references)
```

## 命令行交互

运行 `python writing_assistant.py` 启动命令行交互界面，直接与写作助手对话。

```
《专业写作助手》
============================================================
一个可以帮助你完成各种类型文章写作的智能助手

【支持的文章类型】
- blog: 博客文章
- academic: 学术论文
- news: 新闻报道
- ...

【主要功能】
1. 创作规划：生成大纲、文章结构建议
2. 内容创作：扩展章节、生成标题、摘要、关键词
3. 文本优化：润色文本、检查语法错误
4. 参考资料：生成参考文献、搜索相关资料
5. 文件管理：保存文章到文件

请输入需求: 为"人工智能在医疗中的应用"生成一个博客大纲
```

## 自定义和扩展

您可以通过修改 `writing_assistant.py` 文件来自定义和扩展写作助手的功能：

1. 添加新的工具函数
2. 修改现有工具的参数和行为
3. 调整系统提示以改变助手的行为和风格

## 提示技巧

为获得最佳结果，请尽量详细描述您的需求：

1. 明确指定文章类型（博客、学术论文、新闻等）
2. 提供具体的主题或内容
3. 指定目标受众和风格要求
4. 明确需要的功能（大纲生成、章节扩展、润色等）

例如，不要只说"帮我写篇文章"，而应该说"请为一篇面向大学生的关于'人工智能伦理问题'的博客文章生成大纲，包含5个主要章节"。 