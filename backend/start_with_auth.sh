#!/bin/bash

# LLM文字游戏 - 带认证功能启动脚本
# 版本: 2.1.0

echo "============================================================"
echo "🎮 LLM文字游戏 - 带认证功能启动脚本 v2.1.0"
echo "============================================================"

# 检查Python环境
echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖包..."
pip install -r requirements.txt

# 检查数据库配置
echo "🗄️ 检查数据库配置..."
if [ ! -f "config/config.json" ]; then
    echo "❌ 配置文件不存在: config/config.json"
    exit 1
fi

# 初始化数据库
echo "🗄️ 初始化数据库..."
python init_database.py

# 启动服务器
echo "🚀 启动游戏服务器..."
echo ""
echo "📊 服务信息:"
echo "  - 后端API: http://localhost:8001"
echo "  - API文档: http://localhost:8001/docs"
echo "  - 健康检查: http://localhost:8001/health"
echo ""
echo "🔐 认证端点:"
echo "  - 注册: POST http://localhost:8001/auth/register"
echo "  - 登录: POST http://localhost:8001/auth/login"
echo "  - 用户信息: GET http://localhost:8001/auth/me"
echo ""
echo "🎮 游戏端点:"
echo "  - 游戏API: http://localhost:8001/api"
echo ""
echo "============================================================"

# 启动应用
python src/app.py 