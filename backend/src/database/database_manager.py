"""
数据库管理器
负责数据库连接和基本操作
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from .config import get_database_url
import json
from typing import Dict, List, Any, Optional


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.database_url = get_database_url()
    
    def get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """执行查询并返回结果"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchall()
        except Exception as e:
            print(f"❌ 执行查询失败: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        """执行更新操作"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()
                    return True
        except Exception as e:
            print(f"❌ 执行更新失败: {e}")
            return False
    
    def create_tables(self):
        """创建数据库表"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 这里可以添加创建表的SQL语句
                    pass
        except Exception as e:
            print(f"❌ 创建表失败: {e}")


# 全局数据库管理器实例
db_manager = DatabaseManager() 