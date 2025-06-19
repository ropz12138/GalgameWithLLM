#!/bin/bash
# 一键启动LangGraph版本后端+前端，并自动切换前端API端口

set -e

cd "$(dirname "$0")"

# Conda环境名称
CONDA_ENV=llm_text_game_env
PYTHON_VERSION=3.10

# 检查conda是否可用
if ! command -v conda &> /dev/null; then
  echo "[错误] 未检测到conda命令，请先安装Miniconda或Anaconda。"
  exit 1
fi

# 检查环境是否存在，不存在则创建
if conda info --envs | grep -q "^$CONDA_ENV"; then
  echo "[环境] 已存在conda环境: $CONDA_ENV"
else
  echo "[环境] 创建新的conda环境: $CONDA_ENV (python=$PYTHON_VERSION)"
  conda create -y -n $CONDA_ENV python=$PYTHON_VERSION
fi

# 激活环境
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $CONDA_ENV

echo "[环境] 已激活conda环境: $CONDA_ENV"

BACKEND_DIR="backend/src/langgraph_refactor"
REQUIREMENTS="$BACKEND_DIR/requirements.txt"

# 安装后端依赖（最新版）
echo "[依赖] 检查并安装后端依赖..."
pip install --upgrade pip
pip install --upgrade -r "$REQUIREMENTS"

echo "[后端] 启动LangGraph后端 (端口8001)..."
cd backend/src
nohup uvicorn langgraph_main:app --host 0.0.0.0 --port 8001 > ../../backend.log 2>&1 &

cd ../../

# 自动检测前端目录
if [ -d "react_repo" ]; then
  FRONTEND_DIR="react_repo"
elif [ -d "frontend" ]; then
  FRONTEND_DIR="frontend"
else
  echo "未找到前端目录（react_repo 或 frontend），请检查！"
  exit 1
fi

# 自动切换前端API地址
if [ -f "$FRONTEND_DIR/.env.local" ]; then
  sed -i '' 's|VITE_API_URL=.*|VITE_API_URL=http://localhost:8001|' "$FRONTEND_DIR/.env.local"
  echo "[前端] API地址已切换为 http://localhost:8001 (文件: $FRONTEND_DIR/.env.local)"
fi

echo "[前端] 使用npm启动..."
cd "$FRONTEND_DIR"
npm install
npm run dev &

cd ..

echo "========================================="
echo "🎮 LLM文字游戏 - LangGraph一键启动"
echo "-----------------------------------------"
echo "后端API:   http://localhost:8001"
echo "前端地址:   http://localhost:5173"
echo "API文档:    http://localhost:8001/docs"
echo "========================================="
echo "按 Ctrl+C 可关闭所有服务"
echo "========================================="

wait 