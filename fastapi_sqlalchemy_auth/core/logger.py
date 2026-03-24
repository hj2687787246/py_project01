# 日志配置文件
import os
from loguru import logger
from datetime import datetime

# 1. 创建日志目录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 2. 配置日志格式和文件
log_file_path = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

# 3. 移除默认的 handler，添加自定义配置
logger.remove()
logger.add(
    sink=log_file_path,          # 日志文件路径
    rotation="00:00",            # 每天 0 点分割日志
    retention="30 days",         # 保留 30 天
    level="INFO",                 # 日志级别
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{line} | {message}",
    encoding="utf-8"
)

# 4. 同时也在控制台输出（方便开发调试）
logger.add(
    sink=lambda msg: print(msg, end=""),
    level="DEBUG",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# 导出 logger 实例
def get_logger():
    return logger
