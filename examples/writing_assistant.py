"""
专业写作助手 - 支持多种文章类型的写作
"""

import os
import sys
import time
from datetime import datetime
import re
import json
from pathlib import Path

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent_framework import Agent, tool

# 文章类型定义
ARTICLE_TYPES = {
    "blog": "博客文章",
    "academic": "学术论文",
    "news": "新闻报道",
    "marketing": "营销文案",
    "technical": "技术文档",
    "story": "故事/小说",
    "speech": "演讲稿",
    "report": "报告",
    "review": "评论/评测"
}

# 写作工具 - 大纲生成
@tool(name="generate_outline", description="根据主题和文章类型生成大纲")
def generate_outline(topic: str, article_type: str = "blog", sections: int = 5, depth: int = 2, format: str = "层级") -> str:
    """
    根据主题和文章类型生成大纲
    
    Args:
        topic (str): 文章主题
        article_type (str, optional): 文章类型，如"blog", "academic", "news"等
        sections (int, optional): 主要章节数量
        depth (int, optional): 大纲层级深度，1-3之间
        format (str, optional): 大纲格式，如"层级"、"数字"、"要点"等
        
    Returns:
        str: 文章大纲
    """
    if article_type not in ARTICLE_TYPES:
        return f"不支持的文章类型: {article_type}，可用的类型有: {', '.join(ARTICLE_TYPES.keys())}"
    
    # 验证参数
    if sections < 1:
        sections = 1
    elif sections > 10:
        sections = 10
        
    if depth < 1:
        depth = 1
    elif depth > 3:
        depth = 3
    
    # 验证格式
    valid_formats = ["层级", "数字", "要点", "罗马数字"]
    if format not in valid_formats:
        format = "层级"
    
    # 构建详细说明
    format_examples = {
        "层级": "使用缩进层级结构（如：I. → A. → 1.）",
        "数字": "使用数字编号（如：1. → 1.1 → 1.1.1）",
        "要点": "使用要点符号（如：• → ◦ → ▪）",
        "罗马数字": "使用罗马数字（如：I. → II. → III.）"
    }
    
    depth_description = ["仅主要章节", "包含二级标题", "包含三级标题"][depth-1]
    
    article_type_name = ARTICLE_TYPES[article_type]
    instruction = f"""
大纲需求：
- 主题：「{topic}」
- 文章类型：{article_type_name}
- 主要章节数：{sections}个
- 层级深度：{depth}级（{depth_description}）
- 大纲格式：{format}（{format_examples[format]}）
"""
    
    return f"大纲生成请求：\n{instruction}\n\n请智能体根据以上要求生成详细大纲"

# 写作工具 - 章节扩展
@tool(name="expand_section", description="扩展文章的某个章节")
def expand_section(topic: str, section_title: str, article_type: str = "blog", tone: str = "专业", 
                   length: str = "中等", include_elements: list = None) -> str:
    """
    扩展文章的某个章节
    
    Args:
        topic (str): 文章主题
        section_title (str): 章节标题
        article_type (str, optional): 文章类型
        tone (str, optional): 语气风格，如"专业"、"幽默"、"严肃"等
        length (str, optional): 扩展长度，可选值: "简短"、"中等"、"详细"
        include_elements (list, optional): 需要包含的元素，如["例子", "数据", "观点", "引用", "图表描述"]
        
    Returns:
        str: 扩展后的章节内容
    """
    if article_type not in ARTICLE_TYPES:
        return f"不支持的文章类型: {article_type}，可用的类型有: {', '.join(ARTICLE_TYPES.keys())}"
    
    # 标准化include_elements参数
    if include_elements is None:
        include_elements = []
    elif isinstance(include_elements, str):
        include_elements = [include_elements]
    
    # 验证语气参数
    valid_tones = ["专业", "幽默", "严肃", "热情", "温和", "批判", "故事化", "教学", "激励"]
    if tone not in valid_tones:
        tone = "专业"
    
    # 验证长度参数
    valid_lengths = {
        "简短": "300-500字",
        "中等": "800-1200字",
        "详细": "1500-2500字"
    }
    if length not in valid_lengths:
        length = "中等"
    
    # 验证元素列表
    valid_elements = ["例子", "数据", "观点", "引用", "图表描述", "故事", "案例研究", "实践步骤", "常见问题", "总结"]
    elements_to_include = []
    for element in include_elements:
        if element in valid_elements:
            elements_to_include.append(element)
    
    # 根据文章类型推荐元素
    recommended_elements = {
        "blog": ["例子", "观点", "总结"],
        "academic": ["数据", "引用", "图表描述"],
        "news": ["例子", "引用", "数据"],
        "marketing": ["例子", "故事", "案例研究"],
        "technical": ["实践步骤", "例子", "常见问题"],
        "story": ["故事", "描述", "对话"],
        "speech": ["例子", "故事", "激励点"],
        "report": ["数据", "图表描述", "观点"],
        "review": ["例子", "观点", "对比"]
    }
    
    if not elements_to_include and article_type in recommended_elements:
        elements_to_include = recommended_elements[article_type]
    
    # 构建详细的扩展请求
    article_type_name = ARTICLE_TYPES[article_type]
    elements_str = "、".join(elements_to_include) if elements_to_include else "无特殊要求"
    
    instruction = f"""
章节扩展需求：
- 文章主题：「{topic}」
- 章节标题：「{section_title}」
- 文章类型：{article_type_name}
- 语气风格：{tone}
- 扩展长度：{valid_lengths[length]}
- 需包含元素：{elements_str}
"""
    
    return f"章节扩展请求：\n{instruction}\n\n请智能体根据以上要求提供该章节的详细内容"

