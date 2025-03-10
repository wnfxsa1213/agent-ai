"""
向量数据库管理界面 - 提供图形化操作向量数据库的功能
"""

import os
import sys
import streamlit as st
import shutil
from datetime import datetime
import json
import zipfile

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 现在导入项目内的模块
from core.config_manager import ConfigManager

# 导入必要的库
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, Docx2txtLoader, TextLoader, CSVLoader
)

# 路径设置
DEFAULT_DB_PATH = os.path.join(parent_dir, "reference_dbs")
TEMP_DIR = os.path.join(parent_dir, "temp")
CONFIG_PATH = os.path.join(parent_dir, "config.ini")

# 确保目录存在
os.makedirs(DEFAULT_DB_PATH, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# 文档加载和处理函数
def load_document(file_path):
    """根据文件类型加载文档"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        loader = PyPDFLoader(file_path)
    elif file_ext in ['.docx', '.doc']:
        loader = Docx2txtLoader(file_path)
    elif file_ext in ['.csv', '.tsv']:
        loader = CSVLoader(file_path)
    else:  # 默认作为文本文件处理
        loader = TextLoader(file_path, encoding='utf-8')
        
    return loader.load()

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    """将文档分割成更小的块"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)

def get_embeddings(embedding_type="openai", api_key=None, model=None, api_base=None):
    """获取嵌入对象"""
    config = ConfigManager(CONFIG_PATH)
    
    if embedding_type == "openai":
        # 优先使用传入的API密钥
        if not api_key:
            api_key = config.get("embeddings", "api_key", fallback="")
            if not api_key:
                api_key = os.environ.get("OPENAI_API_KEY", "")
        
        # 优先使用传入的模型名称
        if not model:
            model = config.get("embeddings", "model", fallback="text-embedding-3-small")
        
        # 优先使用传入的API基础URL
        if not api_base:
            api_base = config.get("embeddings", "api_base", fallback="https://api.openai.com/v1")
        
        return OpenAIEmbeddings(
            openai_api_key=api_key,
            model=model,
            openai_api_base=api_base  # 添加自定义API地址
        )
    elif embedding_type == "local":
        model_name = config.get("embeddings", "local_model", 
                              fallback="shibing624/text2vec-base-chinese")
        
        return HuggingFaceEmbeddings(
            model_name=model_name
        )
    else:
        raise ValueError(f"不支持的嵌入类型: {embedding_type}")

# 主UI界面
def main():
    st.set_page_config(
        page_title="向量数据库管理工具",
        page_icon="📚",
        layout="wide"
    )
    
    # 导入配置
    config = ConfigManager(CONFIG_PATH)
    
    # 标题和介绍
    st.title("📚 向量数据库管理工具")
    st.markdown("""
    这个工具可以帮助您可视化操作向量数据库，包括创建数据库、添加内容、搜索和管理。
    """)
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # 嵌入模型配置
        embedding_type = st.radio(
            "选择嵌入模型类型",
            ["OpenAI (在线)", "HuggingFace (本地)"],
            index=0
        )
        
        embedding_provider = "openai" if embedding_type == "OpenAI (在线)" else "local"
        
        # OpenAI设置
        if embedding_provider == "openai":
            api_key = st.text_input(
                "OpenAI API密钥", 
                value=config.get("embeddings", "api_key", fallback=""),
                type="password"
            )
            
            api_base = st.text_input(
                "OpenAI API地址",
                value=config.get("embeddings", "api_base", fallback="https://api.openai.com/v1"),
                help="自定义API地址，例如代理服务器地址"
            )
            
            model = st.selectbox(
                "嵌入模型",
                ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
                index=0
            )
            
            # 保存设置到配置文件
            if st.button("保存API设置"):
                if api_key:
                    config.set("embeddings", "provider", "openai")
                    config.set("embeddings", "api_key", api_key)
                    config.set("embeddings", "model", model)
                    config.set("embeddings", "api_base", api_base)  # 保存API地址
                    config.save()
                    st.success("✅ 设置已保存")
                else:
                    st.error("❌ API密钥不能为空")
        
        # 本地模型设置
        else:
            local_model = st.text_input(
                "本地模型名称",
                value=config.get("embeddings", "local_model", fallback="shibing624/text2vec-base-chinese")
            )
            
            # 保存设置到配置文件
            if st.button("保存本地模型设置"):
                if local_model:
                    config.set("embeddings", "provider", "local")
                    config.set("embeddings", "local_model", local_model)
                    config.save()
                    st.success("✅ 设置已保存")
                else:
                    st.error("❌ 模型名称不能为空")
        
        st.markdown("---")
        st.markdown("### 文档设置")
        
        chunk_size = st.slider(
            "文本块大小",
            min_value=100,
            max_value=2000,
            value=1000,
            step=100,
            help="每个文本块的最大字符数。较小的块可提高搜索准确度，但会增加处理时间和存储空间。"
        )
        
        chunk_overlap = st.slider(
            "文本块重叠",
            min_value=0,
            max_value=500,
            value=200,
            step=50,
            help="相邻文本块之间重叠的字符数。增加重叠可以提高连续性，但会增加存储空间。"
        )
    
    # 主要操作区域
    tabs = st.tabs(["创建数据库", "添加内容", "搜索", "管理数据库"])
    
    # 获取现有数据库列表
    existing_dbs = []
    if os.path.exists(DEFAULT_DB_PATH):
        existing_dbs = [d for d in os.listdir(DEFAULT_DB_PATH) 
                        if os.path.isdir(os.path.join(DEFAULT_DB_PATH, d))]
    
    # Tab 1: 创建数据库
    with tabs[0]:
        st.header("🆕 创建新数据库")
        
        # 数据库名称
        db_name = st.text_input("数据库名称", key="create_db_name")
        
        # 输入方式选择
        input_method = st.radio("选择输入方式", ["上传文件", "上传文件夹", "直接输入文本"], key="create_input_method")
        
        if input_method == "上传文件":
            uploaded_file = st.file_uploader(
                "选择文件", 
                type=["pdf", "txt", "docx", "doc", "csv"],
                help="支持PDF、Word、TXT和CSV文件"
            )
            
            if uploaded_file and db_name:
                # 保存上传的文件
                file_path = os.path.join(TEMP_DIR, uploaded_file.name)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"✅ 文件已上传: {uploaded_file.name}")
                
                if st.button("处理文件并创建数据库", key="create_from_file"):
                    with st.spinner("处理中..."):
                        try:
                            # 加载文档
                            documents = load_document(file_path)
                            
                            # 分割文档
                            chunks = split_documents(documents, chunk_size, chunk_overlap)
                            
                            if not chunks:
                                st.error("❌ 无法从文件中提取内容")
                                # 删除临时文件
                                os.remove(file_path)
                                st.stop()
                            
                            # 获取嵌入对象
                            try:
                                embeddings = get_embeddings(
                                    embedding_provider,
                                    api_key if embedding_provider == "openai" else None,
                                    model if embedding_provider == "openai" else None,
                                    api_base if embedding_provider == "openai" else None
                                )
                            except Exception as e:
                                st.error(f"❌ 创建嵌入对象失败: {str(e)}")
                                # 删除临时文件
                                os.remove(file_path)
                                st.stop()
                            
                            # 创建数据库目录
                            db_path = os.path.join(DEFAULT_DB_PATH, db_name)
                            os.makedirs(db_path, exist_ok=True)
                            
                            # 创建向量数据库
                            vector_db = Chroma.from_documents(
                                documents=chunks,
                                embedding=embeddings,
                                persist_directory=db_path
                            )
                            vector_db.persist()
                            
                            # 保存数据库元信息
                            metadata = {
                                "name": db_name,
                                "file_name": uploaded_file.name,
                                "file_type": os.path.splitext(uploaded_file.name)[1].lstrip('.'),
                                "chunk_size": chunk_size,
                                "chunk_overlap": chunk_overlap,
                                "chunk_count": len(chunks),
                                "embedding_provider": embedding_provider,
                                "embedding_model": model if embedding_provider == "openai" else local_model,
                                "created_at": datetime.now().isoformat(),
                            }
                            
                            with open(os.path.join(db_path, "metadata.json"), "w", encoding="utf-8") as f:
                                json.dump(metadata, f, ensure_ascii=False, indent=2)
                            
                            # 删除临时文件
                            os.remove(file_path)
                            
                            st.success(f"✅ 数据库 '{db_name}' 创建成功！共包含 {len(chunks)} 个文本块。")
                            
                            # 显示数据库信息
                            st.info(f"""
                            📊 数据库信息:
                            - 名称: {db_name}
                            - 来源文件: {uploaded_file.name}
                            - 文本块数量: {len(chunks)}
                            - 嵌入模型: {"OpenAI" if embedding_provider == "openai" else "本地"} ({model if embedding_provider == "openai" else local_model})
                            - 创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                            """)
                        
                        except Exception as e:
                            st.error(f"❌ 创建数据库失败: {str(e)}")
                            # 清理临时文件
                            if os.path.exists(file_path):
                                os.remove(file_path)
        
        elif input_method == "上传文件夹":
            st.info("📁 请指定文件夹路径（需要在服务器上可访问）")
            folder_path = st.text_input("文件夹路径", key="create_folder_path")
            
            file_types = st.multiselect(
                "选择文件类型",
                ["pdf", "docx", "doc", "txt", "csv"],
                default=["pdf", "docx", "txt"],
                help="选择要处理的文件类型"
            )
            
            recursive = st.checkbox("递归处理子文件夹", value=True)
            
            if folder_path and db_name and file_types:
                if not os.path.exists(folder_path):
                    st.error(f"❌ 文件夹不存在: {folder_path}")
                else:
                    if st.button("处理文件夹并创建数据库", key="create_from_folder"):
                        with st.spinner("处理中..."):
                            try:
                                # 收集所有符合条件的文件
                                all_files = []
                                
                                if recursive:
                                    for root, _, files in os.walk(folder_path):
                                        for file in files:
                                            if any(file.lower().endswith(f".{ft}") for ft in file_types):
                                                all_files.append(os.path.join(root, file))
                                else:
                                    for file in os.listdir(folder_path):
                                        file_path = os.path.join(folder_path, file)
                                        if os.path.isfile(file_path) and any(file.lower().endswith(f".{ft}") for ft in file_types):
                                            all_files.append(file_path)
                                
                                if not all_files:
                                    st.error(f"❌ 在文件夹中未找到符合条件的文档")
                                    st.stop()
                                
                                # 创建进度条
                                progress_bar = st.progress(0)
                                progress_text = st.empty()
                                
                                # 加载并处理所有文档
                                documents = []
                                file_stats = {"total": 0}
                                
                                for i, file_path in enumerate(all_files):
                                    progress_text.text(f"处理文件 {i+1}/{len(all_files)}: {os.path.basename(file_path)}")
                                    progress_bar.progress((i) / len(all_files))
                                    
                                    try:
                                        file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
                                        file_stats["total"] += 1
                                        file_stats[file_ext] = file_stats.get(file_ext, 0) + 1
                                        
                                        docs = load_document(file_path)
                                        
                                        # 添加文件名元数据
                                        for doc in docs:
                                            if not hasattr(doc, 'metadata'):
                                                doc.metadata = {}
                                            doc.metadata['source_file'] = os.path.basename(file_path)
                                            
                                        documents.extend(docs)
                                        
                                    except Exception as e:
                                        st.warning(f"⚠️ 处理文件 '{os.path.basename(file_path)}' 时出错: {str(e)}")
                                
                                progress_bar.progress(1.0)
                                progress_text.text(f"分割文档...")
                                
                                if not documents:
                                    st.error("❌ 成功处理文件，但未提取到内容")
                                    st.stop()
                                    
                                # 分割文档
                                chunks = split_documents(documents, chunk_size, chunk_overlap)
                                
                                progress_text.text(f"创建向量数据库...")
                                
                                # 获取嵌入对象
                                try:
                                    embeddings = get_embeddings(
                                        embedding_provider,
                                        api_key if embedding_provider == "openai" else None,
                                        model if embedding_provider == "openai" else None,
                                        api_base if embedding_provider == "openai" else None
                                    )
                                except Exception as e:
                                    st.error(f"❌ 创建嵌入对象失败: {str(e)}")
                                    st.stop()
                                
                                # 创建数据库目录
                                db_path = os.path.join(DEFAULT_DB_PATH, db_name)
                                os.makedirs(db_path, exist_ok=True)
                                
                                # 创建向量数据库
                                vector_db = Chroma.from_documents(
                                    documents=chunks,
                                    embedding=embeddings,
                                    persist_directory=db_path
                                )
                                vector_db.persist()
                                
                                # 生成文件统计信息
                                file_report = ", ".join([f"{ext}: {count}" for ext, count in file_stats.items() if ext != "total"])
                                
                                # 保存数据库元信息
                                metadata = {
                                    "name": db_name,
                                    "directory": os.path.abspath(folder_path),
                                    "file_count": file_stats,
                                    "chunk_size": chunk_size,
                                    "chunk_overlap": chunk_overlap,
                                    "chunk_count": len(chunks),
                                    "embedding_provider": embedding_provider,
                                    "embedding_model": model if embedding_provider == "openai" else local_model,
                                    "created_at": datetime.now().isoformat(),
                                }
                                
                                with open(os.path.join(db_path, "metadata.json"), "w", encoding="utf-8") as f:
                                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                                
                                # 更新进度并显示完成信息
                                progress_text.empty()
                                progress_bar.empty()
                                
                                st.success(f"✅ 数据库 '{db_name}' 创建成功！共处理 {file_stats['total']} 个文件，生成 {len(chunks)} 个文本块。")
                                
                                # 显示数据库信息
                                st.info(f"""
                                📊 数据库信息:
                                - 名称: {db_name}
                                - 来源目录: {folder_path}
                                - 处理文件: {file_stats['total']} 个 ({file_report})
                                - 文本块数量: {len(chunks)}
                                - 嵌入模型: {"OpenAI" if embedding_provider == "openai" else "本地"} ({model if embedding_provider == "openai" else local_model})
                                - 创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                                """)
                            
                            except Exception as e:
                                st.error(f"❌ 创建数据库失败: {str(e)}")
        
        elif input_method == "直接输入文本":
            text_input = st.text_area(
                "输入文本内容", 
                height=300,
                help="直接输入或粘贴文本内容"
            )
            
            if text_input and db_name:
                if st.button("处理文本并创建数据库", key="create_from_text"):
                    with st.spinner("处理中..."):
                        try:
                            # 分割文本
                            text_splitter = RecursiveCharacterTextSplitter(
                                chunk_size=chunk_size,
                                chunk_overlap=chunk_overlap
                            )
                            chunks = text_splitter.create_documents([text_input])
                            
                            # 获取嵌入对象
                            try:
                                embeddings = get_embeddings(
                                    embedding_provider,
                                    api_key if embedding_provider == "openai" else None,
                                    model if embedding_provider == "openai" else None,
                                    api_base if embedding_provider == "openai" else None
                                )
                            except Exception as e:
                                st.error(f"❌ 创建嵌入对象失败: {str(e)}")
                                st.stop()
                            
                            # 创建数据库目录
                            db_path = os.path.join(DEFAULT_DB_PATH, db_name)
                            os.makedirs(db_path, exist_ok=True)
                            
                            # 创建向量数据库
                            vector_db = Chroma.from_documents(
                                documents=chunks,
                                embedding=embeddings,
                                persist_directory=db_path
                            )
                            vector_db.persist()
                            
                            # 保存数据库元信息
                            metadata = {
                                "name": db_name,
                                "source": "直接输入文本",
                                "text_length": len(text_input),
                                "chunk_size": chunk_size,
                                "chunk_overlap": chunk_overlap,
                                "chunk_count": len(chunks),
                                "embedding_provider": embedding_provider,
                                "embedding_model": model if embedding_provider == "openai" else local_model,
                                "created_at": datetime.now().isoformat(),
                            }
                            
                            with open(os.path.join(db_path, "metadata.json"), "w", encoding="utf-8") as f:
                                json.dump(metadata, f, ensure_ascii=False, indent=2)
                            
                            st.success(f"✅ 数据库 '{db_name}' 创建成功！共包含 {len(chunks)} 个文本块。")
                            
                            # 显示数据库信息
                            st.info(f"""
                            📊 数据库信息:
                            - 名称: {db_name}
                            - 来源: 直接输入文本
                            - 文本长度: {len(text_input)} 字符
                            - 文本块数量: {len(chunks)}
                            - 嵌入模型: {"OpenAI" if embedding_provider == "openai" else "本地"} ({model if embedding_provider == "openai" else local_model})
                            - 创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                            """)
                            
                        except Exception as e:
                            st.error(f"❌ 创建数据库失败: {str(e)}")
    
    # Tab 2: 添加内容
    with tabs[1]:
        st.header("➕ 向数据库添加内容")
        
        if not existing_dbs:
            st.info("⚠️ 目前没有现有数据库，请先创建一个数据库")
        else:
            selected_db = st.selectbox("选择数据库", existing_dbs, key="add_db_select")
            
            # 输入方式选择
            input_method = st.radio("选择输入方式", ["上传文件", "直接输入文本"], key="add_input_method")
            
            if input_method == "上传文件":
                uploaded_file = st.file_uploader(
                    "选择文件", 
                    type=["pdf", "txt", "docx", "doc", "csv"],
                    key="add_file_uploader"
                )
                
                if uploaded_file and selected_db:
                    # 保存上传的文件
                    file_path = os.path.join(TEMP_DIR, uploaded_file.name)
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.success(f"✅ 文件已上传: {uploaded_file.name}")
                    
                    if st.button("处理文件并添加到数据库", key="add_from_file"):
                        with st.spinner("处理中..."):
                            try:
                                # 加载文档
                                documents = load_document(file_path)
                                
                                # 分割文档
                                chunks = split_documents(documents, chunk_size, chunk_overlap)
                                
                                if not chunks:
                                    st.error("❌ 无法从文件中提取内容")
                                    # 删除临时文件
                                    os.remove(file_path)
                                    st.stop()
                                
                                # 获取嵌入对象
                                try:
                                    embeddings = get_embeddings(
                                        embedding_provider,
                                        api_key if embedding_provider == "openai" else None,
                                        model if embedding_provider == "openai" else None,
                                        api_base if embedding_provider == "openai" else None
                                    )
                                except Exception as e:
                                    st.error(f"❌ 创建嵌入对象失败: {str(e)}")
                                    # 删除临时文件
                                    os.remove(file_path)
                                    st.stop()
                                
                                # 加载现有数据库
                                db_path = os.path.join(DEFAULT_DB_PATH, selected_db)
                                
                                vector_db = Chroma(
                                    persist_directory=db_path,
                                    embedding_function=embeddings
                                )
                                
                                # 添加新文档
                                vector_db.add_documents(chunks)
                                vector_db.persist()
                                
                                # 更新元数据
                                metadata_path = os.path.join(db_path, "metadata.json")
                                if os.path.exists(metadata_path):
                                    try:
                                        with open(metadata_path, "r", encoding="utf-8") as f:
                                            metadata = json.load(f)
                                            
                                        # 更新元数据
                                        metadata["chunk_count"] = metadata.get("chunk_count", 0) + len(chunks)
                                        metadata["last_updated"] = datetime.now().isoformat()
                                        
                                        # 更新文件信息
                                        if "file_count" not in metadata:
                                            metadata["file_count"] = {"total": 0}
                                        
                                        metadata["file_count"]["total"] = metadata["file_count"].get("total", 0) + 1
                                        
                                        file_ext = os.path.splitext(uploaded_file.name)[1].lower().lstrip('.')
                                        metadata["file_count"][file_ext] = metadata["file_count"].get(file_ext, 0) + 1
                                        
                                        with open(metadata_path, "w", encoding="utf-8") as f:
                                            json.dump(metadata, f, ensure_ascii=False, indent=2)
                                    except Exception as e:
                                        st.warning(f"⚠️ 更新元数据失败: {str(e)}")
                                
                                # 删除临时文件
                                os.remove(file_path)
                                
                                st.success(f"✅ 成功添加 {len(chunks)} 个文本块到数据库 '{selected_db}'")
                                
                            except Exception as e:
                                st.error(f"❌ 添加内容失败: {str(e)}")
                                # 清理临时文件
                                if os.path.exists(file_path):
                                    os.remove(file_path)
            
            elif input_method == "直接输入文本":
                text_input = st.text_area(
                    "输入要添加的文本内容", 
                    height=300, 
                    key="add_text_input"
                )
                
                if text_input and selected_db:
                    if st.button("添加文本到数据库", key="add_from_text"):
                        with st.spinner("处理中..."):
                            try:
                                # 分割文本
                                text_splitter = RecursiveCharacterTextSplitter(
                                    chunk_size=chunk_size,
                                    chunk_overlap=chunk_overlap
                                )
                                chunks = text_splitter.create_documents([text_input])
                                
                                # 获取嵌入对象
                                try:
                                    embeddings = get_embeddings(
                                        embedding_provider,
                                        api_key if embedding_provider == "openai" else None,
                                        model if embedding_provider == "openai" else None,
                                        api_base if embedding_provider == "openai" else None
                                    )
                                except Exception as e:
                                    st.error(f"❌ 创建嵌入对象失败: {str(e)}")
                                    st.stop()
                                
                                # 加载现有数据库
                                db_path = os.path.join(DEFAULT_DB_PATH, selected_db)
                                
                                vector_db = Chroma(
                                    persist_directory=db_path,
                                    embedding_function=embeddings
                                )
                                
                                # 添加新文档
                                vector_db.add_documents(chunks)
                                vector_db.persist()
                                
                                # 更新元数据
                                metadata_path = os.path.join(db_path, "metadata.json")
                                if os.path.exists(metadata_path):
                                    try:
                                        with open(metadata_path, "r", encoding="utf-8") as f:
                                            metadata = json.load(f)
                                            
                                        # 更新元数据
                                        metadata["chunk_count"] = metadata.get("chunk_count", 0) + len(chunks)
                                        metadata["last_updated"] = datetime.now().isoformat()
                                        
                                        with open(metadata_path, "w", encoding="utf-8") as f:
                                            json.dump(metadata, f, ensure_ascii=False, indent=2)
                                    except Exception as e:
                                        st.warning(f"⚠️ 更新元数据失败: {str(e)}")
                                
                                st.success(f"✅ 成功添加 {len(chunks)} 个文本块到数据库 '{selected_db}'")
                                
                            except Exception as e:
                                st.error(f"❌ 添加内容失败: {str(e)}")
    
    # Tab 3: 搜索
    with tabs[2]:
        st.header("🔍 搜索数据库")
        
        if not existing_dbs:
            st.info("⚠️ 目前没有现有数据库，请先创建一个数据库")
        else:
            # 单一数据库搜索或全库搜索
            search_mode = st.radio("搜索模式", ["单一数据库", "多数据库"], key="search_mode")
            
            if search_mode == "单一数据库":
                selected_db = st.selectbox("选择要搜索的数据库", existing_dbs, key="search_db_select")
                
                query = st.text_input("输入搜索查询", key="search_query")
                
                col1, col2 = st.columns(2)
                with col1:
                    limit = st.slider("返回结果数量", 1, 20, 5, key="search_limit")
                with col2:
                    min_relevance = st.slider("最低相关度", 0.0, 1.0, 0.0, 0.05, key="search_min_relevance", 
                                         help="0表示不过滤，值越高表示结果越相关")
                
                if query:
                    if st.button("搜索", key="search_button"):
                        with st.spinner("搜索中..."):
                            try:
                                # 获取嵌入对象
                                try:
                                    embeddings = get_embeddings(
                                        embedding_provider,
                                        api_key if embedding_provider == "openai" else None,
                                        model if embedding_provider == "openai" else None,
                                        api_base if embedding_provider == "openai" else None
                                    )
                                except Exception as e:
                                    st.error(f"❌ 创建嵌入对象失败: {str(e)}")
                                    st.stop()
                                
                                # 加载数据库
                                db_path = os.path.join(DEFAULT_DB_PATH, selected_db)
                                
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
                                
                                # 如果设置了最低相关度，则过滤结果
                                if min_relevance > 0 and results:
                                    # 使用简化的方法估计相关性（完整实现可能需要更复杂的方法）
                                    filtered_results = results[:limit]
                                else:
                                    filtered_results = results[:limit]
                                
                                if not filtered_results:
                                    st.warning(f"⚠️ 在数据库中未找到与 '{query}' 相关的内容")
                                else:
                                    st.success(f"✅ 找到 {len(filtered_results)} 个相关结果")
                                    
                                    # 显示结果
                                    for i, doc in enumerate(filtered_results):
                                        with st.expander(f"结果 {i+1} - 相关度: {min_relevance if min_relevance > 0 else '未计算'}"):
                                            # 获取来源信息
                                            source = doc.metadata.get("source", "")
                                            if not source:
                                                source = doc.metadata.get("source_file", "未知来源")
                                                
                                            page = doc.metadata.get("page", "")
                                            source_info = f"{source}"
                                            if page:
                                                source_info += f" (第{page}页)"
                                            
                                            st.info(f"**来源:** {source_info}")
                                            st.markdown(doc.page_content)
                                
                            except Exception as e:
                                st.error(f"❌ 搜索失败: {str(e)}")
            
            else:  # 多数据库搜索
                selected_dbs = st.multiselect("选择要搜索的数据库", existing_dbs, default=existing_dbs, key="multi_search_db_select")
                
                query = st.text_input("输入搜索查询", key="multi_search_query")
                
                limit_per_db = st.slider("每个数据库返回结果数量", 1, 10, 3, key="multi_search_limit")
                
                if query and selected_dbs:
                    if st.button("搜索", key="multi_search_button"):
                        with st.spinner("搜索中..."):
                            try:
                                all_results = []
                                
                                # 获取嵌入对象
                                try:
                                    embeddings = get_embeddings(
                                        embedding_provider,
                                        api_key if embedding_provider == "openai" else None,
                                        model if embedding_provider == "openai" else None,
                                        api_base if embedding_provider == "openai" else None
                                    )
                                except Exception as e:
                                    st.error(f"❌ 创建嵌入对象失败: {str(e)}")
                                    st.stop()
                                
                                # 在每个数据库中搜索
                                for db in selected_dbs:
                                    db_path = os.path.join(DEFAULT_DB_PATH, db)
                                    try:
                                        vector_db = Chroma(
                                            persist_directory=db_path,
                                            embedding_function=embeddings
                                        )
                                        
                                        results = vector_db.similarity_search_with_score(
                                            query,
                                            k=limit_per_db
                                        )
                                        
                                        # 添加数据库信息到结果中
                                        for doc, score in results:
                                            doc.metadata["database"] = db
                                            # 转换相似度分数为相关度分数
                                            relevance = 1.0 - score/2  # 简单转换
                                            all_results.append((doc, relevance))
                                    except Exception as e:
                                        st.warning(f"⚠️ 在数据库 '{db}' 中搜索时出错: {str(e)}")
                                
                                # 排序结果（按相关度降序）
                                all_results.sort(key=lambda x: x[1], reverse=True)
                                
                                if not all_results:
                                    st.warning(f"⚠️ 在所有数据库中未找到与 '{query}' 相关的内容")
                                else:
                                    st.success(f"✅ 找到 {len(all_results)} 个相关结果")
                                    
                                    # 显示结果
                                    for i, (doc, relevance) in enumerate(all_results):
                                        with st.expander(f"结果 {i+1} - 来自数据库: {doc.metadata.get('database', '未知')} - 相关度: {relevance:.2f}"):
                                            # 获取来源信息
                                            source = doc.metadata.get("source", "")
                                            if not source:
                                                source = doc.metadata.get("source_file", "未知来源")
                                                
                                            page = doc.metadata.get("page", "")
                                            source_info = f"{source}"
                                            if page:
                                                source_info += f" (第{page}页)"
                                            
                                            st.info(f"**来源:** {source_info}")
                                            st.markdown(doc.page_content)
                            
                            except Exception as e:
                                st.error(f"❌ 搜索失败: {str(e)}")
    
    # Tab 4: 管理数据库
    with tabs[3]:
        st.header("🛠️ 管理数据库")
        
        if not existing_dbs:
            st.info("⚠️ 目前没有现有数据库，请先创建一个数据库")
        else:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("现有数据库")
                
                # 显示数据库列表和详细信息
                for db in existing_dbs:
                    with st.expander(f"📁 {db}"):
                        db_path = os.path.join(DEFAULT_DB_PATH, db)
                        metadata_path = os.path.join(db_path, "metadata.json")
                        
                        if os.path.exists(metadata_path):
                            try:
                                with open(metadata_path, "r", encoding="utf-8") as f:
                                    metadata = json.load(f)
                                
                                # 显示数据库详细信息
                                st.markdown("### 数据库信息")
                                
                                # 创建时间
                                created_at = metadata.get("created_at", "未知")
                                if created_at != "未知":
                                    try:
                                        created_datetime = datetime.fromisoformat(created_at)
                                        created_at = created_datetime.strftime("%Y-%m-%d %H:%M:%S")
                                    except:
                                        pass
                                
                                # 最后更新时间
                                last_updated = metadata.get("last_updated", "与创建时间相同")
                                if last_updated != "与创建时间相同":
                                    try:
                                        updated_datetime = datetime.fromisoformat(last_updated)
                                        last_updated = updated_datetime.strftime("%Y-%m-%d %H:%M:%S")
                                    except:
                                        pass
                                
                                # 生成来源信息
                                source_info = ""
                                if "file_name" in metadata:
                                    source_info = f"文件: {metadata['file_name']}"
                                elif "directory" in metadata:
                                    source_info = f"目录: {metadata['directory']}"
                                    if "file_count" in metadata and isinstance(metadata["file_count"], dict):
                                        file_count = metadata["file_count"]
                                        if "total" in file_count:
                                            source_info += f" ({file_count['total']} 个文件)"
                                elif "source" in metadata:
                                    source_info = f"来源: {metadata['source']}"
                                
                                # 块信息
                                chunk_size = metadata.get("chunk_size", "未知")
                                chunk_overlap = metadata.get("chunk_overlap", "未知")
                                chunk_count = metadata.get("chunk_count", "未知")
                                
                                # 嵌入模型信息
                                embedding_provider = metadata.get("embedding_provider", "未知")
                                embedding_model = metadata.get("embedding_model", "未知")
                                
                                # 显示信息表格
                                st.info(f"""
                                - **名称:** {db}
                                - **创建时间:** {created_at}
                                - **最后更新:** {last_updated}
                                - **来源:** {source_info}
                                - **文本块:** {chunk_count} 个 (大小: {chunk_size}, 重叠: {chunk_overlap})
                                - **嵌入模型:** {embedding_provider} ({embedding_model})
                                """)
                                
                                # 显示文件统计（如果有）
                                if "file_count" in metadata and isinstance(metadata["file_count"], dict):
                                    file_count = metadata["file_count"]
                                    if len(file_count) > 1:  # 不仅仅只有total键
                                        st.subheader("文件统计")
                                        file_stats = {k: v for k, v in file_count.items() if k != "total"}
                                        st.json(file_stats)
                                
                            except Exception as e:
                                st.error(f"无法读取数据库元数据: {str(e)}")
                        else:
                            st.warning("⚠️ 未找到数据库元数据文件")
                        
                        # 数据库操作按钮
                        col_rename, col_delete = st.columns(2)
                        
                        with col_rename:
                            if st.button("重命名", key=f"rename_{db}"):
                                st.session_state[f"rename_db_{db}"] = True
                                st.rerun()
                        
                        with col_delete:
                            if st.button("删除", key=f"delete_{db}"):
                                with st.popover("确认删除"):
                                    st.warning(f"确定要删除数据库 '{db}' 吗？此操作不可撤销。")
                                    if st.button("确认删除", key=f"confirm_delete_{db}"):
                                        try:
                                            shutil.rmtree(db_path)
                                            st.success(f"✅ 数据库 '{db}' 已删除")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ 删除数据库失败: {str(e)}")
                        
                        # 重命名表单
                        if f"rename_db_{db}" in st.session_state and st.session_state[f"rename_db_{db}"]:
                            with st.form(key=f"rename_form_{db}"):
                                new_name = st.text_input("新数据库名称", value=db)
                                
                                col_submit, col_cancel = st.columns(2)
                                with col_submit:
                                    submit = st.form_submit_button("确认重命名")
                                with col_cancel:
                                    cancel = st.form_submit_button("取消")
                                
                                if submit and new_name and new_name != db:
                                    try:
                                        new_db_path = os.path.join(DEFAULT_DB_PATH, new_name)
                                        
                                        if os.path.exists(new_db_path):
                                            st.error(f"❌ 数据库名称 '{new_name}' 已存在")
                                        else:
                                            # 重命名数据库目录
                                            shutil.move(db_path, new_db_path)
                                            
                                            # 更新元数据
                                            metadata_path = os.path.join(new_db_path, "metadata.json")
                                            if os.path.exists(metadata_path):
                                                try:
                                                    with open(metadata_path, "r", encoding="utf-8") as f:
                                                        metadata = json.load(f)
                                                    
                                                    metadata["name"] = new_name
                                                    metadata["last_updated"] = datetime.now().isoformat()
                                                    
                                                    with open(metadata_path, "w", encoding="utf-8") as f:
                                                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                                                except Exception as e:
                                                    st.warning(f"⚠️ 更新元数据失败: {str(e)}")
                                            
                                            st.success(f"✅ 数据库已重命名为 '{new_name}'")
                                            st.session_state.pop(f"rename_db_{db}")
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ 重命名数据库失败: {str(e)}")
                                
                                if cancel:
                                    st.session_state.pop(f"rename_db_{db}")
                                    st.rerun()
            
            with col2:
                st.subheader("批量操作")
                
                # 备份所有数据库
                if st.button("备份所有数据库", key="backup_all"):
                    with st.spinner("创建备份中..."):
                        try:
                            backup_dir = os.path.join(os.path.dirname(DEFAULT_DB_PATH), "backups")
                            os.makedirs(backup_dir, exist_ok=True)
                            
                            # 创建备份文件名（使用时间戳）
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            backup_file = os.path.join(backup_dir, f"vectordb_backup_{timestamp}.zip")
                            
                            # 创建ZIP文件
                            with st.progress(0) as progress:
                                # 计算要处理的目录总数
                                total_dbs = len(existing_dbs)
                                
                                with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                    for i, db in enumerate(existing_dbs):
                                        db_path = os.path.join(DEFAULT_DB_PATH, db)
                                        
                                        # 更新进度
                                        progress.progress((i) / total_dbs)
                                        
                                        # 递归添加所有文件
                                        for root, _, files in os.walk(db_path):
                                            for file in files:
                                                file_path = os.path.join(root, file)
                                                # 获取相对路径
                                                rel_path = os.path.relpath(file_path, DEFAULT_DB_PATH)
                                                zipf.write(file_path, rel_path)
                                        
                                progress.progress(1.0)
                            
                            st.success(f"✅ 备份已创建: {backup_file}")
                            
                            # 提供下载链接
                            with open(backup_file, "rb") as f:
                                st.download_button(
                                    label="下载备份文件",
                                    data=f.read(),
                                    file_name=f"vectordb_backup_{timestamp}.zip",
                                    mime="application/zip"
                                )
                            
                        except Exception as e:
                            st.error(f"❌ 创建备份失败: {str(e)}")
                
                # 上传备份
                st.subheader("恢复备份")
                uploaded_backup = st.file_uploader("上传备份文件", type=["zip"], help="上传之前导出的ZIP备份文件")
                
                if uploaded_backup:
                    if st.button("恢复备份", key="restore_backup"):
                        with st.spinner("恢复备份中..."):
                            try:
                                # 保存上传的备份文件
                                backup_path = os.path.join(TEMP_DIR, uploaded_backup.name)
                                
                                with open(backup_path, "wb") as f:
                                    f.write(uploaded_backup.getbuffer())
                                
                                # 解压缩
                                with zipfile.ZipFile(backup_path, 'r') as zipf:
                                    # 获取ZIP文件中的所有数据库名称
                                    all_items = zipf.namelist()
                                    db_names = set()
                                    
                                    for item in all_items:
                                        parts = item.split('/')
                                        if len(parts) > 0:
                                            db_names.add(parts[0])
                                    
                                    # 询问要恢复的数据库
                                    if db_names:
                                        for db in db_names:
                                            with st.expander(f"恢复数据库: {db}"):
                                                restore_mode = st.radio(
                                                    "恢复模式",
                                                    ["覆盖现有数据库", "创建新数据库"],
                                                    key=f"restore_mode_{db}"
                                                )
                                                
                                                new_name = db
                                                if restore_mode == "创建新数据库":
                                                    new_name = st.text_input("新数据库名称", 
                                                                       value=f"{db}_restored",
                                                                       key=f"new_name_{db}")
                                                
                                                if st.button("恢复此数据库", key=f"restore_db_{db}"):
                                                    target_path = os.path.join(DEFAULT_DB_PATH, new_name)
                                                    
                                                    # 检查目标路径
                                                    if os.path.exists(target_path) and restore_mode == "覆盖现有数据库":
                                                        shutil.rmtree(target_path)
                                                    
                                                    os.makedirs(target_path, exist_ok=True)
                                                    
                                                    # 解压此数据库的文件
                                                    for item in all_items:
                                                        if item.startswith(f"{db}/"):
                                                            # 修改路径以适应新的数据库名称
                                                            if restore_mode == "创建新数据库":
                                                                new_item = item.replace(f"{db}/", f"{new_name}/", 1)
                                                                extract_path = os.path.join(DEFAULT_DB_PATH, new_item)
                                                            else:
                                                                extract_path = os.path.join(DEFAULT_DB_PATH, item)
                                                            
                                                            # 确保目标目录存在
                                                            os.makedirs(os.path.dirname(extract_path), exist_ok=True)
                                                            
                                                            # 解压文件
                                                            with zipf.open(item) as source, open(extract_path, 'wb') as target:
                                                                shutil.copyfileobj(source, target)
                                                    
                                                    st.success(f"✅ 数据库 '{db}' 已恢复为 '{new_name}'")
                                    else:
                                        st.error("❌ 备份文件中未找到有效的数据库")
                                
                                # 删除临时备份文件
                                os.remove(backup_path)
                                
                            except Exception as e:
                                st.error(f"❌ 恢复备份失败: {str(e)}")
                                # 清理临时文件
                                if os.path.exists(backup_path):
                                    os.remove(backup_path)

if __name__ == "__main__":
    main() 