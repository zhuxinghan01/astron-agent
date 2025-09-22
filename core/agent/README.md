# Agent

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/Quality-A%2B-brightgreen)](#code-quality)

Agent 是一个基于 FastAPI 的智能Agent系统，提供多种类型的智能对话和推理能力。系统采用现代化的DDD（领域驱动设计）架构，支持插件扩展，集成了多种Agent运行器和工作流引擎。

## ✨ 核心特性

- **多Agent支持**: 提供Chat、CoT（思维链）、CoT Process等多种Agent类型
- **插件化架构**: 支持知识库、链接处理、MCP协议、工作流等插件扩展
- **工作流引擎**: 独立的工作流引擎，支持复杂业务场景编排
- **异步高性能**: 基于FastAPI和异步编程模式，支持高并发处理
- **完整监控**: 集成xingchen-utils追踪和监控系统
- **数据持久化**: 支持MySQL数据存储和Redis缓存
- **专业启动**: 功能完整的命令行启动入口，支持参数配置和优雅关闭
- **灵活配置**: 多层配置系统（命令行参数、环境变量、配置文件）
- **类型安全**: 使用Pydantic V2和Pyright进行严格的类型检查和数据验证
- **代码质量**: 集成Black、isort、Pyright、Pylint等代码质量工具，达到A+评级
- **测试完善**: 571个单元测试覆盖所有核心组件，100%测试通过率，覆盖率84.88%
- **框架兼容**: 完全兼容Pydantic V2，支持现代Python 3.11+特性
- **开源标准**: 遵循现代开源项目结构和最佳实践

## 🏗️ 系统架构

### 项目结构

```
agent/
├── logs/                    # 日志目录
├── api/                     # API层
│   ├── v1/                  # API接口（版本化）
│   │   ├── openapi.py       # OpenAPI端点
│   │   ├── bot_config_mgr_api.py # 配置管理API
│   │   └── workflow_agent.py # 工作流Agent API
│   ├── schemas/             # 数据模型（VO/DTO）
│   │   ├── agent_response.py
│   │   ├── completion.py
│   │   └── bot_config.py
│   └── app.py              # FastAPI应用主入口
│
├── service/                 # 应用服务层
│   ├── builder/             # 服务构建器
│   ├── plugin/              # 插件系统
│   │   ├── base.py          # 插件基类
│   │   ├── knowledge.py     # 知识库插件
│   │   ├── link.py          # 链接处理插件
│   │   ├── mcp.py           # MCP协议插件
│   │   └── workflow.py      # 工作流插件
│   └── runner/              # 服务运行器
│
├── repository/              # 数据访问层
│   ├── mysql_client.py      # MySQL客户端
│   ├── bot_config_client.py # 配置访问
│   └── bot_config_table.py  # 数据库模型
│
├── cache/                   # 缓存层
│   └── redis_client.py      # Redis客户端
│
├── engine/                  # 工作流引擎
│   ├── nodes/               # 引擎节点实现
│   │   ├── chat/            # 对话节点
│   │   ├── cot/             # 思维链节点
│   │   └── cot_process/     # 过程式思维链节点
│   └── entities/            # 引擎实体对象
│
├── domain/                  # 领域层
│   ├── models/              # 数据库模型
│   └── entity/              # 业务实体
│
├── infra/                   # 基础设施层
│   ├── config/              # 配置管理
│   └── app_auth.py          # 认证基础设施
│
├── exceptions/              # 统一异常处理
├── consts/                  # 常量定义
├── tests/                   # 测试目录
│   ├── unit/                # 单元测试 (571个测试用例)
│   │   ├── api/             # API层测试
│   │   │   └── schemas/     # 数据模型测试
│   │   ├── service/         # 服务层测试
│   │   ├── engine/          # 引擎层测试
│   │   ├── cache/           # 缓存层测试
│   │   ├── repository/      # 仓库层测试
│   │   └── exceptions/      # 异常处理测试
│   ├── integration/         # 集成测试
│   └── fixtures/            # 测试数据和Mock对象
├── scripts/                 # 工具脚本
├── .env.example            # 环境配置模板
└── main.py                 # 应用启动入口
```

### 架构层次

**API层** - RESTful API接口，支持版本化管理
**服务层** - 应用服务和业务逻辑编排
**引擎层** - 独立的工作流引擎和节点系统
**领域层** - 核心业务模型和实体
**仓库层** - 数据访问和持久化
**缓存层** - Redis缓存和会话管理
**基础设施层** - 配置、认证等基础服务

### Agent系统

- **Chat Agent**: 处理对话式交互，支持上下文管理
- **CoT Agent**: 实现思维链推理，提供逐步推理能力
- **CoT Process Agent**: 基于过程的思维链实现，支持复杂推理流程

### 工作流引擎

独立的工作流引擎系统，支持：
- 节点化处理流程
- 复杂业务场景编排
- 可扩展的节点类型

## 🚀 快速开始

### 环境要求

- Python 3.11+
- MySQL 数据库
- Redis 缓存服务

### 安装依赖

```bash
# 使用 uv 包管理器（推荐）
uv install

# 或使用 pip
pip install -r requirements.txt
```

### 配置环境

1. 复制环境配置模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，配置以下项：
   - 数据库连接信息（MySQL）
   - Redis缓存服务配置
   - LLM服务配置

### 启动服务

#### 🎯 推荐启动方式（main.py）

**基础启动:**
```bash
# 标准启动（推荐）
python main.py

# 查看帮助信息
python main.py --help
```

**高级配置启动:**
```bash
# 自定义主机和端口
python main.py --host 0.0.0.0 --port 8080

# 开发模式（热重载）
python main.py --reload

# 跳过监控系统初始化
python main.py --no-monitoring

# 组合使用
python main.py --host 0.0.0.0 --port 8080 --reload
```

#### 📋 启动输出示例

```
🚀 正在启动 Agent (Agent)
📝 运行环境: development
🌐 服务地址: http://0.0.0.0:17870
📊 正在初始化监控系统...
✅ 监控系统初始化完成
🔧 正在创建服务器...
✨ Agent 启动完成！
📚 API文档: http://0.0.0.0:17870/docs
```

#### 🔧 其他启动方式

**FastAPI开发调试:**
```bash
# 快速开发测试
python api/app.py
```

**生产环境部署:**
```bash
# 使用uvicorn直接启动
uvicorn api.app:app --host 0.0.0.0 --port 8000

# Docker容器化部署
python main.py --host 0.0.0.0 --no-monitoring
```

## 📖 API文档

启动服务后访问：
- Swagger UI: `http://localhost:17870/docs` (默认端口)
- ReDoc: `http://localhost:17870/redoc` (默认端口)

> 💡 **提示**: 如果使用了自定义端口，请相应调整URL中的端口号

### 主要API端点

#### Agent相关
- `POST /agent/v1/chat/completions` - OpenAPI兼容的聊天接口
- `POST /agent/v1/custom/chat/completions` - 工作流Agent接口（用户模式）

#### 配置管理
- `GET /agent/v1/bot-config` - 获取机器人配置
- `POST /agent/v1/bot-config` - 创建机器人配置
- `PUT /agent/v1/bot-config` - 更新机器人配置
- `DELETE /agent/v1/bot-config` - 删除机器人配置（通过query参数指定app_id和bot_id）

## 🛠️ 开发指南

### 代码质量要求

项目严格遵循代码质量标准，目前达到 **A+ 评级**：

```bash
# 运行所有质量检查
python scripts/quality_check.py

# 代码格式化
python -m black --line-length=88 .

# 导入排序
python -m isort . --settings-path=pyproject.toml

# 类型检查
python -m pyright

# 静态分析
python -m pylint <filename> --rcfile=pyproject.toml

# 代码风格检查
python -m flake8 <filename>
```

### 开发规范

1. **类型注解**: 所有函数和方法必须包含类型注解
2. **行长度限制**: 最大88字符
3. **导入组织**: 使用isort进行导入排序
4. **类型检查**: Pyright严格模式，全面类型安全检查
5. **异步编程**: FastAPI异步/等待模式
6. **DDD架构**: 遵循领域驱动设计原则

### 添加新组件

#### 添加新的Agent类型

1. 在 `engine/nodes/<type>/` 创建节点实现
2. 实现 `engine/nodes/base.py` 的基础接口
3. 添加相应的提示词处理
4. 在服务层构建器中注册

#### 添加新插件

1. 继承 `service/plugin/base.py`
2. 实现必需的插件方法
3. 添加插件配置支持
4. 在插件系统中注册

#### 添加新API端点

1. 在 `api/v1/` 创建路由文件
2. 在 `api/schemas/` 定义请求/响应模型
3. 使用服务层组件实现业务逻辑
4. 在 `api/app.py` 中包含路由

#### 添加新数据访问

1. 在 `repository/` 创建数据访问类
2. 在 `domain/models/` 定义数据模型
3. 在 `cache/` 添加缓存逻辑（如需要）

## ⚙️ 配置说明

### 启动配置

#### main.py 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--host` | string | `0.0.0.0` | 服务器绑定地址 |
| `--port` | int | `17870` | 服务器端口号 |
| `--reload` | flag | `false` | 启用开发模式（热重载） |
| `--no-monitoring` | flag | `false` | 跳过监控系统初始化 |
| `--version` | flag | - | 显示版本信息 |

#### 配置优先级

系统采用多层配置机制，优先级从高到低：

1. **命令行参数** - 最高优先级
   ```bash
   python main.py --host 127.0.0.1 --port 8080
   ```

2. **环境变量** - 中等优先级
   ```bash
   export uvicorn_host=127.0.0.1
   export uvicorn_port=8080
   ```

3. **配置文件** - 基础优先级
   - `.env` 文件配置
   - `infra/config/` 模块配置

4. **默认值** - 兜底配置

### 环境配置

系统支持多种配置源：
- **环境变量配置**: `.env` 文件和系统环境变量
- **数据库配置存储**: 动态配置持久化
- **基础设施层配置**: `infra/config/` 模块统一管理
- **Polaris配置中心**: 远程配置支持（可选）

### LLM配置

支持多种大语言模型集成：
- OpenAI GPT系列
- 其他兼容OpenAI API的模型服务

### 数据库配置

- **MySQL**: 主要数据存储，使用SQLAlchemy 2.0
- **Redis**: 缓存和会话管理

### 监控配置

集成xingchen-utils提供：
- 分布式追踪
- 性能监控  
- 日志管理

## 🧪 测试

项目提供完整的测试覆盖，包括单元测试、集成测试和API测试。

### 测试命令

```bash
# 运行所有单元测试
PYTHONPATH=. /opt/anaconda3/bin/python -m pytest tests/unit/ -v

# 运行集成测试
PYTHONPATH=. /opt/anaconda3/bin/python -m pytest tests/integration/ -v

# 运行特定测试模块
PYTHONPATH=. /opt/anaconda3/bin/python -m pytest tests/unit/api/schemas/ -v

# 工作流Agent节点测试
python tests/integration/workflow_agent_node_test.py
```

### 测试覆盖

- **单元测试**: 571个测试用例，覆盖所有核心组件，覆盖率84.88%
  - API层测试: schemas、路由、响应格式
  - 服务层测试: 构建器、插件、运行器
  - 仓库层测试: 数据访问、缓存、配置管理
  - 异常处理测试: 错误码、异常层次、错误处理

- **集成测试**: 端到端API测试，完整业务流程验证
- **质量检查**: 通过A+级别代码质量标准

### 最新修复

✅ **v1.2.0 测试系统完善**
- 修复了Pydantic V2兼容性问题
- 解决了单元测试模块导入错误
- 统一了异常类属性访问接口
- 创建了完整的测试包结构
- 实现100%测试通过率

## 🔧 维护工具

### 应用管理

```bash
# 应用启动（推荐）
python main.py

# 查看启动帮助
python main.py --help

# 检查应用版本
python main.py --version

# 开发模式启动
python main.py --reload
```

### 代码质量工具

```bash
# 代码质量检查
python scripts/quality_check.py

# 清理旧目录和缓存（重构后）
python scripts/cleanup_old_directories.py

# 导入路径修复（重构工具）
python scripts/fix_imports.py
```

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 贡献前检查清单

- [ ] 运行 `python scripts/quality_check.py` 验证代码质量
- [ ] 确保所有类型注解完整
- [ ] 验证导入组织正确
- [ ] 检查行长度限制（88字符）
- [ ] 使用适当的测试数据测试API端点
- [ ] 遵循DDD架构原则

## 📧 支持

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 项目文档: 查看 `doc/` 目录下的详细文档

---

**项目状态**: v1.2.0 - 已完成架构重构和测试系统完善，采用现代化DDD架构，代码质量达到A+级别，571个单元测试100%通过，已准备开源发布。