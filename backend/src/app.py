"""
主应用文件 - 整合MVC架构的FastAPI应用
"""
import sys
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(PROJECT_ROOT)

# 初始化日志系统
from .utils.logger_config import setup_logger
logger = setup_logger()

from .routers.game_router import game_router
from .routers.debug_router import debug_router
from .routers.llm_router import llm_router
from .routers.story_router import story_router
from .controllers.auth_controller import router as auth_router
from .routers.story_db_router import router as story_db_router
from .routers.location_db_router import router as location_db_router
from .routers.npc_db_router import router as npc_db_router

# 数据库初始化
from .database.init_db import init_database


def create_app() -> FastAPI:
    """
    创建FastAPI应用
    
    Returns:
        FastAPI应用实例
    """
    logger.info("🚀 开始创建FastAPI应用")
    
    app = FastAPI(
        title="LLM文字游戏 (MVC架构版本)",
        description="基于新架构的LLM驱动文字游戏，采用MVC三层架构",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 应用启动事件：初始化数据库
    @app.on_event("startup")
    async def startup_event():
        """应用启动时的初始化任务"""
        logger.info("🚀 应用启动事件开始...")
        
        # 初始化数据库
        logger.info("📊 初始化数据库...")
        try:
            success = init_database(drop_existing=False)
            if success:
                logger.info("✅ 数据库初始化成功")
            else:
                logger.error("❌ 数据库初始化失败，但应用将继续运行")
        except Exception as e:
            logger.error(f"❌ 数据库初始化异常: {e}")
            logger.warning("⚠️ 应用将在没有数据库的情况下运行")
        
        # 创建管理员用户（必须在数据迁移之前）
        logger.info("👤 创建管理员用户...")
        try:
            from .services.auth_service import auth_service
            auth_service.create_admin_user()
            logger.info("✅ 管理员用户创建成功")
        except Exception as e:
            logger.error(f"❌ 创建管理员用户失败: {e}")
        
        # 运行数据迁移（需要管理员用户存在）
        logger.info("🔄 运行数据迁移...")
        try:
            from .database.migrations import run_migrations
            story_id = run_migrations()
            if story_id:
                logger.info(f"✅ 数据迁移成功，默认故事ID: {story_id}")
            else:
                logger.warning("⚠️ 数据迁移失败，但应用将继续运行")
        except Exception as migration_error:
            logger.error(f"❌ 数据迁移异常: {migration_error}")
            logger.warning("⚠️ 应用将继续运行")
        
        logger.info("✅ 应用启动事件完成")
    
    # 应用关闭事件
    @app.on_event("shutdown")
    async def shutdown_event():
        """应用关闭时的清理任务"""
        logger.info("👋 应用正在关闭...")
        # 这里可以添加数据库连接池关闭等清理操作
        logger.info("✅ 应用关闭事件完成")
    
    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 请求日志中间件
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # 记录请求开始
        logger.info(f"📨 [HTTP] {request.method} {request.url.path} - 开始处理")
        
        # 处理请求
        response = await call_next(request)
        
        # 计算耗时
        duration = time.time() - start_time
        
        # 记录请求完成
        logger.info(f"📨 [HTTP] {request.method} {request.url.path} - 状态码: {response.status_code}, 耗时: {duration:.3f}s")
        
        return response
    
    # 异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"❌ [GlobalException] {request.method} {request.url.path} - 异常: {str(exc)}", exc_info=True)
        
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
    logger.info("🔗 注册路由...")
    app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
    app.include_router(game_router)
    app.include_router(debug_router)
    app.include_router(llm_router)
    app.include_router(story_router)
    
    # 数据库相关路由
    app.include_router(story_db_router)
    app.include_router(location_db_router)
    app.include_router(npc_db_router)
    
    logger.info("✅ 路由注册完成")
    
    # 根端点
    @app.get("/")
    async def root():
        return {
            "message": "LLM文字游戏 - MVC架构版本",
            "version": "2.0.0",
            "status": "运行中",
            "architecture": "MVC三层架构",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "2.0.0"
        }
    
    # 数据库状态检查端点
    @app.get("/db-status")
    async def database_status():
        """检查数据库连接状态"""
        try:
            from .database.config import test_connection
            is_connected = test_connection()
            return {
                "database_connected": is_connected,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "database_connected": False,
                "error": str(e),
                "timestamp": time.time()
        }
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🎮 LLM文字游戏 - MVC架构版本")
    print("=" * 60)
    print("🚀 正在启动游戏服务器...")
    print("")
    print("📊 架构信息:")
    print("  - 架构模式: MVC三层架构")
    print("  - 工作流引擎: 新架构 (无LangGraph)")
    print("  - API框架: FastAPI")
    print("  - 数据库: PostgreSQL")
    print("  - 版本: 2.0.0")
    print("")
    print("🌐 服务地址:")
    print("  - 游戏API: http://localhost:8001")
    print("  - 接口文档: http://localhost:8001/docs")
    print("  - 数据库状态: http://localhost:8001/db-status")
    print("  - 前端地址: http://localhost:5173")
    print("")
    print("📝 主要特性:")
    print("  ✅ 清晰的MVC分层架构")
    print("  ✅ PostgreSQL数据库持久化")
    print("  ✅ 自动数据库表结构同步")
    print("  ✅ 统一的错误处理")
    print("  ✅ 完整的日志系统")
    print("  ✅ 标准化的响应格式")
    print("  ✅ 数据验证和安全")
    print("")
    print("=" * 60)
    
    # 启动服务器
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8001,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 游戏服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}") 