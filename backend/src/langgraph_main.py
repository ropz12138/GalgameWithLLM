"""
LangGraph版本的游戏主启动文件
"""
import sys
import os
import asyncio

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.append(PROJECT_ROOT)
sys.path.append(SCRIPT_DIR)

from langgraph_refactor.api_integration import create_langgraph_api_app

# 创建应用实例（模块级别，供uvicorn访问）
app = create_langgraph_api_app()

def main():
    """
    主函数 - 启动LangGraph版本的游戏服务器
    """
    import uvicorn
    
    print("=" * 60)
    print("🎮 LLM文字游戏 - LangGraph重构版本")
    print("=" * 60)
    print("🚀 正在启动游戏服务器...")
    print("")
    print("📊 架构信息:")
    print("  - 工作流引擎: LangGraph")
    print("  - 状态管理: 内置持久化")
    print("  - API框架: FastAPI")
    print("  - 版本: 2.0.0")
    print("")
    print("🌐 服务地址:")
    print("  - 游戏API: http://localhost:8001")
    print("  - 接口文档: http://localhost:8001/docs")
    print("  - 前端地址: http://localhost:5173")
    print("")
    print("📝 主要改进:")
    print("  ✅ 统一的状态管理")
    print("  ✅ 可视化工作流")
    print("  ✅ 更强的错误恢复")
    print("  ✅ 原生流式支持")
    print("  ✅ 人机交互循环")
    print("")
    print("=" * 60)
    
    # 启动服务器
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8001,  # 使用不同端口避免冲突
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 游戏服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")


async def test_workflow():
    """
    测试工作流功能
    """
    from langgraph_refactor.workflow import execute_game_action, get_game_state
    
    print("🧪 测试LangGraph工作流...")
    
    try:
        # 初始化游戏
        print("1. 初始化游戏状态...")
        state = get_game_state("test_session")
        print(f"   初始位置: {state['player_location']}")
        print(f"   初始时间: {state['current_time']}")
        
        # 测试移动
        print("\n2. 测试移动功能...")
        result = await execute_game_action("去主摄影棚", "test_session")
        if result["success"]:
            print("   ✅ 移动成功")
            for msg in result["messages"]:
                print(f"   📝 {msg['speaker']}: {msg['message']}")
        else:
            print(f"   ❌ 移动失败: {result.get('error')}")
        
        # 测试对话
        print("\n3. 测试对话功能...")
        result = await execute_game_action("和林若曦说：你好", "test_session")
        if result["success"]:
            print("   ✅ 对话成功")
            for msg in result["messages"]:
                print(f"   💬 {msg['speaker']}: {msg['message']}")
        else:
            print(f"   ❌ 对话失败: {result.get('error')}")
        
        # 测试探索
        print("\n4. 测试探索功能...")
        result = await execute_game_action("四处看看", "test_session")
        if result["success"]:
            print("   ✅ 探索成功")
            for msg in result["messages"]:
                print(f"   🔍 {msg['speaker']}: {msg['message']}")
        else:
            print(f"   ❌ 探索失败: {result.get('error')}")
        
        # 获取最终状态
        print("\n5. 最终游戏状态:")
        final_state = get_game_state("test_session")
        print(f"   位置: {final_state['player_location']}")
        print(f"   时间: {final_state['current_time']}")
        print(f"   消息数量: {len(final_state['messages'])}")
        
        print("\n🎉 工作流测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def create_startup_script():
    """
    创建启动脚本
    """
    script_content = """#!/bin/bash
# LangGraph版本游戏启动脚本

echo "🎮 启动LangGraph版本的LLM文字游戏"
echo "================================"

# 检查依赖
echo "📦 检查依赖..."
python -c "import langgraph; print('✅ LangGraph已安装')" || {
    echo "❌ LangGraph未安装，请先安装依赖"
    echo "pip install langgraph"
    exit 1
}

# 启动后端
echo "🚀 启动后端服务..."
cd backend/src
python langgraph_main.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "🌐 启动前端服务..."
cd ../../frontend
pnpm run dev &
FRONTEND_PID=$!

echo "✅ 启动完成"
echo "📍 游戏地址: http://localhost:5173"
echo "📍 API地址: http://localhost:8001"

# 等待用户中断
wait

# 清理进程
echo "🛑 停止服务..."
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null
echo "👋 游戏已停止"
"""
    
    script_path = os.path.join(PROJECT_ROOT, "start_langgraph_game.sh")
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(script_path, 0o755)
        
        print(f"✅ 启动脚本已创建: {script_path}")
        print("💡 使用方法: ./start_langgraph_game.sh")
        
    except Exception as e:
        print(f"❌ 创建启动脚本失败: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LangGraph版本的LLM文字游戏")
    parser.add_argument("--test", action="store_true", help="运行工作流测试")
    parser.add_argument("--create-script", action="store_true", help="创建启动脚本")
    
    args = parser.parse_args()
    
    if args.test:
        # 运行测试
        asyncio.run(test_workflow())
    elif args.create_script:
        # 创建启动脚本
        create_startup_script()
    else:
        # 启动服务器
        main() 