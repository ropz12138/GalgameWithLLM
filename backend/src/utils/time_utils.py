"""
时间工具类 - 统一处理游戏中的日期时间
"""
from datetime import datetime, timedelta
from typing import Union, Tuple


class TimeUtils:
    """时间工具类"""
    
    # 游戏时间格式
    GAME_DATETIME_FORMAT = "%Y-%m-%d %H:%M"
    GAME_TIME_FORMAT = "%H:%M"
    GAME_DATE_FORMAT = "%Y-%m-%d"
    
    @classmethod
    def parse_game_time(cls, time_str: str) -> datetime:
        """
        解析游戏时间字符串为datetime对象
        
        Args:
            time_str: 时间字符串，支持 "YYYY-MM-DD HH:MM" 或 "HH:MM" 格式
            
        Returns:
            datetime对象
        """
        try:
            # 尝试解析完整日期时间格式
            if len(time_str) > 5 and ' ' in time_str:
                return datetime.strptime(time_str, cls.GAME_DATETIME_FORMAT)
            else:
                # 如果只有时间，使用默认日期
                time_only = datetime.strptime(time_str, cls.GAME_TIME_FORMAT).time()
                return datetime.combine(datetime(2024, 1, 15), time_only)
        except ValueError:
            # 如果解析失败，返回默认时间
            return datetime(2024, 1, 15, 7, 0)
    
    @classmethod
    def format_game_time(cls, dt: datetime, include_date: bool = True) -> str:
        """
        格式化datetime对象为游戏时间字符串
        
        Args:
            dt: datetime对象
            include_date: 是否包含日期
            
        Returns:
            格式化的时间字符串
        """
        if include_date:
            return dt.strftime(cls.GAME_DATETIME_FORMAT)
        else:
            return dt.strftime(cls.GAME_TIME_FORMAT)
    
    @classmethod
    def add_minutes(cls, time_str: str, minutes: int) -> str:
        """
        给时间字符串添加分钟数
        
        Args:
            time_str: 原时间字符串
            minutes: 要添加的分钟数
            
        Returns:
            新的时间字符串
        """
        dt = cls.parse_game_time(time_str)
        new_dt = dt + timedelta(minutes=minutes)
        return cls.format_game_time(new_dt, include_date=' ' in time_str)
    
    @classmethod
    def get_time_only(cls, time_str: str) -> str:
        """
        从完整时间字符串中提取时间部分
        
        Args:
            time_str: 时间字符串
            
        Returns:
            时间部分 (HH:MM)
        """
        dt = cls.parse_game_time(time_str)
        return dt.strftime(cls.GAME_TIME_FORMAT)
    
    @classmethod
    def get_date_only(cls, time_str: str) -> str:
        """
        从完整时间字符串中提取日期部分
        
        Args:
            time_str: 时间字符串
            
        Returns:
            日期部分 (YYYY-MM-DD)
        """
        dt = cls.parse_game_time(time_str)
        return dt.strftime(cls.GAME_DATE_FORMAT)
    
    @classmethod
    def is_same_day(cls, time1: str, time2: str) -> bool:
        """
        判断两个时间是否在同一天
        
        Args:
            time1: 第一个时间字符串
            time2: 第二个时间字符串
            
        Returns:
            是否在同一天
        """
        dt1 = cls.parse_game_time(time1)
        dt2 = cls.parse_game_time(time2)
        return dt1.date() == dt2.date()
    
    @classmethod
    def time_difference_minutes(cls, time1: str, time2: str) -> int:
        """
        计算两个时间之间的分钟差
        
        Args:
            time1: 第一个时间字符串
            time2: 第二个时间字符串
            
        Returns:
            分钟差 (time2 - time1)
        """
        dt1 = cls.parse_game_time(time1)
        dt2 = cls.parse_game_time(time2)
        return int((dt2 - dt1).total_seconds() / 60)
    
    @classmethod
    def is_time_in_range(cls, current_time: str, start_time: str, end_time: str) -> bool:
        """
        判断当前时间是否在指定时间范围内
        
        Args:
            current_time: 当前时间字符串
            start_time: 开始时间字符串 (HH:MM格式)
            end_time: 结束时间字符串 (HH:MM格式)
            
        Returns:
            是否在时间范围内
        """
        current_dt = cls.parse_game_time(current_time)
        current_time_only = current_dt.time()
        
        start_time_only = datetime.strptime(start_time, cls.GAME_TIME_FORMAT).time()
        end_time_only = datetime.strptime(end_time, cls.GAME_TIME_FORMAT).time()
        
        return start_time_only <= current_time_only < end_time_only
    
    @classmethod
    def get_current_timestamp(cls) -> str:
        """
        获取当前时间戳 (用于日志等)
        
        Returns:
            当前时间戳字符串
        """
        return datetime.now().strftime("%H:%M:%S")
    
    @classmethod
    def format_display_time(cls, time_str: str) -> str:
        """
        格式化时间用于显示
        
        Args:
            time_str: 时间字符串
            
        Returns:
            格式化后的显示时间
        """
        dt = cls.parse_game_time(time_str)
        return dt.strftime("%m月%d日 %H:%M")
    
    @classmethod
    def get_weekday_name(cls, time_str: str) -> str:
        """
        获取星期几的中文名称
        
        Args:
            time_str: 时间字符串
            
        Returns:
            星期几的中文名称
        """
        dt = cls.parse_game_time(time_str)
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return weekdays[dt.weekday()] 