# 写作工具 - 文本润色
@tool(name="polish_text", description="润色和改进文本")
def polish_text(text: str, style: str = "专业", target_audience: str = "通用", focus_areas: list = None) -> str:
    """
    润色和改进文本
    
    Args:
        text (str): 原始文本
        style (str, optional): 目标风格，如"专业"、"通俗"、"学术"、"幽默"、"正式"等
        target_audience (str, optional): 目标受众，如"通用"、"专业人士"、"学生"、"管理层"等
        focus_areas (list, optional): 润色重点关注的方面，如["流畅度", "简洁性", "专业术语", "说服力"]等
        
    Returns:
        str: 润色后的文本
    """
    # 标准化focus_areas参数
    if focus_areas is None:
        focus_areas = ["整体品质"]
    elif isinstance(focus_areas, str):
        focus_areas = [focus_areas]
    
    # 构建润色指引
    polish_guide = []
    
    # 1. 基于风格的指引
    style_guides = {
        "专业": "使用专业术语，保持客观性，逻辑清晰",
        "通俗": "使用日常用语，避免专业术语，简单直接",
        "学术": "严谨的论证，充分的引用，学术术语，正式结构",
        "幽默": "增加俏皮元素，使用双关语，轻松的表达方式",
        "正式": "使用规范用语，避免口语化表达，严肃庄重",
        "温暖": "亲切友好的语气，共情表达，积极正面",
        "简洁": "精简词句，直入主题，减少修饰词",
        "生动": "增加比喻和形象描述，避免平淡表达"
    }
    
    if style in style_guides:
        polish_guide.append(f"风格指引：{style_guides[style]}")
    else:
        polish_guide.append(f"风格指引：按照「{style}」风格调整")
    
    # 2. 基于受众的指引
    audience_guides = {
        "通用": "适合广泛读者，避免过于专业或复杂的内容",
        "专业人士": "可使用行业术语，假设读者具有相关领域基础知识",
        "学生": "适当解释概念，提供学习指引，使用教学性语言",
        "管理层": "强调核心价值和战略意义，简明扼要，突出结论和建议",
        "儿童": "简化语言，使用生动形象的比喻，增加趣味性",
        "老年人": "清晰易懂，避免新兴网络用语，适当放慢信息传递节奏"
    }
    
    if target_audience in audience_guides:
        polish_guide.append(f"受众适配：{audience_guides[target_audience]}")
    else:
        polish_guide.append(f"受众适配：针对「{target_audience}」读者群体调整")
    
    # 3. 基于重点关注方面的指引
    focus_guides = {
        "整体品质": "全面提升文本质量",
        "流畅度": "改善句子连贯性，使段落过渡自然",
        "简洁性": "删减冗余表达，保持语言精炼",
        "专业术语": "适当增加或解释专业术语",
        "说服力": "加强论证和例证，提高说服力",
        "表达准确性": "确保用词准确，表达清晰",
        "结构优化": "调整段落结构，改善整体布局",
        "情感共鸣": "增强情感元素，引起读者共鸣"
    }
    
    focus_instructions = []
    for area in focus_areas:
        if area in focus_guides:
            focus_instructions.append(f"{area}：{focus_guides[area]}")
        else:
            focus_instructions.append(f"{area}：关注此方面")
    
    polish_guide.append(f"重点关注：{'，'.join(focus_instructions)}")
    
    # 构建完整的指引
    instruction = "\n".join(polish_guide)
    
    return f"润色请求:\n\n原文本长度：{len(text)}字\n润色指引：\n{instruction}\n\n请智能体提供润色后的内容，并简要说明所做的主要改进"

