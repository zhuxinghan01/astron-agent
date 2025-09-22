# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是 Stellar Agent 星辰Agent平台，一个基于 Spring Boot 的微服务架构项目。项目采用多模块Maven结构，支持多语言CI/CD开发工具链。

## 架构说明

### 核心模块
- **commons**: 公共模块，包含通用工具类和基础组件
- **hub**: 核心服务模块，负责主要业务逻辑
- **toolkit**: 工具包模块，提供各种工具功能
- **auth**: 认证授权模块，处理用户认证和权限管理

### 技术栈
- Java 21
- Spring Boot 3.5.4
- MyBatis Plus 3.5.7
- MySQL数据库
- Maven构建工具

## 开发命令

### 环境设置
```bash
# 一键设置开发环境
make dev-setup

# 安装开发工具链
make install-tools

# 检查工具安装状态
make check-tools
```

### Java后端开发
```bash
# 编译Java项目
make fmt-java
# 或直接使用Maven
cd backend-java && mvn compile

# 运行代码质量检查
make check-java
# 或直接使用Maven
cd backend-java && mvn test

# 运行特定模块的测试
mvn test -pl commons
mvn test -pl hub
mvn test -pl toolkit  
mvn test -pl auth
```

### Console项目开发
```bash
# 格式化Console Java后端代码
make fmt-console

# 运行Console Java后端代码质量检查
make check-console

# 检查Console代码格式（不修改文件）
make fmt-check-console

# 查看Console项目信息
make info-console

# 格式化Console前端TypeScript代码
make fmt-console-frontend

# 运行Console前端TypeScript代码质量检查
make check-console-frontend

# 检查Console前端代码格式（不修改文件）
make fmt-check-console-frontend

# 查看Console前端项目信息
make info-console-frontend

# 直接在console/backend目录运行Maven命令
cd console/backend && mvn compile
cd console/backend && mvn test

# 直接在console/frontend目录运行npm命令（如果有TypeScript项目）
cd console/frontend && npm install
cd console/frontend && npm run build
```

### 代码格式化和质量检查
```bash
# 格式化所有项目代码
make fmt

# 运行所有代码质量检查
make check

# 检查代码格式（不修改文件）
make fmt-check
```

### Git工作流
```bash
# 创建功能分支
make new-feature name=feature-name

# 创建修复分支
make new-hotfix name=hotfix-name

# 安全推送（验证分支命名规范）
make safe-push

# 安装Git钩子
make hooks-install
```

### 项目管理
```bash
# 查看项目状态
make project-status

# 显示帮助信息
make help

# 检查分支命名规范
make check-branch
```

## 开发规范

### 分支命名规范
- `master`: 主分支
- `develop`: 开发分支
- `feature-*`: 功能分支
- `hotfix-*`: 修复分支

### 提交信息规范
遵循 Conventional Commits 标准：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 格式化
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建工具、依赖更新

示例：
```bash
git commit -m "feat(auth): add OAuth2 authentication support"
git commit -m "fix(hub): resolve database connection issue"
```

### 代码质量
- 项目使用 checkstyle.xml 进行代码风格检查
- 使用 pmd-ruleset.xml 进行代码质量分析
- 使用 spotbugs-exclude.xml 排除已知问题

## 常用开发任务

### 添加新模块
1. 在 backend-java/pom.xml 中添加模块声明
2. 创建模块目录和pom.xml
3. 遵循现有模块的结构和命名约定

### 运行单个服务
```bash
# 运行认证服务
cd backend-java/auth && mvn spring-boot:run

# 运行核心服务
cd backend-java/hub && mvn spring-boot:run

# 运行工具包服务
cd backend-java/toolkit && mvn spring-boot:run
```

### 数据库操作
- 配置文件位于各模块的 src/main/resources/application.yml
- 使用 MyBatis Plus 进行数据库操作
- 数据库配置示例在 .env.example 中提供

### Docker部署
```bash
# 使用Docker Compose启动服务
cd backend-java/docker && docker-compose up -d
```

## 重要文件

- `Makefile`: 核心构建和CI工具
- `Makefile-readme.md`: Makefile使用指南
- `backend-java/pom.xml`: Maven父项目配置
- `.env.example`: 环境变量配置示例
- `backend-java/checkstyle.xml`: 代码风格检查配置
- `backend-java/pmd-ruleset.xml`: 代码质量规则
- `.cursor/rules/`: Cursor IDE规则配置

## 开发注意事项

1. **环境配置**: 首次开发需要运行 `make dev-setup` 配置环境
2. **代码提交**: 使用项目提供的Git钩子确保代码质量
3. **分支管理**: 严格按照分支命名规范创建和管理分支
4. **测试**: 每次提交前运行 `make check` 确保代码质量
5. **文档更新**: 重要变更需要同步更新相关文档