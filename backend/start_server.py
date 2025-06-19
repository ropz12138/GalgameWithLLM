#!/usr/bin/env python3
"""
服务器启动脚本
专门用于启动FastAPI服务器
"""
import sys
import os
import uvicorn

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, "src"))

from utils.database import init_db, check_database_connection


def main():
    """主启动函数"""
    print("=" * 60)
    print("🎮 LLM文字游戏 - 服务器启动脚本 v2.1.0")
    print("=" * 60)
    
    # 检查数据库连接
    print("🔍 检查数据库连接...")
    if not check_database_connection():
        print("❌ 数据库连接失败")
        return
    
    # 初始化数据库
    print("🗄️ 初始化数据库...")
    init_db()
    
    print("🚀 启动FastAPI服务器...")
    print("📊 服务信息:")
    print("  - 地址: http://localhost:8001")
    print("  - 文档: http://localhost:8001/docs")
    print("  - 健康检查: http://localhost:8001/health")
    print("=" * 60)
    
    # 启动服务器
    try:
        uvicorn.run(
            "src.app:app",  # 使用导入字符串
            host="0.0.0.0",
            port=8001,
            reload=True,  # 启用reload
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")


if __name__ == "__main__":
    main() 