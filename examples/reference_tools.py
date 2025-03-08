"""
参考资料处理工具 - 提供向量数据库支持的文档处理和语义搜索功能
"""

import os
import re
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

# 添加父目录到路径
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent_framework import tool
from agent_framework.config import ConfigManager

# 第三方依赖，请确保已安装：
# pip install langchain langchain-openai chromadb pypdf docx2txt tiktoken

try:
    from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, CSVLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_community.document_transformers import Html2TextTransformer
    from langchain_core.documents import Document
    from langchain_community.embeddings import HuggingFaceEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("警告: LangChain相关库未安装。请运行: pip install langchain langchain-openai chromadb pypdf docx2txt tiktoken")


# 全局配置
DEFAULT_DB_PATH = "./reference_dbs"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def get_embeddings(embedding_type="openai", config=None):
    """
    根据配置创建嵌入对象
    
    Args:
        embedding_type (str): 嵌入类型，"openai"或"local"
        config (ConfigManager, optional): 配置管理器对象
        
    Returns:
        Embeddings: 嵌入对象
    """
    if config is None:
        config = ConfigManager()
    
    if embedding_type == "openai":
        api_key = config.get("embeddings", "api_key", fallback="")
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY", "")
        
        model = config.get("embeddings", "model", fallback="text-embedding-3-small")
        
        return OpenAIEmbeddings(
            openai_api_key=api_key,
            model=model
        )
    elif embedding_type == "local":
        model_name = config.get("embeddings", "local_model", 
                               fallback="shibing624/text2vec-base-chinese")
        
        return HuggingFaceEmbeddings(
            model_name=model_name
        )
    else:
        raise ValueError(f"不支持的嵌入类型: {embedding_type}")


