#!/usr/bin/env python3
"""
向量数据库管理界面启动脚本
"""

import os
import sys
import argparse
import subprocess
import webbrowser
from time import sleep

def main():
    """主函数：解析参数并启动UI"""
    parser = argparse.ArgumentParser(description="启动向量数据库管理界面")
    parser.add_argument("--port", type=int, default=8501, help="Streamlit服务端口号")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    args = parser.parse_args()
    
    # 确定UI脚本路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ui_script = os.path.join(script_dir, "ui", "vector_db_ui.py")
    
    if not os.path.exists(ui_script):
        print(f"错误: 未找到UI脚本: {ui_script}")
        sys.exit(1)
    
    # 检查Streamlit是否安装
    try:
        import streamlit
        print("已检测到Streamlit库")
    except ImportError:
        print("未检测到Streamlit库，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
            print("Streamlit安装成功")
        except subprocess.CalledProcessError:
            print("错误: 安装Streamlit失败")
            sys.exit(1)
    
    # 启动Streamlit服务
    cmd = [
        sys.executable, "-m", "streamlit", "run", ui_script,
        "--server.port", str(args.port),
        "--browser.serverAddress", "localhost",
        "--server.headless", "true",  # 禁用Streamlit自动打开浏览器
        "--theme.base", "light"
    ]
    
    print(f"启动向量数据库管理界面，端口: {args.port}")
    
    # 在新的进程中启动Streamlit
    process = subprocess.Popen(cmd)
    
    # 等待服务启动
    print("正在启动服务...")
    sleep(3)
    
    # 打开浏览器
    if not args.no_browser:
        url = f"http://localhost:{args.port}"
        webbrowser.open(url)
        print(f"已在浏览器中打开界面: {url}")
    
    try:
        # 等待用户按Ctrl+C
        print("服务已启动。按Ctrl+C退出。")
        process.wait()
    except KeyboardInterrupt:
        # 捕获Ctrl+C
        print("\n用户终止，正在关闭服务...")
        process.terminate()
        process.wait()
        print("服务已关闭")

if __name__ == "__main__":
    main() 