# 写作工具 - 语法检查
@tool(name="check_grammar", description="检查文本的语法和拼写错误")
def check_grammar(text: str, check_level: str = "标准") -> str:
    """
    检查文本的语法和拼写错误
    
    Args:
        text (str): 待检查的文本
        check_level (str, optional): 检查级别，可选值: "基础", "标准", "严格"
        
    Returns:
        str: 检查结果
    """
    # 这里应该集成真实的语法检查工具
    # 这只是一个示例实现
    errors = []
    warnings = []
    suggestions = []
    words = text.split()
    
    # 基础检查规则
    # 1. 重复词检查
    for i, word in enumerate(words):
        if i > 0 and i < len(words) - 1:
            if word.lower() == words[i-1].lower():
                errors.append(f"第{i+1}个词「{word}」与前一个词重复")
            elif word.lower() == "的" and (words[i-1].lower() == "的" or words[i+1].lower() == "的"):
                errors.append(f"第{i+1}个词「{word}」可能存在重复")
    
    # 2. 句子长度检查
    sentences = re.split(r'[。！？.!?]', text)
    for i, sentence in enumerate(sentences):
        if len(sentence) > 100:
            warnings.append(f"第{i+1}个句子过长（{len(sentence)}字），建议分割为多个短句")
    
    # 3. 标点符号检查
    if "，," in text or "。." in text:
        errors.append("存在中英文标点混用问题")
    
    # 4. 仅在严格模式下检查的规则
    if check_level == "严格":
        # 检查常见错误搭配
        incorrect_pairs = [("进行", "进行"), ("非常", "特别"), ("问题", "问题")]
        for i in range(len(words) - 1):
            pair = (words[i], words[i+1])
            if pair in incorrect_pairs:
                suggestions.append(f"可能存在不当搭配：「{pair[0]} {pair[1]}」")
    
    # 构建结构化结果
    result = []
    if errors:
        result.append("【错误】:")
        for i, error in enumerate(errors, 1):
            result.append(f"{i}. {error}")
        result.append("")
    
    if warnings:
        result.append("【警告】:")
        for i, warning in enumerate(warnings, 1):
            result.append(f"{i}. {warning}")
        result.append("")
    
    if suggestions and check_level != "基础":
        result.append("【建议】:")
        for i, suggestion in enumerate(suggestions, 1):
            result.append(f"{i}. {suggestion}")
        result.append("")
    
    if not result:
        return f"检查完成（{check_level}级别）：未发现明显的语法或拼写错误"
    else:
        result.insert(0, f"检查完成（{check_level}级别）:")
        return "\n".join(result)

# 写作工具 - 生成标题
@tool(name="generate_titles", description="为文章生成吸引人的标题")
def generate_titles(topic: str, article_type: str = "blog", count: int = 5, title_style: str = "标准") -> str:
    """
    为文章生成吸引人的标题
    
    Args:
        topic (str): 文章主题
        article_type (str, optional): 文章类型
        count (int, optional): 生成标题数量
        title_style (str, optional): 标题风格，如"标准"、"疑问句"、"数字列表"、"吸引眼球"等
        
    Returns:
        str: 生成的标题列表
    """
    if article_type not in ARTICLE_TYPES:
        return f"不支持的文章类型: {article_type}，可用的类型有: {', '.join(ARTICLE_TYPES.keys())}"
    
    # 限制生成标题的数量在合理范围内
    if count < 1:
        count = 1
    elif count > 10:
        count = 10
        
    article_type_name = ARTICLE_TYPES[article_type]
    return f"已请求为「{topic}」{article_type_name}生成{count}个「{title_style}」风格的吸引人标题，请智能体提供标题列表"

