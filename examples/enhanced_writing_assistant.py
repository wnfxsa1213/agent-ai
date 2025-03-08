"""
增强版写作助手 - 集成了向量数据库功能的专业写作智能体
"""

import os
import sys
import time
from datetime import datetime
import json
from pathlib import Path

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent_framework import Agent

# 导入写作助手工具
from agent_framework.examples.writing_assistant import (
    generate_outline,
    expand_section,
    polish_text,
    check_grammar,
    generate_titles,
    generate_summary,
    generate_references,
    generate_keywords,
    suggest_structure,
    save_article,
    search_reference,
    ARTICLE_TYPES
)

# 导入参考资料处理工具
from agent_framework.examples.reference_tools import (
    load_document,
    load_documents,
    list_reference_dbs,
    semantic_search,
    reference_with_search,
    delete_reference_db,
    save_with_references,
    LANGCHAIN_AVAILABLE
)

def main():
    """
    主函数
    """
    # 创建智能体
    agent = Agent(
        name="增强版写作助手",
        description="一个集成了向量数据库功能的专业写作助手，可以智能利用参考资料",
        model="gpt-4o",  # 使用更强大的模型
        tools=[
            # 原有写作工具
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
            search_reference.tool,
            
            # 参考资料处理工具
            load_document.tool,
            load_documents.tool,
            list_reference_dbs.tool,
            semantic_search.tool,
            reference_with_search.tool,
            delete_reference_db.tool,
            save_with_references.tool
        ],
        system_prompt="""你是一个增强版专业写作助手，不仅具备强大的写作能力，还能智能利用参考资料。

【写作能力】
1. 精准把握不同文体特点和风格，如学术论文、博客、新闻、营销文案等
2. 提供结构化的写作建议，确保文章逻辑清晰、重点突出
3. 根据目标受众调整表达方式，确保内容适合读者理解水平
4. 遵循各类写作规范和引用标准，如APA、MLA等格式

【参考资料利用能力】
1. 帮助用户管理和使用各类参考资料（PDF、Word、文本文件等）
2. 通过语义搜索找到最相关的资料片段
3. 将参考资料中的知识融入写作内容
4. 自动生成规范的引用和参考文献

【工作方式】
1. 理解用户需求：主动询问必要细节，如主题、文章类型、参考资料等
2. 分析文章需求：评估适合的结构、风格和内容深度
3. 智能利用参考资料：提取关键信息，恰当引用
4. 提供个性化写作指导：根据用户的写作风格和目标提供建议

【交互准则】
1. 保持友好、专业的沟通风格
2. 适当运用专业术语，同时确保用户理解
3. 在复杂问题上提供多个选项，帮助用户做出决策
4. 详细解释如何使用参考资料功能

你的目标是成为用户的专业写作伙伴，通过智能利用参考资料，帮助他们创作出高质量、有深度、有依据的内容。"""
    )
    
    # 程序启动显示
    print("\n" + "="*70)
    print(f"《{agent.name}》".center(68))
    print("="*70)
    print(f"{agent.description}")
    
    # 检查依赖
    if not LANGCHAIN_AVAILABLE:
        print("\n【警告】未安装向量数据库相关依赖，部分功能将不可用")
        print("请运行以下命令安装必要依赖：")
        print("pip install langchain langchain-openai chromadb pypdf docx2txt tiktoken")
    
    print("\n【支持的文章类型】")
    for key, value in ARTICLE_TYPES.items():
        print(f"- {key}: {value}")
    
    print("\n【主要功能】")
    print("1. 创作规划：生成大纲、文章结构建议")
    print("2. 内容创作：扩展章节、生成标题、摘要、关键词")
    print("3. 文本优化：润色文本、检查语法错误")
    print("4. 参考资料：生成参考文献、搜索相关资料")
    print("5. 文件管理：保存文章到文件")
    print("6. 参考资料处理：加载文档、构建向量数据库、语义搜索")
    
    print("\n【参考资料功能使用示例】")
    examples = [
        "加载文档 C:/我的资料/thesis.pdf",
        "加载目录 C:/我的资料/research_papers 创建数据库 我的论文资料",
        "列出所有参考资料数据库",
        "在'我的论文资料'数据库中搜索'人工智能伦理问题'",
        "根据参考资料生成一篇关于'AI伦理'的文章大纲"
    ]
    for i, example in enumerate(examples, 1):
        print(f"示例{i}: {example}")
    
    print("\n【命令】")
    print("- 输入 'help' 或 '帮助' 查看详细使用指南")
    print("- 输入 'reference-help' 查看参考资料功能使用指南")
    print("- 输入 'exit' 或 '退出' 结束程序")
    print("-"*70)
    
    # 主循环
    history = []  # 存储历史消息
    
    while True:
        try:
            user_input = input("\n请输入需求: ")
            
            # 处理特殊命令
            if user_input.lower() in ['exit', 'quit', '退出']:
                print("\n感谢使用增强版写作助手，祝您创作愉快！")
                break
                
            elif user_input.lower() in ['help', 'h', '帮助', '?']:
                print("\n【详细使用指南】")
                print("1. 生成大纲: '为[主题]生成[文章类型]大纲，包含[数量]个章节'")
                print("2. 扩展章节: '扩展[主题]的[章节标题]部分，风格为[风格]'")
                print("3. 润色文本: '以[风格]风格润色以下文本，目标读者是[受众]：[文本内容]'")
                print("4. 检查语法: '检查以下文本的语法错误：[文本内容]'")
                print("5. 生成标题: '为[主题]的[文章类型]生成[数量]个吸引人的标题'")
                print("6. 生成摘要: '为以下文章生成[长度]摘要：[文章内容]'")
                print("7. 文章结构: '为[文章类型]建议一个结构'")
                print("8. 保存文章: '将[标题]的文章保存为[格式]文件：[文章内容]'")
                continue
                
            elif user_input.lower() in ['reference-help', 'ref-help', '参考资料帮助']:
                print("\n【参考资料功能使用指南】")
                print("1. 加载单个文档: '加载文档 [文件路径]，创建数据库 [数据库名称]'")
                print("2. 加载目录文档: '加载目录 [目录路径]，创建数据库 [数据库名称]，文件类型 [pdf,docx,txt]'")
                print("3. 查看数据库列表: '列出所有参考资料数据库'")
                print("4. 语义搜索: '在[数据库名称]中搜索[查询内容]，返回[数量]个结果'")
                print("5. 跨库搜索: '在所有数据库中搜索[查询内容]'")
                print("6. 基于参考写作: '根据在[数据库名]中搜索到的关于[主题]的资料，生成一个[文章类型]大纲'")
                print("7. 保存带引用: '将标题为[标题]的文章与参考资料一起保存为[格式]文件'")
                continue
            
            # 记录请求时间
            start_time = time.time()
            
            # 处理请求
            print("\n正在处理您的请求...")
            response = agent.run(user_input)
            end_time = time.time()
            
            # 显示响应
            print("\n" + "-"*70)
            print(response)
            print("-"*70)
            print(f"响应时间: {end_time - start_time:.2f} 秒")
            
            # 添加到历史记录
            history.append((user_input, response))
            
        except KeyboardInterrupt:
            print("\n\n操作已取消。输入 'exit' 退出程序，或继续输入新的请求。")
        except Exception as e:
            print(f"\n处理请求时出错: {str(e)}")
            print("请重试或尝试不同的请求。")

if __name__ == "__main__":
    main() 