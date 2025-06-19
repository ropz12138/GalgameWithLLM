#!/usr/bin/env python3
"""
MVC架构版本的游戏启动脚本
"""
import sys
import os
import uvicorn

# 添加src目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(SCRIPT_DIR, "src")
sys.path.append(SRC_DIR)


def main():
    """
    主函数 - 启动MVC架构版本的游戏服务器
    """
    print("=" * 60)
    print("🎮 LLM文字游戏 - MVC架构版本")
    print("=" * 60)
    print("🚀 正在启动游戏服务器...")
    print("")
    print("📊 架构信息:")
    print("  - 架构模式: MVC三层架构")
    print("  - 工作流引擎: LangGraph")
    print("  - API框架: FastAPI")
    print("  - 版本: 2.0.0")
    print("")
    print("🌐 服务地址:")
    print("  - 游戏API: http://localhost:8001")
    print("  - 接口文档: http://localhost:8001/docs")
    print("  - 前端地址: http://localhost:5173")
    print("")
    print("📝 主要特性:")
    print("  ✅ 清晰的MVC分层架构")
    print("  ✅ 统一的错误处理")
    print("  ✅ 完整的日志系统")
    print("  ✅ 标准化的响应格式")
    print("  ✅ 数据验证和安全")
    print("")
    print("=" * 60)
    
    # 启动服务器
    try:
        uvicorn.run(
            "app:app",  # 使用导入字符串
            host="0.0.0.0", 
            port=8001,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 游戏服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")


if __name__ == "__main__":
    main() 