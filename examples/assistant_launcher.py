"""
智能体启动器 - 统一入口点，运行不同的智能体示例
"""

import os
import sys
import argparse

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能体框架示例启动器")
    parser.add_argument("--assistant", "-a", type=str, default="writing",
                       choices=["writing", "enhanced", "custom"],
                       help="选择要启动的智能体类型")
    parser.add_argument("--model", "-m", type=str, default=None,
                       help="指定使用的模型，覆盖配置文件设置")
    parser.add_argument("--config", "-c", type=str, default=None,
                       help="指定配置文件路径")
    
    args = parser.parse_args()
    
    if args.assistant == "writing":
        print("启动基础写作助手...")
        from agent_framework.examples.writing_assistant import main as writing_main
        writing_main()
    elif args.assistant == "enhanced":
        print("启动增强版写作助手...")
        from agent_framework.examples.enhanced_writing_assistant import main as enhanced_main
        enhanced_main()
    elif args.assistant == "custom":
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
    
if __name__ == "__main__":
    main() 