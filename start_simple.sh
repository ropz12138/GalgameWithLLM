#!/bin/bash
# 简化启动脚本 - 避免复杂的环境检查

set -e

cd "$(dirname "$0")"

echo "============================================================"
echo "🎮 LLM文字游戏 - 简化启动脚本 v2.1.0"
echo "============================================================"

# 后端启动
echo ""
echo "🚀 启动后端服务..."
echo "============================================================"

cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装后端依赖
echo "📦 安装后端依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 测试数据库连接
echo "🧪 测试数据库连接..."
python test_db_fix.py

# 启动后端服务器
echo "🚀 启动后端服务器..."
nohup python start_server.py > ../backend_simple.log 2>&1 &
BACKEND_PID=$!

cd ..

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 8

# 检查后端是否启动成功
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ 后端服务启动成功"
else
    echo "❌ 后端服务启动失败，请检查日志: tail -f backend_simple.log"
    exit 1
fi

# 前端启动
echo ""
echo "🎨 启动前端服务..."
echo "============================================================"

cd frontend

# 安装前端依赖
echo "📦 安装前端依赖..."
npm install

# 创建环境配置文件
echo "⚙️ 配置前端环境..."
cat > .env.local << EOF
VITE_API_URL=http://localhost:8001
VITE_APP_TITLE=LLM文字游戏
VITE_APP_VERSION=2.1.0
EOF

# 启动前端开发服务器
echo "🚀 启动前端开发服务器..."
npm run dev &
FRONTEND_PID=$!

cd ..

# 等待前端启动
echo "⏳ 等待前端服务启动..."
sleep 5

echo ""
echo "============================================================"
echo "🎉 系统启动完成！"
echo "============================================================"
echo ""
echo "📊 服务信息:"
echo "  🖥️  后端API:     http://localhost:8001"
echo "  🎨  前端地址:    http://localhost:5173"
echo "  📚  API文档:     http://localhost:8001/docs"
echo "  🏥  健康检查:    http://localhost:8001/health"
echo ""
echo "🔐 认证端点:"
echo "  📝  用户注册:    POST http://localhost:8001/auth/register"
echo "  🔑  用户登录:    POST http://localhost:8001/auth/login"
echo "  👤  用户信息:    GET  http://localhost:8001/auth/me"
echo ""
echo "🎮 游戏端点:"
echo "  🎯  游戏API:     http://localhost:8001/api"
echo ""
echo "🧪 测试工具:"
echo "  🧪  数据库测试:  python backend/test_db_fix.py"
echo "  🧪  认证测试:    python backend/test_auth.py"
echo ""
echo "============================================================"
echo "💡 提示:"
echo "  - 按 Ctrl+C 可停止所有服务"
echo "  - 查看后端日志: tail -f backend_simple.log"
echo "============================================================"

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ 服务已停止'; exit 0" INT

# 保持脚本运行
wait 