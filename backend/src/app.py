"""
主应用文件 - 整合MVC架构的FastAPI应用
"""
import sys
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(PROJECT_ROOT)

from routers import game_router, debug_router, llm_router, auth_router
from utils.database import init_db, check_database_connection
# from utils.logger_utils import LoggerUtils


def create_app() -> FastAPI:
    """
    创建FastAPI应用
    
    Returns:
        FastAPI应用实例
    """
    app = FastAPI(
        title="LLM文字游戏 (MVC架构版本)",
        description="基于LangGraph的LLM驱动文字游戏，采用MVC三层架构，支持用户认证",
        version="2.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 请求日志中间件（暂时注释掉）
    # @app.middleware("http")
    # async def log_requests(request: Request, call_next):
    #     start_time = time.time()
    #     
    #     # 处理请求
    #     response = await call_next(request)
    #     
    #     # 计算耗时
    #     duration = time.time() - start_time
    #     
    #     # 记录请求日志
    #     LoggerUtils.log_api_request(
    #         method=request.method,
    #         path=request.url.path,
    #         status_code=response.status_code,
    #         duration=duration
    #     )
    #     
    #     return response
    
    # 异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # 记录错误日志（暂时注释掉）
        # LoggerUtils.log_error(exc, f"全局异常处理 - {request.method} {request.url.path}")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "服务器内部错误",
                "message": str(exc),
                "timestamp": time.time()
            }
        )
    
    # 注册路由
    app.include_router(auth_router)  # 认证路由
    app.include_router(game_router)
    app.include_router(debug_router)
    app.include_router(llm_router)
    
    # 根端点
    @app.get("/")
    async def root():
        return {
            "message": "LLM文字游戏 - MVC架构版本",
            "version": "2.1.0",
            "status": "运行中",
            "architecture": "MVC三层架构",
            "features": [
                "用户认证系统",
                "LangGraph工作流",
                "实时对话",
                "状态管理"
            ],
            "endpoints": {
                "auth": "/auth - 用户认证",
                "game": "/api - 游戏功能",
                "docs": "/docs - API文档"
            }
        }
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        db_status = "healthy" if check_database_connection() else "unhealthy"
        return {
            "status": "healthy",
            "database": db_status,
            "timestamp": time.time(),
            "version": "2.1.0"
        }
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🎮 LLM文字游戏 - MVC架构版本 v2.1.0")
    print("=" * 60)
    print("🚀 正在启动游戏服务器...")
    print("")
    print("📊 架构信息:")
    print("  - 架构模式: MVC三层架构")
    print("  - 工作流引擎: LangGraph")
    print("  - API框架: FastAPI")
    print("  - 数据库: PostgreSQL/SQLite")
    print("  - 认证: JWT")
    print("  - 版本: 2.1.0")
    print("")
    print("🌐 服务地址:")
    print("  - 游戏API: http://localhost:8001")
    print("  - 接口文档: http://localhost:8001/docs")
    print("  - 前端地址: http://localhost:5173")
    print("")
    print("🔐 认证端点:")
    print("  - 注册: POST /auth/register")
    print("  - 登录: POST /auth/login")
    print("  - 用户信息: GET /auth/me")
    print("")
    print("📝 主要特性:")
    print("  ✅ 用户认证系统")
    print("  ✅ 密码加密存储")
    print("  ✅ JWT令牌认证")
    print("  ✅ 数据库持久化")
    print("  ✅ 清晰的MVC分层架构")
    print("  ✅ 统一的错误处理")
    print("  ✅ 完整的日志系统")
    print("  ✅ 标准化的响应格式")
    print("  ✅ 数据验证和安全")
    print("")
    print("=" * 60)
    
    # 初始化数据库
    print("🗄️ 初始化数据库...")
    init_db()
    
    # 启动服务器
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8001,
            reload=False,  # 禁用reload模式避免警告
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 游戏服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}") 