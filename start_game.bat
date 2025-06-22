@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 🎮 LLM文字游戏一键启动脚本 (Windows版本)
REM 自动启动后端和前端服务

REM 配置
set CONDA_ENV=llm_text_game_env
set BACKEND_PORT=8001
set FRONTEND_PORT=5173

echo ================================================================
echo 🎮 LLM文字游戏 - 一键启动脚本 (Windows版本)
echo ================================================================
echo.

REM 检查conda是否安装
conda --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到conda命令，请确保已安装Anaconda/Miniconda
    pause
    exit /b 1
)

REM 检查conda环境是否存在
conda env list | findstr /C:"%CONDA_ENV%" >nul
if errorlevel 1 (
    echo ❌ 错误: 未找到conda环境 '%CONDA_ENV%'
    echo 请先创建conda环境:
    echo conda create -n %CONDA_ENV% python=3.10
    echo conda activate %CONDA_ENV%
    echo pip install -r backend/requirements.txt
    pause
    exit /b 1
)

REM 检查必要的目录
if not exist "backend" (
    echo ❌ 错误: 未找到backend目录
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ 错误: 未找到frontend目录
    pause
    exit /b 1
)

REM 创建日志目录
if not exist "logs" mkdir logs

REM 启动后端服务
echo.
echo 🚀 启动后端服务...
echo   - 环境: %CONDA_ENV%
echo   - 端口: %BACKEND_PORT%
echo   - 日志: logs\backend.log

REM 在新窗口中启动后端
start "后端服务" /min cmd /c "cd backend && conda activate %CONDA_ENV% && echo %date% %time%: 启动后端服务 >> ..\logs\backend.log && python -m uvicorn src.app:app --host 0.0.0.0 --port %BACKEND_PORT% --reload >> ..\logs\backend.log 2>&1"

REM 等待后端启动
echo ⏳ 等待后端服务启动...
timeout /t 8 /nobreak >nul

REM 检查后端是否启动成功
curl -s http://localhost:%BACKEND_PORT%/health >nul 2>&1
if errorlevel 1 (
    echo ❌ 后端服务启动失败，请检查日志: logs\backend.log
    pause
    exit /b 1
) else (
    echo ✅ 后端服务启动成功
)

REM 检查前端依赖
echo.
echo 🔍 检查前端依赖...
if not exist "frontend\node_modules" (
    echo ⚠️  未找到node_modules，正在安装依赖...
    cd frontend
    where pnpm >nul 2>&1
    if not errorlevel 1 (
        pnpm install
    ) else (
        where yarn >nul 2>&1
        if not errorlevel 1 (
            yarn install
        ) else (
            npm install
        )
    )
    cd ..
)

REM 启动前端服务
echo.
echo 🚀 启动前端服务...
echo   - 端口: %FRONTEND_PORT%
echo   - 日志: logs\frontend.log

REM 在新窗口中启动前端
cd frontend
where pnpm >nul 2>&1
if not errorlevel 1 (
    start "前端服务" /min cmd /c "echo %date% %time%: 启动前端服务 >> ..\logs\frontend.log && pnpm dev --port %FRONTEND_PORT% >> ..\logs\frontend.log 2>&1"
) else (
    where yarn >nul 2>&1
    if not errorlevel 1 (
        start "前端服务" /min cmd /c "echo %date% %time%: 启动前端服务 >> ..\logs\frontend.log && yarn dev --port %FRONTEND_PORT% >> ..\logs\frontend.log 2>&1"
    ) else (
        start "前端服务" /min cmd /c "echo %date% %time%: 启动前端服务 >> ..\logs\frontend.log && npm run dev -- --port %FRONTEND_PORT% >> ..\logs\frontend.log 2>&1"
    )
)
cd ..

REM 等待前端启动
echo ⏳ 等待前端服务启动...
timeout /t 10 /nobreak >nul

REM 检查前端是否启动成功
curl -s http://localhost:%FRONTEND_PORT% >nul 2>&1
if errorlevel 1 (
    echo ⚠️  前端服务可能仍在启动中...
) else (
    echo ✅ 前端服务启动成功
)

REM 显示启动完成信息
echo.
echo ================================================================
echo 🎉 游戏服务启动完成！
echo ================================================================
echo.
echo 📱 服务地址:
echo   🎮 游戏前端: http://localhost:%FRONTEND_PORT%
echo   🔧 后端API: http://localhost:%BACKEND_PORT%
echo   📚 API文档: http://localhost:%BACKEND_PORT%/docs
echo.
echo 📝 日志文件:
echo   后端日志: logs\backend.log
echo   前端日志: logs\frontend.log
echo.
echo 💡 使用说明:
echo   - 前端和后端服务在独立窗口中运行
echo   - 关闭对应窗口即可停止服务
echo   - 或运行: stop_game.bat
echo   - 查看日志: type logs\backend.log
echo.

REM 自动打开浏览器
echo 🌐 正在打开游戏页面...
start http://localhost:%FRONTEND_PORT%

echo 🎮 游戏服务已启动，请查看浏览器
pause 