# astronAgent Project Complete Deployment Guide

This guide will help you start all components of the astronAgent project in the correct order, including identity authentication, knowledge base, and core services.

## 📋 Project Architecture Overview

The astronAgent project consists of three main components:

1. **Casdoor** - Identity authentication and single sign-on service
2. **RagFlow** - Knowledge base and document retrieval service
3. **astronAgent** - Core business service cluster

## 🚀 Deployment Steps

### Prerequisites

**Agent System Requirements**
- CPU >= 2 Core
- RAM >= 4 GiB
- Disk >= 50 GB

**RAGFlow Requirements**
- CPU >= 4 Core
- RAM >= 16 GB
- Disk >= 50 GB

### Step 1: Start Casdoor Identity Authentication Service (Deploy as needed)

Casdoor is an open-source identity and access management platform that supports multiple authentication protocols including OAuth 2.0, OIDC, and SAML.

```bash
# Navigate to Casdoor directory
cd docker/casdoor

# Modify environment configuration
vim conf/app.conf

# Start Casdoor service
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

**Service Information:**
- Access URL: http://localhost:8000
- Container name: casdoor
- Default configuration: Production mode (GIN_MODE=release)

**Configuration directories:**
- Configuration files: `./conf` directory
- Log files: `./logs` directory

### Step 2: Start RagFlow Knowledge Base Service

RagFlow is an open-source RAG (Retrieval-Augmented Generation) engine that uses deep document understanding technology to provide accurate Q&A services.

```bash
# Navigate to RagFlow directory
cd docker/ragflow

# Start RagFlow service (including all dependencies)
docker-compose up -d

# Check service status
docker-compose ps

# View service logs
docker-compose logs -f ragflow
```

**RagFlow Service Components:**
- **ragflow-server**: Main service (port 9380)
- **ragflow-mysql**: MySQL database (port 3306)
- **ragflow-redis**: Redis cache (port 6379)
- **ragflow-minio**: Object storage (port 9000, console 9001)
- **ragflow-es-01** or **ragflow-opensearch-01**: Search engine (port 9200/9201)
- **ragflow-infinity**: Vector database (optional)

**Access URLs:**
- RagFlow Web Interface: http://localhost:9380

**Important Configuration Notes:**
- Uses Elasticsearch by default. To use opensearch、infinity, modify the DOC_ENGINE configuration in .env
- Supports GPU acceleration, use `docker-compose-gpu.yml` to start

### Step 3: Configure astronAgent Core Services

Before starting astronAgent services, configure the relevant connection information to integrate with Casdoor and RagFlow as needed.

#### 3.1 Configure Knowledge Base Service Connection

Edit `docker/astronAgent/.env` file to configure RagFlow connection information:

**Key Configuration Items:**

```env
# RAGFlow Configuration
RAGFLOW_BASE_URL=http://localhost:9380
RAGFLOW_API_TOKEN=ragflow-your-api-token-here
RAGFLOW_TIMEOUT=60
RAGFLOW_DEFAULT_GROUP=Astron Knowledge Base
```

**Getting RagFlow API Token:**
1. Access RagFlow Web Interface: http://localhost:9380
2. Login and go to user settings
3. Generate API Token
4. Update the token in the configuration file

#### 3.2 Configure Casdoor Authentication Integration

Edit `docker/astronAgent/.env` file to configure Casdoor connection information:

**Key Configuration Items:**

```env
# Casdoor Configuration
CONSOLE_CASDOOR_URL=http://your-casdoor-server:8000
CONSOLE_CASDOOR_ID=your-casdoor-client-id
CONSOLE_CASDOOR_APP=your-casdoor-app-name
CONSOLE_CASDOOR_ORG=your-casdoor-org-name
```

**Configure Casdoor authentication integration according to your needs, mainly including:**
1. **OAuth Application Registration**: Register astronAgent application in Casdoor
2. **Callback URL Configuration**: Set correct callback URLs
3. **Permission Configuration**: Configure user roles and permissions
4. **Configuration File Update**

### Step 4: Start astronAgent Core Services

```bash
# Navigate to astronAgent directory
cd docker/astronAgent

# Copy environment configuration
cp .env.example .env

# Modify configuration as needed
vim .env

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View service logs
docker-compose logs -f
```

## 📊 Service Access URLs

After startup is complete, you can access various services through the following URLs:

### Authentication Services
- **Casdoor Management Interface**: http://localhost:8000

### Knowledge Base Services
- **RagFlow Web Interface**: http://localhost:9380

### AstronAgent Core Services
- **Console Frontend (nginx proxy)**: http://localhost:80

### Middleware Services
- **PostgreSQL**: localhost:5432
- **MySQL**: localhost:3306
- **Redis**: localhost:6379
- **Elasticsearch**: http://localhost:9200
- **Kafka**: localhost:9092
- **MinIO**: http://localhost:9000

## 🔍 Troubleshooting

### 1. Service Startup Failure

```bash
# View detailed error logs
docker-compose logs service-name

# Check port usage
netstat -tlnp | grep :port-number

# Check resource usage
docker stats
```

### 2. Inter-service Connection Issues

**Common Issues:**
- Ensure all services are in the same network
- Check service name resolution is correct
- Verify port configuration consistency

**Solutions:**
```bash
# View network configuration
docker network ls
docker network inspect [network-name]

# Test service connectivity
docker exec -it container-name ping target-service-name
```

### 3. Configuration File Issues

**Check configuration file syntax:**
```bash
# Validate docker-compose file
docker-compose config

# Check environment variables
docker-compose config --services
```

### 4. Data Persistence Issues

```bash
# View data volumes
docker volume ls

# Check volume mounting
docker volume inspect volume-name
```

## 📚 Additional Resources

- [AstronAgent Official Documentation](https://docs.astronAgent.cn)
- [Casdoor Official Documentation](https://casdoor.org/docs/overview)
- [RagFlow Official Documentation](https://ragflow.io/docs)
- [Docker Compose Official Documentation](https://docs.docker.com/compose/)

## 🤝 Technical Support

If you encounter problems, please:

1. Check relevant service log files
2. Review official documentation and troubleshooting guides
3. Submit an Issue in the project's GitHub repository
4. Contact the technical support team

---

**Note**: For first-time deployment, it's recommended to validate all functionality in a test environment before deploying to production.