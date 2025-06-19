"""
日志工具类 - 提供统一的日志记录功能
"""
import logging
import sys
import os
from datetime import datetime
from typing import Optional


class LoggerUtils:
    """日志工具类"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str = "galgame", level: int = logging.INFO) -> logging.Logger:
        """
        获取日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别
            
        Returns:
            日志记录器
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 避免重复添加处理器
        if not logger.handlers:
            # 创建控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            
            # 创建文件处理器（确保目录存在）
            try:
                # 确保日志目录存在
                log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
                os.makedirs(log_dir, exist_ok=True)
                
                log_file = os.path.join(log_dir, f"{name}.log")
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(level)
            except Exception as e:
                print(f"警告：无法创建日志文件 {name}.log: {e}")
                file_handler = None
            
            # 创建格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            console_handler.setFormatter(formatter)
            if file_handler:
                file_handler.setFormatter(formatter)
            
            # 添加处理器
            logger.addHandler(console_handler)
            if file_handler:
                logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def log_game_action(cls, session_id: str, action: str, result: dict, logger_name: str = "game"):
        """
        记录游戏行动日志
        
        Args:
            session_id: 会话ID
            action: 玩家行动
            result: 执行结果
            logger_name: 日志记录器名称
        """
        try:
            logger = cls.get_logger(logger_name)
            
            success = result.get("success", False)
            status = "成功" if success else "失败"
            error = result.get("error", "")
            
            log_message = f"[{session_id}] 行动: {action} | 状态: {status}"
            if error:
                log_message += f" | 错误: {error}"
            
            if success:
                logger.info(log_message)
            else:
                logger.error(log_message)
        except Exception as e:
            print(f"记录游戏行动日志失败: {e}")
    
    @classmethod
    def log_llm_request(cls, model_name: str, prompt: str, response: str, duration: float, logger_name: str = "llm"):
        """
        记录LLM请求日志
        
        Args:
            model_name: 模型名称
            prompt: 提示词
            response: 响应内容
            duration: 请求耗时
            logger_name: 日志记录器名称
        """
        try:
            logger = cls.get_logger(logger_name)
            
            # 截断过长的内容
            prompt_preview = prompt[:100] + "..." if len(prompt) > 100 else prompt
            response_preview = response[:100] + "..." if len(response) > 100 else response
            
            log_message = f"[{model_name}] 耗时: {duration:.2f}s | 提示词: {prompt_preview} | 响应: {response_preview}"
            logger.info(log_message)
        except Exception as e:
            print(f"记录LLM请求日志失败: {e}")
    
    @classmethod
    def log_error(cls, error: Exception, context: str = "", logger_name: str = "error"):
        """
        记录错误日志
        
        Args:
            error: 异常对象
            context: 错误上下文
            logger_name: 日志记录器名称
        """
        try:
            logger = cls.get_logger(logger_name)
            
            log_message = f"错误: {str(error)}"
            if context:
                log_message = f"[{context}] {log_message}"
            
            logger.error(log_message, exc_info=True)
        except Exception as e:
            print(f"记录错误日志失败: {e}")
    
    @classmethod
    def log_performance(cls, operation: str, duration: float, details: Optional[dict] = None, logger_name: str = "performance"):
        """
        记录性能日志
        
        Args:
            operation: 操作名称
            duration: 耗时
            details: 详细信息
            logger_name: 日志记录器名称
        """
        try:
            logger = cls.get_logger(logger_name)
            
            log_message = f"操作: {operation} | 耗时: {duration:.3f}s"
            if details:
                log_message += f" | 详情: {details}"
            
            logger.info(log_message)
        except Exception as e:
            print(f"记录性能日志失败: {e}")
    
    @classmethod
    def log_api_request(cls, method: str, path: str, status_code: int, duration: float, logger_name: str = "api"):
        """
        记录API请求日志
        
        Args:
            method: HTTP方法
            path: 请求路径
            status_code: 状态码
            duration: 请求耗时
            logger_name: 日志记录器名称
        """
        try:
            logger = cls.get_logger(logger_name)
            
            status_category = "成功" if 200 <= status_code < 400 else "失败"
            log_message = f"{method} {path} | 状态: {status_code} ({status_category}) | 耗时: {duration:.3f}s"
            
            if 200 <= status_code < 400:
                logger.info(log_message)
            else:
                logger.warning(log_message)
        except Exception as e:
            print(f"记录API请求日志失败: {e}") 