# 写作工具 - 生成摘要
@tool(name="generate_summary", description="为文章生成摘要")
def generate_summary(text: str, length: str = "中等", focus: str = "全面", style: str = "简洁") -> str:
    """
    为文章生成摘要
    
    Args:
        text (str): 文章内容
        length (str, optional): 摘要长度，可选值: "短"(100字以内), "中等"(200字左右), "长"(400字左右)
        focus (str, optional): 摘要侧重点，可选值: "全面", "观点", "方法", "结论", "背景"
        style (str, optional): 摘要风格，可选值: "简洁", "详细", "学术", "通俗"
        
    Returns:
        str: 生成的摘要
    """
    # 验证长度参数
    valid_lengths = {"短": "100字以内", "中等": "200字左右", "长": "400字左右"}
    if length not in valid_lengths:
        length = "中等"
    
    # 验证重点参数
    valid_focus = ["全面", "观点", "方法", "结论", "背景"]
    if focus not in valid_focus:
        focus = "全面"
    
    # 验证风格参数
    valid_styles = ["简洁", "详细", "学术", "通俗"]
    if style not in valid_styles:
        style = "简洁"
    
    # 计算原文长度
    text_length = len(text)
    
    # 计算预期摘要长度
    if length == "短":
        target_length = min(100, text_length // 10)
    elif length == "中等":
        target_length = min(200, text_length // 5)
    else:  # 长
        target_length = min(400, text_length // 3)
    
    # 构建详细的摘要生成请求
    focus_instructions = {
        "全面": "涵盖文章的主要内容、观点和结论",
        "观点": "侧重于文章的主要观点和论点",
        "方法": "侧重于文章所使用的方法和技术",
        "结论": "侧重于文章的结论和建议",
        "背景": "侧重于文章的背景和问题描述"
    }
    
    style_instructions = {
        "简洁": "使用简明扼要的语言，直接呈现核心内容",
        "详细": "提供更多细节和背景说明",
        "学术": "使用学术性语言和结构",
        "通俗": "使用通俗易懂的语言，适合一般读者"
    }
    
    summary_instruction = f"""
摘要要求：
- 长度：{valid_lengths[length]}（目标约{target_length}字）
- 重点：{focus_instructions[focus]}
- 风格：{style_instructions[style]}
- 原文长度：{text_length}字
"""
    
    return f"摘要生成请求：\n{summary_instruction}\n\n请智能体根据以上要求生成文章摘要"

# 写作工具 - 生成参考文献
@tool(name="generate_references", description="生成参考文献列表")
def generate_references(topic: str, style: str = "APA", count: int = 5, source_types: list = None, 
                        year_range: str = "近十年", language: str = "中文") -> str:
    """
    生成参考文献列表
    
    Args:
        topic (str): 文章主题
        style (str, optional): 引用样式，如"APA", "MLA", "Chicago", "GB/T 7714", "IEEE"等
        count (int, optional): 期望生成的参考文献数量
        source_types (list, optional): 参考文献类型，如["期刊论文", "专著", "网页", "会议论文", "学位论文"]
        year_range (str, optional): 参考文献年份范围，如"近五年", "近十年", "2010-2020", "不限"
        language (str, optional): 参考文献语言，如"中文", "英文", "双语"
        
    Returns:
        str: 参考文献列表
    """
    # 验证引用样式
    valid_styles = {
        "APA": "美国心理学会格式 (American Psychological Association)",
        "MLA": "现代语言协会格式 (Modern Language Association)",
        "Chicago": "芝加哥格式 (Chicago Manual of Style)",
        "GB/T 7714": "中国国家标准格式",
        "IEEE": "电气电子工程师学会格式",
        "Harvard": "哈佛引用格式",
        "AMA": "美国医学协会格式",
        "Vancouver": "温哥华格式（医学领域常用）"
    }
    
    if style not in valid_styles:
        style = "APA"
    
    # 验证参考文献数量
    if count < 1:
        count = 1
    elif count > 20:
        count = 20
    
    # 标准化source_types参数
    if source_types is None:
        source_types = ["期刊论文", "专著", "网页"]
    elif isinstance(source_types, str):
        source_types = [source_types]
    
    # 验证文献类型
    valid_source_types = ["期刊论文", "专著", "网页", "会议论文", "学位论文", "报纸文章", "研究报告", "政府文件", "数据集"]
    filtered_source_types = []
    for source_type in source_types:
        if source_type in valid_source_types:
            filtered_source_types.append(source_type)
    
    if not filtered_source_types:
        filtered_source_types = ["期刊论文", "专著", "网页"]
    
    # 验证年份范围
    valid_year_ranges = ["近三年", "近五年", "近十年", "近二十年", "不限"]
    if year_range not in valid_year_ranges and not re.match(r'^\d{4}-\d{4}$', year_range):
        year_range = "近十年"
    
    # 验证语言
    valid_languages = ["中文", "英文", "双语"]
    if language not in valid_languages:
        language = "中文"
    
    # 构建详细的参考文献请求
    source_types_str = "、".join(filtered_source_types)
    
    instruction = f"""
参考文献需求：
- 主题：「{topic}」
- 引用格式：{style}（{valid_styles[style]}）
- 数量：{count}条
- 文献类型：{source_types_str}
- 年份范围：{year_range}
- 语言：{language}
"""
    
    return f"参考文献生成请求：\n{instruction}\n\n请智能体根据以上要求生成符合格式的参考文献列表"

# 写作工具 - 生成关键词
@tool(name="generate_keywords", description="为文章生成关键词")
def generate_keywords(text: str, count: int = 5, keyword_type: str = "主题词", language: str = "中文") -> str:
    """
    为文章生成关键词
    
    Args:
        text (str): 文章内容
        count (int, optional): 关键词数量
        keyword_type (str, optional): 关键词类型，如"主题词", "SEO优化词", "技术术语", "混合"
        language (str, optional): 关键词语言，如"中文", "英文", "双语"
        
    Returns:
        str: 关键词列表
    """
    # 验证关键词数量
    if count < 1:
        count = 1
    elif count > 15:
        count = 15
    
    # 验证关键词类型
    valid_types = ["主题词", "SEO优化词", "技术术语", "混合"]
    if keyword_type not in valid_types:
        keyword_type = "主题词"
    
    # 关键词类型说明
    type_descriptions = {
        "主题词": "提取文章的核心主题和概念",
        "SEO优化词": "针对搜索引擎优化的热门搜索词",
        "技术术语": "提取文章中的专业技术术语",
        "混合": "综合考虑主题词、SEO词和技术术语"
    }
    
    # 验证语言
    valid_languages = ["中文", "英文", "双语"]
    if language not in valid_languages:
        language = "中文"
    
    # 智能推荐：根据文本长度调整关键词数量
    text_length = len(text)
    recommended_count = max(3, min(10, text_length // 500))
    
    instruction = f"""
关键词提取需求：
- 文本长度：{text_length}字
- 关键词数量：{count}个（推荐数量：{recommended_count}个）
- 关键词类型：{keyword_type}（{type_descriptions[keyword_type]}）
- 关键词语言：{language}
"""
    
    return f"关键词提取请求：\n{instruction}\n\n请智能体根据以上要求从文本中提取关键词并按重要性排序"

# 写作工具 - 文章结构建议
@tool(name="suggest_structure", description="为特定类型的文章提供结构建议")
def suggest_structure(article_type: str, purpose: str = "一般", length: str = "标准", target_audience: str = "通用") -> str:
    """
    为特定类型的文章提供结构建议
    
    Args:
        article_type (str): 文章类型
        purpose (str, optional): 写作目的，如"一般", "教育", "说服", "娱乐", "分析"
        length (str, optional): 文章长度，如"简短", "标准", "长篇"
        target_audience (str, optional): 目标受众，如"通用", "专业人士", "学生", "管理层"
        
    Returns:
        str: 结构建议
    """
    # 基础结构模板
    basic_structures = {
        "blog": "博客文章通常包含:\n1. 引人注目的标题\n2. 开场白/引言\n3. 主要内容（分为3-5个小节）\n4. 总结/结论\n5. 号召性用语(CTA)",
        "academic": "学术论文通常包含:\n1. 标题\n2. 摘要\n3. 关键词\n4. 引言\n5. 文献综述\n6. 研究方法\n7. 结果\n8. 讨论\n9. 结论\n10. 参考文献",
        "news": "新闻报道通常包含:\n1. 标题\n2. 导语（回答5W1H：何人、何事、何时、何地、为何、如何）\n3. 主体内容（按重要性递减）\n4. 背景信息\n5. 引述\n6. 结语",
        "marketing": "营销文案通常包含:\n1. 吸引眼球的标题\n2. 问题提出\n3. 解决方案\n4. 产品/服务介绍\n5. 社会证明/案例\n6. 优惠信息\n7. 强烈的号召性用语",
        "technical": "技术文档通常包含:\n1. 标题\n2. 概述\n3. 先决条件\n4. 步骤说明（按顺序）\n5. 代码示例\n6. 常见问题\n7. 故障排除\n8. 参考资料",
        "story": "故事/小说通常包含:\n1. 开场/背景设定\n2. 人物介绍\n3. 冲突/问题出现\n4. 情节发展\n5. 高潮\n6. 解决\n7. 结局",
        "speech": "演讲稿通常包含:\n1. 开场白（吸引注意）\n2. 自我介绍\n3. 主题陈述\n4. 主要论点（2-4个）\n5. 故事/案例\n6. 总结\n7. 号召行动",
        "report": "报告通常包含:\n1. 标题\n2. 执行摘要\n3. 引言\n4. 方法\n5. 发现/结果\n6. 分析\n7. 结论\n8. 建议\n9. 附录",
        "review": "评论/评测通常包含:\n1. 标题\n2. 简介\n3. 背景信息\n4. 优点分析\n5. 缺点分析\n6. 比较\n7. 总体评价\n8. 推荐意见",
        "guide": "指南通常包含:\n1. 标题\n2. 引言（目的说明）\n3. 必要背景/基础知识\n4. 分步骤说明\n5. 提示与技巧\n6. 常见问题解答\n7. 总结",
        "case_study": "案例研究通常包含:\n1. 标题\n2. 执行摘要\n3. 背景介绍\n4. 挑战/问题描述\n5. 解决方案\n6. 实施过程\n7. 结果/成效\n8. 结论与经验",
        "essay": "论述文通常包含:\n1. 标题\n2. 引言（包含论点）\n3. 论证部分（多个段落，每段一个分论点）\n4. 反驳可能的反对意见\n5. 结论\n6. 参考文献",
        "proposal": "提案通常包含:\n1. 标题\n2. 执行摘要\n3. 问题/需求陈述\n4. 目标\n5. 解决方案/方法\n6. 资源需求（时间，人力，预算）\n7. 预期成果\n8. 风险评估\n9. 实施计划\n10. 结论"
    }
    
    # 验证文章类型
    if article_type not in basic_structures:
        available_types = ", ".join(sorted(basic_structures.keys()))
        return f"不支持的文章类型: {article_type}，可用的类型有: {available_types}"
    
    # 验证写作目的
    valid_purposes = ["一般", "教育", "说服", "娱乐", "分析", "指导", "启发", "总结"]
    if purpose not in valid_purposes:
        purpose = "一般"
    
    # 验证长度
    valid_lengths = {
        "简短": "1000字以内",
        "标准": "1000-3000字",
        "长篇": "3000字以上",
    }
    if length not in valid_lengths:
        length = "标准"
    
    # 验证目标受众
    valid_audiences = ["通用", "专业人士", "学生", "管理层", "初学者", "研究人员", "决策者"]
    if target_audience not in valid_audiences:
        target_audience = "通用"
    
    # 获取基础结构
    base_structure = basic_structures[article_type]
    
    # 针对写作目的的额外建议
    purpose_suggestions = {
        "教育": "- 添加更多的解释性内容和示例\n- 考虑包含练习或复习问题\n- 使用图表和图示来阐明复杂概念",
        "说服": "- 加强情感共鸣点\n- 增加更多证据和数据支持\n- 预先反驳可能的反对意见\n- 强化结尾的号召性用语",
        "娱乐": "- 使用更生动的语言和形象化描述\n- 增加趣味性元素和意外转折\n- 考虑加入幽默元素",
        "分析": "- 扩展方法论和数据来源说明\n- 深入探讨多种可能的解释\n- 增加对比分析和趋势讨论",
        "指导": "- 详细展开每个步骤\n- 添加常见错误和避免方法\n- 包含实际案例展示",
        "启发": "- 强化个人故事和经验分享\n- 添加思考性问题\n- 提供多角度思考框架",
        "总结": "- 突出关键信息和核心观点\n- 使用图表总结数据\n- 确保覆盖所有重要方面"
    }
    
    # 针对长度的调整建议
    length_suggestions = {
        "简短": "- 精简次要内容\n- 聚焦1-2个核心观点\n- 减少示例数量，保留最有力的例子",
        "标准": "- 保持结构均衡\n- 每个部分给予适当篇幅\n- 适量使用示例和说明",
        "长篇": "- 考虑增加子章节\n- 扩展示例和案例分析\n- 添加更多背景信息和深入探讨\n- 考虑使用附录存放辅助材料"
    }
    
    # 针对受众的调整建议
    audience_suggestions = {
        "通用": "- 避免行业术语或提供解释\n- 使用日常生活示例\n- 保持语言简洁直接",
        "专业人士": "- 可使用行业术语\n- 减少基础概念解释\n- 增加技术细节和深度分析",
        "学生": "- 增加教学性内容\n- 清晰解释概念\n- 提供学习提示和复习点",
        "管理层": "- 强调战略意义和商业价值\n- 提供执行摘要\n- 突出结论和建议",
        "初学者": "- 详细解释基础概念\n- 使用大量示例\n- 避免过于复杂的内容",
        "研究人员": "- 详细说明研究方法和数据\n- 深入讨论理论基础\n- 增加与现有研究的比较",
        "决策者": "- 强调结论和建议\n- 简洁展示关键数据\n- 添加风险评估和预期效果"
    }
    
    # 组合所有建议
    structure_suggestion = f"""
【{article_type}的基础结构】
{base_structure}

【根据您的需求的个性化建议】
1. 针对「{purpose}」目的的建议：
{purpose_suggestions.get(purpose, "保持标准结构即可")}

2. 针对「{length}」长度（{valid_lengths[length]}）的调整：
{length_suggestions.get(length, "")}

3. 针对「{target_audience}」受众的调整：
{audience_suggestions.get(target_audience, "")}
"""
    
    return structure_suggestion

# 写作工具 - 保存文章
@tool(name="save_article", description="保存文章到文件")
def save_article(title: str, content: str, format: str = "txt", folder: str = "", add_timestamp: bool = False, 
                encoding: str = "utf-8") -> str:
    """
    保存文章到文件
    
    Args:
        title (str): 文章标题
        content (str): 文章内容
        format (str, optional): 文件格式，如"txt", "md", "html", "docx", "pdf"等
        folder (str, optional): 保存的文件夹路径，为空则保存在当前目录
        add_timestamp (bool, optional): 是否在文件名中添加时间戳
        encoding (str, optional): 文件编码，默认为utf-8
        
    Returns:
        str: 操作结果
    """
    try:
        # 验证格式
        valid_formats = ["txt", "md", "html", "json", "csv"]
        if format not in valid_formats:
            format = "txt"
        
        # 处理文件名
        filename = title.replace(" ", "_").replace("/", "_").replace("\\", "_")
        # 移除不安全的字符
        filename = re.sub(r'[<>:"|?*]', '', filename)
        
        # 添加时间戳
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}"
        
        # 确保有正确的扩展名
        if not filename.endswith(f".{format}"):
            filename += f".{format}"
        
        # 处理保存路径
        if folder:
            # 创建文件夹（如果不存在）
            folder_path = Path(folder)
            folder_path.mkdir(parents=True, exist_ok=True)
            file_path = folder_path / filename
        else:
            file_path = Path(filename)
        
        # 根据不同的格式处理内容
        if format == "html":
            content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="{encoding}">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 2em; }}
        h1 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {content.replace('\n', '<br>')}
</body>
</html>"""
        elif format == "md":
            # 确保标题是Markdown格式
            if not content.startswith("# "):
                content = f"# {title}\n\n{content}"
        elif format == "json":
            content = json.dumps({
                "title": title,
                "content": content,
                "created_at": datetime.now().isoformat(),
            }, ensure_ascii=False, indent=2)
        
        # 保存文件
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
        
        return f"已将文章保存到: {file_path.absolute()}"
    except Exception as e:
        return f"保存文章失败: {str(e)}"

# 写作工具 - 搜索参考资料
@tool(name="search_reference", description="搜索相关参考资料")
def search_reference(query: str, source: str = "web", language: str = "中文", 
                    result_count: int = 5, filter_criteria: dict = None) -> str:
    """
    搜索相关参考资料
    
    Args:
        query (str): 搜索查询
        source (str, optional): 资料来源，如"web", "academic", "news", "books"等
        language (str, optional): 搜索结果语言，如"中文", "英文", "双语"
        result_count (int, optional): 返回结果数量
        filter_criteria (dict, optional): 过滤条件，如{"year": "近五年", "type": "论文", "field": "计算机科学"}
        
    Returns:
        str: 搜索结果
    """
    # 验证资料来源
    valid_sources = {
        "web": "网络搜索",
        "academic": "学术数据库",
        "news": "新闻媒体",
        "books": "图书资料",
        "journals": "期刊论文",
        "conferences": "会议论文",
        "reports": "研究报告",
        "theses": "学位论文",
        "patents": "专利文献"
    }
    
    if source not in valid_sources:
        source = "web"
    
    # 验证结果数量
    if result_count < 1:
        result_count = 1
    elif result_count > 20:
        result_count = 20
    
    # 验证语言
    valid_languages = ["中文", "英文", "双语", "全部"]
    if language not in valid_languages:
        language = "中文"
    
    # 处理过滤条件
    if filter_criteria is None:
        filter_criteria = {}
    
    # 构建搜索指引
    search_instruction = f"""
搜索需求：
- 查询词：「{query}」
- 资料来源：{valid_sources[source]}
- 语言要求：{language}
- 结果数量：{result_count}条
"""
    
    # 添加过滤条件（如果有）
    if filter_criteria:
        filter_str = []
        for key, value in filter_criteria.items():
            filter_str.append(f"- {key}: {value}")
        
        if filter_str:
            search_instruction += "\n过滤条件：\n" + "\n".join(filter_str)
    
    # 添加智能推荐
    recommended_sources = {
        "学术": "academic",
        "教育": "academic",
        "研究": "academic",
        "新闻": "news",
        "时事": "news",
        "事件": "news",
        "书籍": "books",
        "小说": "books",
        "文学": "books",
        "专利": "patents",
        "发明": "patents",
        "技术": "journals"
    }
    
    # 智能推荐资料来源
    for keyword, rec_source in recommended_sources.items():
        if keyword in query and source == "web":
            search_instruction += f"\n\n注意：检测到查询包含「{keyword}」关键词，建议考虑使用「{valid_sources[rec_source]}」作为资料来源"
            break
    
    return f"参考资料搜索请求：\n{search_instruction}\n\n请智能体根据以上需求提供搜索结果"

def main():
    """
    主函数
    """
    # 创建智能体
    agent = Agent(
        name="专业写作助手",
        description="一个可以帮助你完成各种类型文章写作的智能助手",
        model="gpt-4o",  # 使用更强大的模型
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
        ],
        system_prompt="""你是一个专业的写作助手，擅长帮助用户完成各种类型的文章写作。

【写作能力】
1. 精准把握不同文体特点和风格，如学术论文、博客、新闻、营销文案等
2. 提供结构化的写作建议，确保文章逻辑清晰、重点突出
3. 根据目标受众调整表达方式，确保内容适合读者理解水平
4. 遵循各类写作规范和引用标准，如APA、MLA等格式

【工作方式】
1. 理解用户需求：主动询问必要细节，如主题、文章类型、目标受众、长度要求等
2. 分析文章需求：评估适合的结构、风格和内容深度
3. 提供具体建议：不仅告诉"做什么"，还提供"如何做"的详细指导
4. 根据反馈调整：根据用户反馈快速调整写作建议和内容生成

【交互准则】
1. 保持友好、专业的沟通风格
2. 适当运用专业术语，同时确保用户理解
3. 在复杂问题上提供多个选项，帮助用户做出决策
4. 关注写作过程中的细节和连贯性

你了解各种写作工具的使用场景和最佳实践，并能引导用户有效地使用它们来提升写作质量。
你的目标是不仅提供技术支持，还要成为用户的写作教练和顾问，帮助他们在写作过程中取得进步。
"""
    )
    
    # 程序启动显示
    print("\n" + "="*60)
    print(f"《{agent.name}》".center(58))
    print("="*60)
    print(f"{agent.description}")
    print("\n【支持的文章类型】")
    for key, value in ARTICLE_TYPES.items():
        print(f"- {key}: {value}")
    
    print("\n【主要功能】")
    print("1. 创作规划：生成大纲、文章结构建议")
    print("2. 内容创作：扩展章节、生成标题、摘要、关键词")
    print("3. 文本优化：润色文本、检查语法错误")
    print("4. 参考资料：生成参考文献、搜索相关资料")
    print("5. 文件管理：保存文章到文件")
    
    print("\n【使用示例】")
    examples = [
        "请为「人工智能在教育领域的应用」生成一个技术文档大纲",
        "帮我为「远程工作的挑战与对策」博客文章生成5个吸引人的标题",
        "请检查以下文本的语法错误：「我觉得这个的的观点很有意思，但是但是需要更多论证。」",
        "以学术风格润色这段文字，目标读者是大学教授：「AI很厉害，能做很多事情，比如写作和编程。」",
        "为我的演讲稿建议一个合适的结构"
    ]
    for i, example in enumerate(examples, 1):
        print(f"示例{i}: {example}")
    
    print("\n【命令】")
    print("- 输入 'help' 或 '帮助' 查看详细使用指南")
    print("- 输入 'exit' 或 '退出' 结束程序")
    print("-"*60)
    
    # 主循环
    history = []  # 存储历史消息
    
    while True:
        try:
            user_input = input("\n请输入需求: ")
            
            # 处理特殊命令
            if user_input.lower() in ['exit', 'quit', '退出']:
                print("\n感谢使用专业写作助手，祝您创作愉快！")
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
            
            # 记录请求时间
            start_time = time.time()
            
            # 处理请求
            print("\n正在处理您的请求...")
            response = agent.run(user_input)
            end_time = time.time()
            
            # 显示响应
            print("\n" + "-"*60)
            print(response)
            print("-"*60)
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