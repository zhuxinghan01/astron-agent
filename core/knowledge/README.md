# Knowledge Service

Core knowledge base service for the Stellar Agent platform, a high-performance RAG (Retrieval-Augmented Generation) service built with FastAPI.

## 🚀 Project Overview

Knowledge Service is the core knowledge component of the Stellar Agent platform, providing intelligent Q&A, document retrieval, and knowledge management capabilities. It supports multiple AI models and retrieval strategies, offering a unified knowledge service interface for upper-layer applications.

### Core Features

- 🧠 **Multi-strategy RAG Support**: Supports multiple retrieval-augmented generation strategies
- 🔌 **Multi-model Integration**: Integrates multiple AI models including iFlytek Spark, AIUI, etc.
- 📊 **Complete Monitoring**: Built-in metrics monitoring and distributed tracing
- 🏗️ **Microservice Architecture**: Modern microservice design based on FastAPI
- 🧪 **High Quality Code**: 100% test coverage with strict coding standards

## 📋 Technology Stack

- **Python**: 3.11+
- **Web Framework**: FastAPI 0.115+
- **HTTP Client**: aiohttp 3.12+
- **Data Validation**: Pydantic 2.9+
- **ASGI Server**: Uvicorn 0.34+
- **Code Quality**: Black, Flake8, isort, MyPy, Pylint
- **Testing Framework**: pytest 8.4+
- **Monitoring & Tracing**: OpenTelemetry (xingchen-utils)

## 🏗️ Project Architecture

```
knowledge/
├── api/                    # API layer
│   ├── v1/api.py          # REST API route definitions
│   └── log_conf.py        # Logging configuration
├── service/               # Service layer
│   ├── rag_strategy.py    # RAG strategy interface
│   ├── rag_strategy_factory.py  # Strategy factory
│   └── impl/              # Strategy implementations
│       ├── aiui_strategy.py     # AIUI strategy
│       ├── cbg_strategy.py      # CBG strategy
│       └── sparkdesk_strategy.py # iFlytek Spark strategy
├── infra/                 # Infrastructure layer
│   ├── aiui/              # AIUI integration
│   ├── desk/              # iFlytek Spark Desktop
│   └── xinghuo/           # iFlytek Spark service
├── domain/                # Domain models
│   ├── entity/            # Entity objects
│   └── response.py        # Response models
├── consts/                # Constant definitions
├── exceptions/            # Exception handling
├── utils/                 # Utility classes
└── main.py               # Application entry point
```

## 🚦 Quick Start

### Prerequisites

- Python 3.11 or higher
- uv package manager (recommended) or pip

### Install Dependencies

```bash
# Install using uv (recommended)
uv sync

# Or install using pip
pip install -r requirements.txt
```

### Environment Configuration

Copy the configuration file and modify the relevant parameters:

```bash
cp config.env .env
```

Main configuration items:

```bash
# Monitoring configuration
METRIC_ENDPOINT=your-metric-endpoint
TRACE_ENDPOINT=your-trace-endpoint

# Service configuration
WORKERS=5
PORT=20010

# AI model configuration
AIUI_API_KEY=your-aiui-key
SPARK_API_KEY=your-spark-key
```

### Start Service

```bash
# Development environment
python main.py

# Production environment
uvicorn main:create_app --host 0.0.0.0 --port 20010 --workers 5
```

### Docker Deployment

```bash
# Build image
docker build -t knowledge-service .

# Run container
docker run -d -p 20010:20010 \
  --env-file .env \
  knowledge-service
```

## 🔧 Development Guide

### Code Standards

The project adopts strict code quality standards:

```bash
# Code formatting
black .
isort .

# Code inspection
flake8 .
pylint service/ infra/ domain/
mypy .
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest service/impl/aiui_strategy_test_1.py

# Generate coverage report
pytest --cov=. --cov-report=html
```

Current test coverage: **100%** ✅

### Adding New RAG Strategies

1. Create new strategy implementation in `service/impl/` directory
2. Inherit from `RagStrategy` base class
3. Implement necessary methods
4. Register new strategy in `rag_strategy_factory.py`
5. Write corresponding unit tests

Example:

```python
from service.rag_strategy import RagStrategy

class CustomStrategy(RagStrategy):
    def query(self, question: str) -> str:
        # Implement custom retrieval logic
        pass
```

## 📡 API Documentation

After starting the service, you can access the following addresses:

- **Swagger UI**: http://localhost:20010/docs
- **ReDoc**: http://localhost:20010/redoc

### Main API Endpoints

- `POST /api/v1/rag/query` - RAG Q&A interface
- `GET /api/v1/health` - Health check

## 📊 Monitoring & Operations

### Metrics Monitoring

The service integrates OpenTelemetry metrics monitoring:

- **HTTP Request Metrics**: Request count, response time, error rate
- **Business Metrics**: RAG query success rate, model response time
- **System Metrics**: Memory usage, CPU utilization

### Distributed Tracing

Supports complete request chain tracing:

- **Request Tracing**: Complete request lifecycle
- **Dependency Tracing**: External service call tracing
- **Error Tracing**: Exception and error chain analysis

### Log Management

Structured logging based on loguru:

```bash
# View real-time logs
tail -f logs/knowledge.log

# View error logs
grep "ERROR" logs/knowledge.log
```

## 🤝 Contributing Guidelines

1. Fork this repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Create Pull Request

### Commit Standards

Follow [Conventional Commits](https://www.conventionalcommits.org/) standard:

- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation updates
- `style`: Code formatting
- `refactor`: Code refactoring
- `test`: Test related
- `chore`: Toolchain, dependency updates

## 📄 License

This project is open source under the MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support & Feedback

- 📧 Email: your-email@company.com
- 🐛 Issue Reports: [GitHub Issues](https://github.com/your-org/openstellar/issues)
- 📚 Documentation: [Project Documentation](https://docs.your-domain.com)

---

**Stellar Agent Platform** | Making AI smarter, making knowledge more valuable