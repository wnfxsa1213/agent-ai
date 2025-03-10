"""
智能体启动器 - 统一入口点，运行不同的智能体示例
"""

import os
import sys
import argparse
import subprocess
import webbrowser
from time import sleep

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能体框架示例启动器")
    parser.add_argument("--assistant", "-a", type=str, default="writing",
                       choices=["writing", "enhanced", "custom", "vectordb", "all"],
                       help="选择要启动的智能体类型")
    parser.add_argument("--model", "-m", type=str, default=None,
                       help="指定使用的模型，覆盖配置文件设置")
    parser.add_argument("--config", "-c", type=str, default=None,
                       help="指定配置文件路径")
    parser.add_argument("--port", "-p", type=int, default=8501,
                       help="指定向量数据库UI的端口号")
    parser.add_argument("--no-browser", "-nb", action="store_true",
                       help="不自动打开浏览器")
    
    args = parser.parse_args()
    
    # 根据选择启动相应的智能体
    if args.assistant in ["writing", "all"]:
        print("启动基础写作助手...")
        if args.assistant == "all":
            # 以独立进程启动
            subprocess.Popen([sys.executable, "-m", "agent_framework.examples.writing_assistant"])
        else:
            from agent_framework.examples.writing_assistant import main as writing_main
            writing_main()
    
    if args.assistant in ["enhanced", "all"]:
        print("启动增强版写作助手...")
        if args.assistant == "all":
            # 以独立进程启动
            subprocess.Popen([sys.executable, "-m", "agent_framework.examples.enhanced_writing_assistant"])
        else:
            from agent_framework.examples.enhanced_writing_assistant import main as enhanced_main
            enhanced_main()
    
    if args.assistant in ["vectordb", "all"]:
        print(f"启动向量数据库管理界面，端口: {args.port}...")
        # 启动向量数据库UI
        launch_vectordb_ui(args.port, args.no_browser)
    
    if args.assistant == "custom":
        print("启动自定义智能体...")
        # 这里可以添加自定义智能体的启动代码
        from agent_framework import Agent, tool
        
        @tool(name="hello", description="打招呼")
        def hello(name: str = "世界") -> str:
            """向指定对象打招呼"""
            return f"你好，{name}！"
        
        agent = Agent(
            name="自定义助手",
            description="一个简单的自定义助手示例",
            model=args.model,
            config_path=args.config,
            tools=[hello.tool]
        )
        
        print("\n" + "="*50)
        print("自定义助手已启动。输入'exit'退出。")
        print("="*50)
        
        while True:
            user_input = input("\n> ")
            if user_input.lower() in ["exit", "quit", "退出"]:
                break
            try:
                response = agent.run(user_input)
                print(f"\n{response}")
            except Exception as e:
                print(f"\n错误: {e}")

def launch_vectordb_ui(port=8501, no_browser=False):
    """启动向量数据库管理界面"""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ui_script = os.path.join(script_dir, "ui", "vector_db_ui.py")
    
    if not os.path.exists(ui_script):
        print(f"错误: 未找到UI脚本: {ui_script}")
        return
    
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
            return
    
    # 启动Streamlit服务
    cmd = [
        sys.executable, "-m", "streamlit", "run", ui_script,
        "--server.port", str(port),
        "--browser.serverAddress", "localhost",
        "--theme.base", "light"
    ]
    
    # 在新的进程中启动Streamlit
    process = subprocess.Popen(cmd)
    
    # 等待服务启动
    print("正在启动服务...")
    sleep(3)
    
    # 打开浏览器
    if not no_browser:
        url = f"http://localhost:{port}"
        webbrowser.open(url)
        print(f"已在浏览器中打开界面: {url}")
    
    if os.environ.get("ASSISTANT_LAUNCHER_ALL_MODE") != "1":
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

def print_launcher_help():
    """打印启动器帮助信息"""
    print("\n" + "="*70)
    print("智能体框架启动器 - 使用指南".center(68))
    print("="*70)
    print("\n可用的智能体类型:")
    print("  writing   - 基础写作助手（支持各种文章类型的写作）")
    print("  enhanced  - 增强版写作助手（集成了向量数据库的写作工具）")
    print("  vectordb  - 向量数据库管理界面（用于管理参考资料数据库）")
    print("  custom    - 自定义智能体（简单示例）")
    print("  all       - 同时启动所有智能体")
    
    print("\n常用选项:")
    print("  --model, -m    指定使用的模型（如gpt-4o, claude-3-opus等）")
    print("  --config, -c   指定配置文件路径")
    print("  --port, -p     指定向量数据库UI的端口号（默认8501）")
    print("  --no-browser   不自动打开浏览器")
    
    print("\n使用示例:")
    print("  python assistant_launcher.py -a writing        # 启动基础写作助手")
    print("  python assistant_launcher.py -a enhanced       # 启动增强版写作助手")
    print("  python assistant_launcher.py -a vectordb -p 8502  # 在8502端口启动向量数据库UI")
    print("  python assistant_launcher.py -a all            # 启动所有智能体")
    print("="*70 + "\n")

if __name__ == "__main__":
    # 首先检查是否有参数，如果没有，显示帮助信息
    if len(sys.argv) == 1:
        print_launcher_help()
        choice = input("请选择要启动的智能体类型 [writing/enhanced/vectordb/custom/all]: ").strip().lower()
        if choice in ["writing", "enhanced", "vectordb", "custom", "all"]:
            sys.argv.extend(["--assistant", choice])
            if choice == "all":
                # 设置环境变量标记，防止在all模式下阻塞
                os.environ["ASSISTANT_LAUNCHER_ALL_MODE"] = "1"
        else:
            print("无效的选择，默认启动基础写作助手")
            sys.argv.extend(["--assistant", "writing"])
    
    main() 