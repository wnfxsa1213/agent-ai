import os
import sys
import subprocess

@tool
def launch_vector_db_ui():
    """启动向量数据库管理界面，提供图形化操作向量数据库的功能"""
    ui_launcher_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_launcher.py")
    
    subprocess.Popen([sys.executable, ui_launcher_path])
    
    return "向量数据库管理界面已启动，请在浏览器中访问 http://localhost:8501"

# 在帮助信息中添加新功能
def print_help():
    # ... existing code ...
    print("  启动向量数据库UI    - 启动图形化向量数据库管理界面")
    # ... existing code ...

# ... existing code ... 