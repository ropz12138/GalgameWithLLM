#!/bin/bash
# 一键启动完整系统（后端+前端+认证功能）

set -e

cd "$(dirname "$0")"

echo "============================================================"
echo "🎮 LLM文字游戏 - 完整系统启动脚本 v2.1.0"
echo "============================================================"

# 检查Python环境
echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查Node.js环境
echo "🔍 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装Node.js"
    exit 1
fi

# 检查npm环境
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装npm"
    exit 1
fi

echo "✅ 环境检查通过"

# 后端启动
echo ""
echo "🚀 启动后端服务..."
echo "============================================================"

# 进入后端目录
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

# 检查数据库配置
echo "🗄️ 检查数据库配置..."
if [ ! -f "config/config.json" ]; then
    echo "❌ 配置文件不存在: config/config.json"
    exit 1
fi

# 初始化数据库
echo "🗄️ 初始化数据库..."
python init_database.py

# 启动后端服务器
echo "🚀 启动后端服务器..."
nohup python src/app.py > ../backend_full.log 2>&1 &
BACKEND_PID=$!

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 检查后端是否启动成功
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ 后端服务启动成功"
else
    echo "❌ 后端服务启动失败"
    exit 1
fi

cd ..

# 前端启动
echo ""
echo "🎨 启动前端服务..."
echo "============================================================"

# 进入前端目录
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
sleep 3

echo ""
echo "============================================================"
echo "🎉 系统启动完成！"
echo "============================================================"
echo ""
echo "📊 服务信息:"
echo "  🖥️  后端API:     http://localhost:8001"
echo "  🎨  前端地址:    http://localhost:5173"
echo "  📚  API文档:     http://localhost:8001/docs"
echo "  📖  ReDoc文档:   http://localhost:8001/redoc"
echo "  🏥  健康检查:    http://localhost:8001/health"
echo ""
echo "🔐 认证端点:"
echo "  📝  用户注册:    POST http://localhost:8001/auth/register"
echo "  🔑  用户登录:    POST http://localhost:8001/auth/login"
echo "  👤  用户信息:    GET  http://localhost:8001/auth/me"
echo ""
echo "🎮 游戏端点:"
echo "  🎯  游戏API:     http://localhost:8001/api"
echo "  🎲  游戏状态:    GET  http://localhost:8001/api/game_state"
echo "  🚀  初始化游戏:  GET  http://localhost:8001/api/initialize_game"
echo ""
echo "📝 主要特性:"
echo "  ✅ 用户认证系统 (JWT)"
echo "  ✅ 密码加密存储 (bcrypt)"
echo "  ✅ 数据库持久化 (PostgreSQL/SQLite)"
echo "  ✅ MVC三层架构"
echo "  ✅ LangGraph工作流"
echo "  ✅ 实时对话系统"
echo "  ✅ 现代化前端界面"
echo ""
echo "🧪 测试工具:"
echo "  🧪  认证测试:    python backend/test_auth.py"
echo "  📋  API示例:     python backend/api_examples.py"
echo ""
echo "============================================================"
echo "💡 提示:"
echo "  - 按 Ctrl+C 可停止所有服务"
echo "  - 查看后端日志: tail -f backend_full.log"
echo "  - 查看前端日志: 前端控制台"
echo "============================================================"

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ 服务已停止'; exit 0" INT

# 保持脚本运行
wait 