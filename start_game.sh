#!/bin/bash

# 🎮 LLM文字游戏一键启动脚本
# 自动启动后端和前端服务

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
CONDA_ENV="llm_text_game_env"
BACKEND_PORT=8001
FRONTEND_PORT=5173

# 打印标题
echo -e "${PURPLE}================================================================${NC}"
echo -e "${PURPLE}🎮 LLM文字游戏 - 一键启动脚本${NC}"
echo -e "${PURPLE}================================================================${NC}"
echo ""

# 检查conda是否安装
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到conda命令，请确保已安装Anaconda/Miniconda${NC}"
    exit 1
fi

# 检查conda环境是否存在
if ! conda env list | grep -q "$CONDA_ENV"; then
    echo -e "${RED}❌ 错误: 未找到conda环境 '$CONDA_ENV'${NC}"
    echo -e "${YELLOW}请先创建conda环境:${NC}"
    echo -e "${CYAN}conda create -n $CONDA_ENV python=3.10${NC}"
    echo -e "${CYAN}conda activate $CONDA_ENV${NC}"
    echo -e "${CYAN}pip install -r backend/requirements.txt${NC}"
    exit 1
fi

# 检查必要的目录
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ 错误: 未找到backend目录${NC}"
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ 错误: 未找到frontend目录${NC}"
    exit 1
fi

# 检查和安装后端依赖
echo -e "${BLUE}🔍 检查后端依赖...${NC}"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $CONDA_ENV

# 检查关键依赖是否已安装
python -c "import fastapi, sqlalchemy, passlib" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  后端依赖不完整，正在安装...${NC}"
    cd backend
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 后端依赖安装失败${NC}"
        exit 1
    fi
    cd ..
    echo -e "${GREEN}✅ 后端依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ 后端依赖已就绪${NC}"
fi

# 检查端口是否被占用
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️  警告: 端口 $port 已被占用 ($service)${NC}"
        echo -e "${YELLOW}是否要终止占用该端口的进程? (y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            lsof -ti:$port | xargs kill -9
            echo -e "${GREEN}✅ 已终止占用端口 $port 的进程${NC}"
        else
            echo -e "${RED}❌ 取消启动${NC}"
            exit 1
        fi
    fi
}

# 检查端口
echo -e "${BLUE}🔍 检查端口占用情况...${NC}"
check_port $BACKEND_PORT "后端服务"
check_port $FRONTEND_PORT "前端服务"

# 创建日志目录
mkdir -p logs

# 启动后端服务
echo ""
echo -e "${BLUE}🚀 启动后端服务...${NC}"
echo -e "${CYAN}  - 环境: $CONDA_ENV${NC}"
echo -e "${CYAN}  - 端口: $BACKEND_PORT${NC}"
echo -e "${CYAN}  - 日志: logs/backend.log${NC}"

# 在后台启动后端
(
    cd backend
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate $CONDA_ENV
    echo "$(date): 启动后端服务" >> ../logs/backend.log
    python -m uvicorn src.app:app --host 0.0.0.0 --port $BACKEND_PORT --reload >> ../logs/backend.log 2>&1
) &
BACKEND_PID=$!

# 等待后端启动
echo -e "${YELLOW}⏳ 等待后端服务启动...${NC}"
sleep 5

# 检查后端是否启动成功
if curl -s http://localhost:$BACKEND_PORT/health > /dev/null; then
    echo -e "${GREEN}✅ 后端服务启动成功${NC}"
else
    echo -e "${RED}❌ 后端服务启动失败，请检查日志: logs/backend.log${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# 检查前端依赖
echo ""
echo -e "${BLUE}🔍 检查前端依赖...${NC}"
if [ ! -d "frontend/node_modules" ] || [ ! -f "frontend/node_modules/react-router-dom/package.json" ]; then
    echo -e "${YELLOW}⚠️  前端依赖不完整，正在安装...${NC}"
    cd frontend
    if command -v pnpm &> /dev/null; then
        pnpm install
    elif command -v yarn &> /dev/null; then
        yarn install
    else
        npm install
    fi
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 前端依赖安装失败${NC}"
        cd ..
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    cd ..
    echo -e "${GREEN}✅ 前端依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ 前端依赖已就绪${NC}"
fi

# 启动前端服务
echo ""
echo -e "${BLUE}🚀 启动前端服务...${NC}"
echo -e "${CYAN}  - 端口: $FRONTEND_PORT${NC}"
echo -e "${CYAN}  - 日志: logs/frontend.log${NC}"

# 在后台启动前端
(
    cd frontend
    echo "$(date): 启动前端服务" >> ../logs/frontend.log
    if command -v pnpm &> /dev/null; then
        pnpm dev --port $FRONTEND_PORT >> ../logs/frontend.log 2>&1
    elif command -v yarn &> /dev/null; then
        yarn dev --port $FRONTEND_PORT >> ../logs/frontend.log 2>&1
    else
        npm run dev -- --port $FRONTEND_PORT >> ../logs/frontend.log 2>&1
    fi
) &
FRONTEND_PID=$!

# 等待前端启动
echo -e "${YELLOW}⏳ 等待前端服务启动...${NC}"
sleep 8

# 检查前端是否启动成功
if curl -s http://localhost:$FRONTEND_PORT > /dev/null; then
    echo -e "${GREEN}✅ 前端服务启动成功${NC}"
else
    echo -e "${YELLOW}⚠️  前端服务可能仍在启动中...${NC}"
fi

# 显示启动完成信息
echo ""
echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}🎉 游戏服务启动完成！${NC}"
echo -e "${GREEN}================================================================${NC}"
echo ""
echo -e "${CYAN}📱 服务地址:${NC}"
echo -e "${CYAN}  🔐 登录页面: http://localhost:$FRONTEND_PORT/login${NC}"
echo -e "${CYAN}  🎮 游戏前端: http://localhost:$FRONTEND_PORT/galgame${NC}"
echo -e "${CYAN}  🔧 后端API: http://localhost:$BACKEND_PORT${NC}"
echo -e "${CYAN}  📚 API文档: http://localhost:$BACKEND_PORT/docs${NC}"
echo ""
echo -e "${CYAN}👤 默认管理员账户:${NC}"
echo -e "${CYAN}  用户名: admin${NC}"
echo -e "${CYAN}  密码: admin123${NC}"
echo ""
echo -e "${CYAN}📊 进程信息:${NC}"
echo -e "${CYAN}  后端PID: $BACKEND_PID${NC}"
echo -e "${CYAN}  前端PID: $FRONTEND_PID${NC}"
echo ""
echo -e "${CYAN}📝 日志文件:${NC}"
echo -e "${CYAN}  后端日志: logs/backend.log${NC}"
echo -e "${CYAN}  前端日志: logs/frontend.log${NC}"
echo ""
echo -e "${YELLOW}💡 使用说明:${NC}"
echo -e "${YELLOW}  - 按 Ctrl+C 停止所有服务${NC}"
echo -e "${YELLOW}  - 或运行: ./stop_game.sh${NC}"
echo -e "${YELLOW}  - 查看日志: tail -f logs/backend.log${NC}"
echo ""

# 保存PID到文件
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# 等待用户中断
trap 'echo -e "\n${YELLOW}🛑 正在停止服务...${NC}"; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; echo -e "${GREEN}✅ 服务已停止${NC}"; exit 0' INT

echo -e "${GREEN}🎮 游戏正在运行，按 Ctrl+C 停止服务${NC}"
wait 