import os

from loguru import logger

from common.service.base import ServiceFactory
from common.service.log.logger_service import LogService


class LogServiceFactory(ServiceFactory):
    def __init__(self):
        super().__init__(LogService)

    def create(self):
        """
        Initialize log instance.
        :return:
        """
        print("------ init loguru in factory")
        current_dir = os.getenv("COMMON_LOG_PATH", "./")
        log_dir = os.path.join(current_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)  # 确保日志目录存在

        # 配置日志存储路径、日志等级
        log_path = os.path.join(log_dir, "app.log")
        log_level = os.getenv("COMMON_LOG_LEVEL", "ERROR")

        # 初始化 loguru
        logger.remove()  # 移除默认的日志配置

        log_format = "{level} | {time:YYYY-MM-DD HH:mm:ss} | {file} - {function}: {line} {message}"

        # 添加文件处理器，带有日志等级和相对路径
        logger.add(
            log_path,
            rotation="100 MB",  # 日志文件大小超过100MB自动切分
            retention="10 days",  # 日志保留10天
            compression="zip",  # 可选：压缩旧的日志文件
            format=log_format,  # 自定义格式
            serialize=True,  # 启用 JSON 格式
            level=log_level,  # 日志等级
        )
        logger.debug(
            f"Loguru initialized successfully. Log file: {log_path}, Log level: {log_level}"
        )
        return LogService()


# print("------ logger factory")
