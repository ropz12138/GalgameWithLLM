#!/bin/bash

# 🛑 LLM文字游戏停止脚本
# 停止后端和前端服务

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
BACKEND_PORT=8001
FRONTEND_PORT=5173

echo -e "${PURPLE}================================================================${NC}"
echo -e "${PURPLE}🛑 LLM文字游戏 - 停止服务脚本${NC}"
echo -e "${PURPLE}================================================================${NC}"
echo ""

# 停止通过PID文件记录的进程
stop_by_pid() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}🛑 停止$service_name (PID: $pid)...${NC}"
            kill "$pid" 2>/dev/null
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${YELLOW}⚠️  强制停止$service_name...${NC}"
                kill -9 "$pid" 2>/dev/null
            fi
            echo -e "${GREEN}✅ $service_name已停止${NC}"
        else
            echo -e "${BLUE}ℹ️  $service_name进程已不存在${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "${BLUE}ℹ️  未找到$service_name的PID文件${NC}"
    fi
}

# 停止通过端口查找的进程
stop_by_port() {
    local port=$1
    local service_name=$2
    
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}🛑 停止占用端口$port的$service_name进程...${NC}"
        echo "$pids" | xargs kill 2>/dev/null
        sleep 2
        
        # 检查是否还有进程
        local remaining_pids=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$remaining_pids" ]; then
            echo -e "${YELLOW}⚠️  强制停止占用端口$port的进程...${NC}"
            echo "$remaining_pids" | xargs kill -9 2>/dev/null
        fi
        echo -e "${GREEN}✅ 端口$port上的$service_name已停止${NC}"
    else
        echo -e "${BLUE}ℹ️  端口$port上没有运行的$service_name${NC}"
    fi
}

# 停止后端服务
echo -e "${BLUE}🔍 停止后端服务...${NC}"
stop_by_pid ".backend.pid" "后端服务"
stop_by_port $BACKEND_PORT "后端服务"

# 停止前端服务
echo ""
echo -e "${BLUE}🔍 停止前端服务...${NC}"
stop_by_pid ".frontend.pid" "前端服务"
stop_by_port $FRONTEND_PORT "前端服务"

# 清理临时文件
echo ""
echo -e "${BLUE}🧹 清理临时文件...${NC}"
rm -f .backend.pid .frontend.pid

# 显示完成信息
echo ""
echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}✅ 所有服务已停止${NC}"
echo -e "${GREEN}================================================================${NC}"
echo ""
echo -e "${CYAN}📝 日志文件仍然保留在 logs/ 目录中${NC}"
echo -e "${CYAN}如需查看日志:${NC}"
echo -e "${CYAN}  - 后端日志: tail -f logs/backend.log${NC}"
echo -e "${CYAN}  - 前端日志: tail -f logs/frontend.log${NC}"
echo "" 