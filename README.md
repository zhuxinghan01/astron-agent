# Astra Agent - Agent Platform

A comprehensive microservices-based platform for building and deploying AI agents, featuring a modular architecture with multi-language support and advanced CI/CD toolchain.

## Overview

Astra Agent is a Stellar Agent platform built on Spring Boot microservices architecture with multi-module Maven structure, supporting comprehensive multi-language CI/CD development toolchain. The platform provides intelligent agent creation, management, deployment capabilities along with enterprise-grade security and scalability features.

## Architecture

### Core Modules
- **commons**: Common module containing shared utilities and base components
- **hub**: Core service module handling main business logic
- **toolkit**: Toolkit module providing various tool functionalities
- **auth**: Authentication and authorization module for user management and permissions

### Technology Stack
- **Backend**: Java 21, Spring Boot 3.5.4, MyBatis Plus 3.5.7, MySQL
- **Frontend**: React 18+, TypeScript, Vite, Tailwind CSS
- **Build Tools**: Maven, npm/pnpm
- **Infrastructure**: Docker, Redis, MinIO
- **Quality Tools**: Checkstyle, PMD, SpotBugs, ESLint

## Project Structure

```
astra-agent/
├── console/                    # Console subsystem (Backend + Frontend)
│   ├── backend/               # Java Spring Boot multi-modules
│   │   ├── auth/              # Authentication module
│   │   ├── commons/           # Common utilities and DTOs
│   │   ├── hub/               # Main business domain
│   │   ├── toolkit/           # Toolkit services
│   │   ├── config/            # Code quality configs
│   │   └── docker/            # Docker compose services
│   └── frontend/              # React TypeScript SPA
├── core/                      # Core platform services
│   ├── agent/                 # Agent execution engine (Python)
│   ├── common/                # Shared Python libraries
│   ├── knowledge/             # Knowledge base service (Python)
│   ├── memory/                # Memory management
│   ├── plugin/                # Plugin system
│   ├── tenant/                # Multi-tenant service (Go)
│   └── workflow/              # Workflow orchestration (Python)
├── docs/                      # Documentation
└── makefiles/                 # Build system components
```

## Quick Start

### Prerequisites
- Java 21+
- Maven 3.8+
- Node.js 18+
- Docker & Docker Compose
- Python 3.9+ (for core services)
- Go 1.21+ (for tenant service)

### Environment Setup

```bash
# One-time development environment setup
make dev-setup

# Or manually install tools
make install-tools

# Check tool installation status
make check-tools
```

### Backend Development

```bash
# Compile Java projects
make fmt-java
# or directly with Maven
cd console/backend && mvn compile

# Run code quality checks
make check-java
# or directly with Maven
cd console/backend && mvn test

# Run specific module tests
mvn test -pl commons
mvn test -pl hub
mvn test -pl toolkit
mvn test -pl auth
```

### Console Development

```bash
# Format Console Java backend code
make fmt-console

# Run Console Java backend quality checks
make check-console

# Format Console frontend TypeScript code
make fmt-console-frontend

# Run Console frontend quality checks
make check-console-frontend

# Direct commands for console backend
cd console/backend && mvn compile
cd console/backend && mvn test

# Direct commands for console frontend
cd console/frontend && npm install
cd console/frontend && npm run build
```

### Core Services Development

```bash
# Python services (agent, knowledge, workflow, etc.)
cd core/agent && python -m pytest
cd core/knowledge && python -m pytest

# Go service (tenant)
cd core/tenant && go test ./...
cd core/tenant && go build
```

## Development Commands

### Code Quality and Formatting
```bash
# Format all project code
make fmt

# Run all code quality checks
make check

# Check code format (without modifying files)
make fmt-check
```

### Git Workflow
```bash
# Create feature branch
make new-feature name=feature-name

# Create hotfix branch
make new-hotfix name=hotfix-name

# Safe push (validates branch naming conventions)
make safe-push

# Install Git hooks
make hooks-install
```

### Project Management
```bash
# View project status
make project-status

# Show help information
make help

# Check branch naming conventions
make check-branch
```

## Features

### Console Features
- **User Management**: Login, registration, authentication, rate limiting, and auditing
- **Agent Management**: Create, publish, marketplace display, and sharing
- **Data & Knowledge**: Dataset management, file handling, and retrieval tracking
- **Workflow Canvas**: Visual orchestration and template management
- **Operations**: Statistics, logging, and configuration management