@tool(name="load_document", description="加载单个文档并构建向量数据库")
def load_document(file_path: str, db_name: str = None, chunk_size: int = CHUNK_SIZE, 
                 chunk_overlap: int = CHUNK_OVERLAP) -> str:
    """
    加载单个文档(PDF/DOCX/TXT等)并构建向量数据库
    
    Args:
        file_path (str): 文档的文件路径
        db_name (str, optional): 向量数据库名称，默认使用文件名
        chunk_size (int, optional): 文本块大小
        chunk_overlap (int, optional): 文本块重叠大小
        
    Returns:
        str: 处理结果描述
    """
    if not LANGCHAIN_AVAILABLE:
        return "错误: 未安装必要的依赖库。请运行: pip install langchain langchain-openai chromadb pypdf docx2txt tiktoken"
    
    if not os.path.exists(file_path):
        return f"错误: 文件'{file_path}'不存在"
    
    # 如果未指定数据库名称，使用文件名(不含扩展名)
    if db_name is None:
        db_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # 规范化数据库名称，移除不安全字符
    db_name = re.sub(r'[^a-zA-Z0-9_-]', '_', db_name)
    
    # 确定文件类型并加载
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            loader = PyPDFLoader(file_path)
        elif file_ext in ['.docx', '.doc']:
            loader = Docx2txtLoader(file_path)
        elif file_ext == '.txt':
            loader = TextLoader(file_path, encoding='utf-8')
        elif file_ext in ['.csv', '.tsv']:
            loader = CSVLoader(file_path)
        else:
            return f"不支持的文件类型: {file_ext}"
        
        documents = loader.load()
        
        if not documents:
            return f"警告: 从文件'{file_path}'中未提取到内容"
            
        # 分割文档为较小的块
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = text_splitter.split_documents(documents)
        
        # 创建向量存储目录
        db_path = os.path.join(DEFAULT_DB_PATH, db_name)
        os.makedirs(db_path, exist_ok=True)
        
        # 使用统一的嵌入获取函数
        config = ConfigManager()
        embedding_type = config.get("embeddings", "provider", fallback="openai")
        embeddings = get_embeddings(embedding_type, config)
        
        # 创建并保存向量数据库
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=db_path
        )
        vector_db.persist()
        
        # 保存数据库元信息
        metadata = {
            "file_name": os.path.basename(file_path),
            "file_path": os.path.abspath(file_path),
            "file_type": file_ext.lstrip('.'),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "chunk_count": len(chunks),
            "created_at": datetime.now().isoformat(),
        }
        
        with open(os.path.join(db_path, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return f"成功处理文档 '{os.path.basename(file_path)}'。\n" \
               f"共生成{len(chunks)}个文本块，向量数据库已保存为'{db_name}'。"
    
    except Exception as e:
        return f"处理文件时出错: {str(e)}"


@tool(name="load_documents", description="加载目录中的所有文档并构建向量数据库")
def load_documents(directory_path: str, db_name: str = "reference_collection", 
                  file_types: List[str] = None, recursive: bool = False,
                  chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> str:
    """
    加载目录中的所有文档并构建向量数据库
    
    Args:
        directory_path (str): 文档所在的目录路径
        db_name (str, optional): 向量数据库名称
        file_types (List[str], optional): 要加载的文件类型列表，如["pdf", "docx", "txt"]
        recursive (bool, optional): 是否递归处理子目录
        chunk_size (int, optional): 文本块大小
        chunk_overlap (int, optional): 文本块重叠大小
        
    Returns:
        str: 处理结果描述
    """
    if not LANGCHAIN_AVAILABLE:
        return "错误: 未安装必要的依赖库。请运行: pip install langchain langchain-openai chromadb pypdf docx2txt tiktoken"
    
    if not os.path.exists(directory_path):
        return f"错误: 目录'{directory_path}'不存在"
    
    if not os.path.isdir(directory_path):
        return f"错误: '{directory_path}'不是目录"
    
    # 默认支持的文件类型
    if file_types is None:
        file_types = ["pdf", "docx", "doc", "txt", "csv"]
    
    # 确保所有文件类型都是小写且不带点
    file_types = [ft.lower().lstrip('.') for ft in file_types]
    
    # 收集所有符合条件的文件
    all_files = []
    
    if recursive:
        for root, _, files in os.walk(directory_path):
            for file in files:
                if any(file.lower().endswith(f".{ft}") for ft in file_types):
                    all_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path) and any(file.lower().endswith(f".{ft}") for ft in file_types):
                all_files.append(file_path)
    
    if not all_files:
        return f"在目录'{directory_path}'中未找到符合条件的文档"
    
    # 加载并处理所有文档
    documents = []
    file_stats = {"total": 0}
    
    for file_path in all_files:
        try:
            file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            file_stats["total"] += 1
            file_stats[file_ext] = file_stats.get(file_ext, 0) + 1
            
            if file_ext == 'pdf':
                loader = PyPDFLoader(file_path)
            elif file_ext in ['docx', 'doc']:
                loader = Docx2txtLoader(file_path)
            elif file_ext == 'txt':
                loader = TextLoader(file_path, encoding='utf-8')
            elif file_ext in ['csv', 'tsv']:
                loader = CSVLoader(file_path)
            else:
                continue
                
            docs = loader.load()
            
            # 添加文件名元数据
            for doc in docs:
                if not hasattr(doc, 'metadata'):
                    doc.metadata = {}
                doc.metadata['source_file'] = os.path.basename(file_path)
                
            documents.extend(docs)
            
        except Exception as e:
            return f"处理文件'{file_path}'时出错: {str(e)}"
    
    if not documents:
        return "成功处理文件，但未提取到内容"
        
    # 分割文档为较小的块
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(documents)
    
    # 创建向量存储目录
    db_path = os.path.join(DEFAULT_DB_PATH, db_name)
    os.makedirs(db_path, exist_ok=True)
    
    # 使用统一的嵌入获取函数
    config = ConfigManager()
    embedding_type = config.get("embeddings", "provider", fallback="openai")
    embeddings = get_embeddings(embedding_type, config)
    
    # 创建并保存向量数据库
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=db_path
    )
    vector_db.persist()
    
    # 保存数据库元信息
    metadata = {
        "directory": os.path.abspath(directory_path),
        "file_count": file_stats,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "chunk_count": len(chunks),
        "created_at": datetime.now().isoformat(),
    }
    
    with open(os.path.join(db_path, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # 生成处理报告
    file_report = ", ".join([f"{ext}: {count}" for ext, count in file_stats.items() if ext != "total"])
    
    return f"成功处理{file_stats['total']}个文档（{file_report}）。\n" \
           f"共生成{len(chunks)}个文本块，向量数据库已保存为'{db_name}'。"


@tool(name="list_reference_dbs", description="列出所有可用的参考资料数据库")
def list_reference_dbs() -> str:
    """
    列出所有可用的参考资料数据库
    
    Returns:
        str: 数据库列表及其信息
    """
    if not os.path.exists(DEFAULT_DB_PATH):
        return "未找到任何参考资料数据库"
    
    dbs = []
    
    for db_name in os.listdir(DEFAULT_DB_PATH):
        db_path = os.path.join(DEFAULT_DB_PATH, db_name)
        if not os.path.isdir(db_path):
            continue
            
        # 尝试读取元数据
        metadata_path = os.path.join(db_path, "metadata.json")
        metadata = {}
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            except:
                pass
        
        db_info = {
            "name": db_name,
            "path": db_path,
            "created": metadata.get("created_at", "未知"),
            "chunks": metadata.get("chunk_count", "未知"),
            "source": metadata.get("file_name", metadata.get("directory", "未知")),
        }
        
        dbs.append(db_info)
    
    if not dbs:
        return "未找到任何参考资料数据库"
    
    result = "可用的参考资料数据库：\n\n"
    for i, db in enumerate(dbs, 1):
        result += f"{i}. 名称: {db['name']}\n"
        result += f"   来源: {db['source']}\n"
        result += f"   创建时间: {db['created']}\n"
        result += f"   文本块数: {db['chunks']}\n\n"
    
    return result


@tool(name="semantic_search", description="在参考资料中进行语义搜索")
def semantic_search(query: str, db_name: str, limit: int = 5, min_relevance: float = 0.0) -> str:
    """
    在向量数据库中进行语义搜索
    
    Args:
        query (str): 搜索查询
        db_name (str): 向量数据库名称
        limit (int, optional): 返回结果数量上限
        min_relevance (float, optional): 最低相关度阈值(0.0-1.0)，设为0表示不过滤
        
    Returns:
        str: 搜索结果
    """
    if not LANGCHAIN_AVAILABLE:
        return "错误: 未安装必要的依赖库。请运行: pip install langchain langchain-openai chromadb"
    
    db_path = os.path.join(DEFAULT_DB_PATH, db_name)
    if not os.path.exists(db_path):
        return f"错误: 数据库'{db_name}'不存在，请先加载文档"
    
    try:
        # 使用统一的嵌入获取函数
        config = ConfigManager()
        embedding_type = config.get("embeddings", "provider", fallback="openai")
        embeddings = get_embeddings(embedding_type, config)
        
        # 加载向量数据库
        vector_db = Chroma(
            persist_directory=db_path,
            embedding_function=embeddings
        )
        
        # 使用MMR搜索以提高结果多样性
        results = vector_db.max_marginal_relevance_search(
            query, 
            k=limit*2,  # 先检索更多结果，然后过滤
            fetch_k=limit*3
        )
        
        if min_relevance > 0 and hasattr(vector_db, "_collection"):
            # 获取查询向量的嵌入
            query_embedding = embeddings.embed_query(query)
            
            # 计算相似度并过滤结果
            filtered_results = []
            for doc in results:
                # 通过文档ID找到对应的嵌入
                doc_id = doc.metadata.get("_id", "")
                if doc_id:
                    # 查询相似度（简化实现，实际可能需要调整）
                    try:
                        similarity = vector_db._collection.get(ids=[doc_id], include=["embeddings"])
                        if similarity and "embeddings" in similarity:
                            # 计算余弦相似度
                            from numpy import dot
                            from numpy.linalg import norm
                            
                            doc_embedding = similarity["embeddings"][0]
                            cos_sim = dot(query_embedding, doc_embedding)/(norm(query_embedding)*norm(doc_embedding))
                            
                            if cos_sim >= min_relevance:
                                filtered_results.append((doc, cos_sim))
                    except:
                        # 如果无法计算相似度，仍保留该结果
                        filtered_results.append((doc, 0))
            
            # 按相似度排序
            filtered_results.sort(key=lambda x: x[1], reverse=True)
            results = [item[0] for item in filtered_results[:limit]]
        else:
            # 如果不过滤，直接取前limit个结果
            results = results[:limit]
        
        if not results:
            return f"在参考资料中未找到与'{query}'相关的内容"
        
        # 尝试获取数据库元数据
        metadata_path = os.path.join(db_path, "metadata.json")
        db_metadata = {}
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    db_metadata = json.load(f)
            except:
                pass
        
        # 格式化搜索结果
        response = f"在'{db_name}'中找到{len(results)}个与查询相关的内容：\n\n"
        
        for i, doc in enumerate(results):
            # 获取来源信息
            source = doc.metadata.get("source", "")
            if not source:
                source = doc.metadata.get("source_file", "未知来源")
                
            page = doc.metadata.get("page", "")
            source_info = f"{source}"
            if page:
                source_info += f" (第{page}页)"
                
            # 提取文本内容，限制长度
            content = doc.page_content
            if len(content) > 800:
                content = content[:797] + "..."
                
            response += f"【结果 {i+1}】来源: {source_info}\n{content}\n\n"
            
            # 如果超过3个结果，添加分隔线
            if i < len(results) - 1 and i >= 2:
                response += "---\n\n"
        
        # 添加使用提示
        response += "提示: 您可以使用这些相关内容来丰富您的写作。"
        
        return response
        
    except Exception as e:
        return f"搜索时出错: {str(e)}"


@tool(name="reference_with_search", description="结合多个参考资料库搜索信息")
def reference_with_search(query: str, db_names: List[str] = None, limit_per_db: int = 3) -> str:
    """
    在多个向量数据库中同时搜索信息
    
    Args:
        query (str): 搜索查询
        db_names (List[str], optional): 要搜索的数据库名称列表，为空则搜索所有数据库
        limit_per_db (int, optional): 每个数据库返回的最大结果数
        
    Returns:
        str: 搜索结果
    """
    if not LANGCHAIN_AVAILABLE:
        return "错误: 未安装必要的依赖库"
    
    # 如果未指定数据库，获取所有可用数据库
    if not db_names:
        if not os.path.exists(DEFAULT_DB_PATH):
            return "错误: 未找到任何参考资料数据库"
            
        db_names = []
        for name in os.listdir(DEFAULT_DB_PATH):
            path = os.path.join(DEFAULT_DB_PATH, name)
            if os.path.isdir(path):
                db_names.append(name)
        
        if not db_names:
            return "错误: 未找到任何参考资料数据库"
    
    all_results = []
    searched_dbs = []
    
    # 在每个数据库中搜索
    for db_name in db_names:
        db_path = os.path.join(DEFAULT_DB_PATH, db_name)
        if not os.path.exists(db_path):
            continue
            
        try:
            # 使用统一的嵌入获取函数
            config = ConfigManager()
            embedding_type = config.get("embeddings", "provider", fallback="openai")
            embeddings = get_embeddings(embedding_type, config)
            
            # 加载向量数据库
            vector_db = Chroma(
                persist_directory=db_path,
                embedding_function=embeddings
            )
            
            # 搜索相似内容
            results = vector_db.similarity_search(query, k=limit_per_db)
            
            if results:
                searched_dbs.append(db_name)
                for doc in results:
                    # 添加数据库名称
                    if not hasattr(doc, 'metadata'):
                        doc.metadata = {}
                    doc.metadata['db_name'] = db_name
                    all_results.append(doc)
                    
        except Exception as e:
            # 如果某个数据库搜索失败，继续搜索其他数据库
            continue
    
    if not all_results:
        return f"在所有参考资料中未找到与'{query}'相关的内容"
    
    # 对所有结果按相关性排序（简化处理）
    # 在完整实现中，可以重新对所有结果进行嵌入和相似度计算
    
    # 格式化搜索结果
    response = f"在{len(searched_dbs)}个数据库中找到{len(all_results)}个与查询相关的内容：\n\n"
    
    for i, doc in enumerate(all_results[:10]):  # 最多显示10个结果
        # 获取来源信息
        db = doc.metadata.get("db_name", "未知数据库")
        source = doc.metadata.get("source", "")
        if not source:
            source = doc.metadata.get("source_file", "未知来源")
            
        page = doc.metadata.get("page", "")
        source_info = f"{source}"
        if page:
            source_info += f" (第{page}页)"
            
        # 提取文本内容，限制长度
        content = doc.page_content
        if len(content) > 600:
            content = content[:597] + "..."
            
        response += f"【结果 {i+1}】数据库: {db}, 来源: {source_info}\n{content}\n\n"
        
        # 超过5个结果，添加分隔线
        if i < min(9, len(all_results)-1) and i >= 4:
            response += "---\n\n"
    
    # 如果结果超过10个，添加提示
    if len(all_results) > 10:
        response += f"还有{len(all_results)-10}个相关结果未显示。请提供更具体的查询以获得更精确的结果。\n\n"
    
    return response


@tool(name="delete_reference_db", description="删除参考资料数据库")
def delete_reference_db(db_name: str) -> str:
    """
    删除指定的参考资料数据库
    
    Args:
        db_name (str): 要删除的数据库名称
        
    Returns:
        str: 操作结果
    """
    db_path = os.path.join(DEFAULT_DB_PATH, db_name)
    if not os.path.exists(db_path):
        return f"错误: 数据库'{db_name}'不存在"
    
    try:
        import shutil
        shutil.rmtree(db_path)
        return f"成功删除数据库'{db_name}'"
    except Exception as e:
        return f"删除数据库时出错: {str(e)}"


@tool(name="save_with_references", description="保存带有参考资料引用的文章")
def save_with_references(title: str, content: str, references: List[str], 
                        format: str = "md", save_dir: str = "./articles") -> str:
    """
    保存带有参考资料引用的文章
    
    Args:
        title (str): 文章标题
        content (str): 文章内容
        references (List[str]): 参考资料列表，每项为一条引用信息
        format (str, optional): 文件格式，如"md", "txt", "html"
        save_dir (str, optional): 保存目录
        
    Returns:
        str: 操作结果
    """
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    # 处理文件名
    filename = re.sub(r'[<>:"/\\|?*]', '_', title)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.{format}"
    file_path = os.path.join(save_dir, full_filename)
    
    try:
        # 根据不同格式处理内容
        if format == "md":
            final_content = f"# {title}\n\n{content}\n\n## 参考资料\n\n"
            for i, ref in enumerate(references, 1):
                final_content += f"{i}. {ref}\n"
                
        elif format == "html":
            final_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 2em; }}
        h1 {{ color: #333; }}
        .references {{ margin-top: 2em; border-top: 1px solid #ccc; padding-top: 1em; }}
        .reference {{ margin-bottom: 0.5em; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="content">
        {content.replace('\n', '<br>')}
    </div>
    <div class="references">
        <h2>参考资料</h2>
        <ol>"""
            
            for ref in references:
                final_content += f"\n            <li class=\"reference\">{ref}</li>"
                
            final_content += """
        </ol>
    </div>
</body>
</html>"""
            
        else:  # txt或其他格式
            final_content = f"{title}\n\n{content}\n\n参考资料：\n"
            for i, ref in enumerate(references, 1):
                final_content += f"{i}. {ref}\n"
        
        # 保存文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_content)
            
        return f"已将文章保存到: {file_path}"
        
    except Exception as e:
        return f"保存文章时出错: {str(e)}"


def main():
    """
    测试函数
    """
    print("参考资料工具模块 - 提供向量数据库支持的文档处理和语义搜索功能")
    print("此模块通常与写作助手集成使用，不单独运行")
    
    # 检查依赖安装
    if not LANGCHAIN_AVAILABLE:
        print("\n错误: 未安装必要的依赖库")
        print("请运行以下命令安装依赖:")
        print("pip install langchain langchain-openai chromadb pypdf docx2txt tiktoken")
        return
    
    print("\n所有依赖已正确安装，模块可以使用")
    print("\n可用工具:")
    print("- load_document: 加载单个文档并构建向量数据库")
    print("- load_documents: 加载目录中的所有文档并构建向量数据库") 
    print("- list_reference_dbs: 列出所有可用的参考资料数据库")
    print("- semantic_search: 在参考资料中进行语义搜索")
    print("- reference_with_search: 结合多个参考资料库搜索信息")
    print("- delete_reference_db: 删除参考资料数据库")
    print("- save_with_references: 保存带有参考资料引用的文章")


if __name__ == "__main__":
    main() 