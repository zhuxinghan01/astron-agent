"""
Constants definition module containing various constants and configuration
parameters used in the project.
"""

import os

# 环境变量
Env = os.getenv("ENVIRONMENT")
ENV_PRODUCTION = "production"
ENV_PRERELEASE = "prerelease"
ENV_DEVELOPMENT = "development"



# 配置中心连接
POLARIS_USERNAME_KEY = "PolarisUsername"
POLARIS_PASSWORD_KEY = "PolarisPassword"
POLARIS_PRO_URL = ""
POLARIS_PRE_URL = ""
POLARIS_DEV_URL = ""
POLARIS_PRO_CLUSTER_GROUP = "pro"
POLARIS_PRE_CLUSTER_GROUP = "pre"
POLARIS_DEV_CLUSTER_GROUP = "dev"
POLARIS_PROJECT_NAME = "r"
POLARIS_SERVICE_NAME = "aitools"
POLARIS_VERSION = "1.0.2"
POLARIS_CONFIG_FILE = "aitools.env"

SERVICE_PORT = 18990

# 常量
IMAGE_GENERATE_MAX_PROMPT_LEN = 510

# SID服务相关环境变量名
SID_SERVICE_SUB = "SERVICE_SUB"
SID_SERVICE_LOCATION = "SERVICE_LOCATION"  # 保持原有拼写错误以兼容现有代码
SID_SERVICE_PORT = "SERVICE_PORT"
