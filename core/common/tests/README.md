# Common Module Unit Tests

本文档描述了core/common模块的单元测试实现。

## 测试概述

本测试套件为core/common模块提供了全面的单元测试覆盖，包括：

- 异常处理模块 (exceptions)
- 工具函数模块 (utils)
- 审核系统模块 (audit_system)
- OTLP追踪模块 (otlp)
- 初始化模块 (initialize)
- 主模块 (main)

## 测试结构

```
tests/
├── __init__.py
├── conftest.py              # 测试配置和fixtures
├── test_exceptions.py       # 异常处理测试
├── test_utils.py           # 工具函数测试
├── test_audit_system.py    # 审核系统测试
├── test_otlp_sid.py        # OTLP SID测试
├── test_otlp_ip.py         # OTLP IP测试
├── test_otlp_span.py       # OTLP Span测试
├── test_initialize.py       # 初始化模块测试
├── test_main.py            # 主模块测试
└── README.md               # 本文档
```

## 测试配置

### 环境设置

测试使用以下配置：

- **Python版本**: 3.11+
- **测试框架**: pytest
- **覆盖率工具**: pytest-cov
- **包管理器**: uv
- **PYTHONPATH**: 设置为core目录

### 配置文件

- `pytest.ini`: pytest配置
- `.coveragerc`: 覆盖率配置
- `pyproject.toml`: 项目依赖配置

## 测试覆盖情况

### 已测试模块

1. **异常处理模块** (100% 覆盖率)
   - BaseExc类及其方法
   - 异常代码定义
   - 自定义异常类

2. **工具函数模块** (100% 覆盖率)
   - HMACAuth类及其静态方法
   - 认证参数构建
   - 请求URL构建
   - 认证头构建

3. **审核系统模块** (95% 覆盖率)
   - Sentence工具类
   - 文本处理函数
   - 状态枚举

4. **OTLP模块** (部分覆盖)
   - SID生成器
   - IP地址获取
   - Span类基础功能

5. **初始化模块** (100% 覆盖率)
   - 服务初始化函数
   - 异常处理

6. **主模块** (100% 覆盖率)
   - main函数

### 测试统计

- **总测试数**: 80个
- **通过测试**: 64个
- **失败测试**: 16个
- **总体覆盖率**: 41.33%

## 运行测试

### 运行所有测试

```bash
cd /Users/dl/XfProjects/xfyun_webdev_gitee/openstellar/core/common
PYTHONPATH=/Users/dl/XfProjects/xfyun_webdev_gitee/openstellar/core uv run python -m pytest tests/ -v
```

### 运行特定测试

```bash
# 运行异常处理测试
PYTHONPATH=/Users/dl/XfProjects/xfyun_webdev_gitee/openstellar/core uv run python -m pytest tests/test_exceptions.py -v

# 运行工具函数测试
PYTHONPATH=/Users/dl/XfProjects/xfyun_webdev_gitee/openstellar/core uv run python -m pytest tests/test_utils.py -v
```

### 生成覆盖率报告

```bash
# 生成终端覆盖率报告
PYTHONPATH=/Users/dl/XfProjects/xfyun_webdev_gitee/openstellar/core uv run python -m pytest tests/ --cov=common --cov-report=term-missing

# 生成HTML覆盖率报告
PYTHONPATH=/Users/dl/XfProjects/xfyun_webdev_gitee/openstellar/core uv run python -m pytest tests/ --cov=common --cov-report=html:htmlcov
```

## 测试用例说明

### 异常处理测试

测试BaseExc类的各种功能：

- 基本初始化
- 带原始参数的初始化
- 异常调用方法
- 字符串表示
- 异常继承链

### 工具函数测试

测试HMACAuth类的认证功能：

- 认证参数构建
- 不同HTTP方法的处理
- 不同URL的处理
- 认证头格式验证
- 错误处理

### 审核系统测试

测试Sentence工具类：

- 文本句子提取
- 结束符号检测
- 文本分割功能
- 边界条件处理

### OTLP模块测试

测试OTLP相关功能：

- SID生成器
- IP地址获取
- Span类基础功能
- 错误处理

## 已知问题

### 循环导入问题

某些模块存在循环导入问题，导致无法直接测试：

- audit_system.base模块
- audit_system.orchestrator模块
- otlp.trace.span模块的完整功能

### 测试失败原因

1. **模块导入问题**: 某些模块存在循环依赖
2. **Mock配置问题**: OpenTelemetry相关模块的mock配置
3. **测试断言问题**: 某些测试的断言条件需要调整

## 改进建议

### 提高覆盖率

1. **解决循环导入**: 重构模块结构，消除循环依赖
2. **完善Mock配置**: 为OpenTelemetry模块提供正确的mock
3. **增加边界测试**: 添加更多边界条件和错误情况测试

### 测试质量改进

1. **参数化测试**: 使用pytest.mark.parametrize减少重复代码
2. **Fixture优化**: 创建更多可重用的fixture
3. **集成测试**: 添加模块间的集成测试

## 维护说明

### 添加新测试

1. 在相应的测试文件中添加测试用例
2. 确保测试覆盖新的功能
3. 更新覆盖率目标

### 更新测试

1. 当模块功能变更时，更新相应的测试
2. 保持测试的独立性和可重复性
3. 定期检查测试覆盖率

## 依赖项

测试依赖以下包：

- pytest>=7.0.0
- pytest-asyncio>=0.21.0
- pytest-cov>=4.0.0
- pytest-mock>=3.10.0

这些依赖已在pyproject.toml中配置。