### Core Platform Features
- **Agent Engine**: Multi-step reasoning, plugin integration, workflow execution
- **Knowledge Base**: RAG implementation, document processing, semantic search
- **Memory Management**: Database operations, schema management, data export/import
- **Plugin System**: Extensible tool integration, RPA automation, external API connections
- **Multi-tenancy**: Isolated environments, resource management, authentication
- **Workflow**: Visual flow designer, node-based execution, template library

## Development Standards

### Branch Naming Convention
- `master`: Main branch
- `develop`: Development branch
- `feature-*`: Feature branches
- `hotfix-*`: Hotfix branches

### Commit Message Convention
Following Conventional Commits standard:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation updates
- `style`: Code formatting
- `refactor`: Code refactoring
- `test`: Test-related changes
- `chore`: Build tools, dependency updates

Examples:
```bash
git commit -m "feat(auth): add OAuth2 authentication support"
git commit -m "fix(hub): resolve database connection issue"
```

### Code Quality
- Uses `checkstyle.xml` for Java code style checking
- Uses `pmd-ruleset.xml` for code quality analysis
- Uses `spotbugs-exclude.xml` to exclude known issues
- Frontend follows ESLint configuration in `eslint.config.js`

## Deployment

### Docker Deployment
```bash
# Start services with Docker Compose
cd console/backend/docker && docker-compose up -d

# Build individual service images
docker build -t astra-agent/console-auth console/backend/auth/
docker build -t astra-agent/console-hub console/backend/hub/
```

### Service Configuration
- Backend configurations: `src/main/resources/application.yml` in each module
- Frontend configurations: `.env.example` and `vite.config.js`
- Environment variable examples provided in `.env.example`

## Testing

### Backend Testing
```bash
cd console/backend
mvn test

# Or run specific module tests
cd console/backend/auth && mvn test
cd console/backend/hub && mvn test
```

### Frontend Testing
```bash
cd console/frontend
npm test  # or yarn test
```

### Core Services Testing
```bash
# Python services
cd core/agent && python -m pytest
cd core/knowledge && python -m pytest

# Go service
cd core/tenant && go test ./...
```

## Common Development Tasks

### Adding New Modules
1. Add module declaration in `console/backend/pom.xml`
2. Create module directory and `pom.xml`
3. Follow existing module structure and naming conventions

### Running Individual Services
```bash
# Authentication service
cd console/backend/auth && mvn spring-boot:run

# Core hub service
cd console/backend/hub && mvn spring-boot:run

# Toolkit service
cd console/backend/toolkit && mvn spring-boot:run
```

### Database Operations
- Configuration files located in each module's `src/main/resources/application.yml`
- Uses MyBatis Plus for database operations
- Database configuration examples provided in `.env.example`

## Important Files

- `Makefile`: Core build and CI tools
- `CLAUDE.md`: Claude Code assistant instructions
- `console/backend/pom.xml`: Maven parent project configuration
- `.env.example`: Environment variable configuration examples
- `console/backend/checkstyle.xml`: Code style checking configuration
- `console/backend/pmd-ruleset.xml`: Code quality rules
- `.cursor/rules/`: Cursor IDE rule configurations

## Contributing

We welcome contributions through Issues and Pull Requests:

1. **Fork the repository** and create a feature branch (recommended naming: `feat/*`, `fix/*`, `docs/*`)
2. **Ensure quality** by running build and static checks before submission
3. **Clear descriptions** in PRs about motivation, implementation, and impact scope
4. **Follow conventions** outlined in this README and CLAUDE.md

### Development Guidelines
1. **Environment setup**: Run `make dev-setup` for first-time development
2. **Code submission**: Use provided Git hooks to ensure code quality
3. **Branch management**: Strictly follow branch naming conventions
4. **Testing**: Run `make check` before each commit to ensure code quality
5. **Documentation**: Update relevant documentation for significant changes

## Troubleshooting

### Common Issues
- **Port conflicts**: Modify backend `server.port` or frontend Vite port
- **Storage unavailable**: Ensure MinIO/Redis services are started and network accessible
- **Build failures**: Check JDK/Maven/Node versions meet requirements, clean cache and retry

### Getting Help
- Check documentation in `docs/` directory
- Review `Makefile-readme.md` for build system usage
- Create issues for bug reports or feature requests

## License

This project follows the open source license described in the `LICENSE` file in the repository root directory.

## Acknowledgments

Thanks to all developers and community partners who contribute code, documentation, and feedback to the Astra Agent ecosystem.

---

*Built with ❤️ by the Astra Agent community*
