@echo off
chcp 65001 >nul

REM 🛑 LLM文字游戏停止脚本 (Windows版本)
REM 停止后端和前端服务

REM 配置
set BACKEND_PORT=8001
set FRONTEND_PORT=5173

echo ================================================================
echo 🛑 LLM文字游戏 - 停止服务脚本 (Windows版本)
echo ================================================================
echo.

REM 停止后端服务
echo 🔍 停止后端服务...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%BACKEND_PORT%') do (
    echo 🛑 停止占用端口%BACKEND_PORT%的进程 (PID: %%a)...
    taskkill /PID %%a /F >nul 2>&1
    if not errorlevel 1 (
        echo ✅ 后端服务已停止
    )
)

REM 停止前端服务
echo.
echo 🔍 停止前端服务...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%FRONTEND_PORT%') do (
    echo 🛑 停止占用端口%FRONTEND_PORT%的进程 (PID: %%a)...
    taskkill /PID %%a /F >nul 2>&1
    if not errorlevel 1 (
        echo ✅ 前端服务已停止
    )
)

REM 停止可能的Python进程
echo.
echo 🔍 停止相关Python进程...
tasklist | findstr python >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2" %%a in ('tasklist ^| findstr python') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    echo ✅ Python进程已停止
)

REM 停止可能的Node进程
echo.
echo 🔍 停止相关Node进程...
tasklist | findstr node >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2" %%a in ('tasklist ^| findstr node') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    echo ✅ Node进程已停止
)

REM 显示完成信息
echo.
echo ================================================================
echo ✅ 所有服务已停止
echo ================================================================
echo.
echo 📝 日志文件仍然保留在 logs\ 目录中
echo 如需查看日志:
echo   - 后端日志: type logs\backend.log
echo   - 前端日志: type logs\frontend.log
echo.
pause 