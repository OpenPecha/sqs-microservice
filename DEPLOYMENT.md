# Deployment Guide

This guide covers deploying the FastAPI microservice with SQS consumer to various platforms.

## 🏗️ Architecture

The application is a FastAPI server that:
- Exposes REST API endpoints for segment relations
- Runs an SQS consumer in a background thread
- Processes messages from AWS SQS queue
- Stores results in PostgreSQL and Neo4j databases

## 📋 Prerequisites

- Docker installed (for containerized deployment)
- AWS account with SQS queue configured
- PostgreSQL database
- Neo4j database (Aura or self-hosted)

## 🔧 Environment Variables

Copy `env.example` to `.env` and configure:

```bash
cp env.example .env
```

### Required Variables

```bash
# Database
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_PASSWORD=your-password
POSTGRES_URL=postgresql://user:pass@host:5432/dbname

# AWS SQS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
SQS_QUEUE_URL=https://sqs.region.amazonaws.com/account/queue-name
```

## 🐳 Docker Deployment

### Local Development

```bash
# Build and run with docker-compose
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

### Production Build

```bash
# Build production image
docker build -t celery-microservice:latest .

# Run with environment variables
docker run -d \
  --name fastapi-app \
  -p 8080:8080 \
  --env-file .env \
  celery-microservice:latest
```

## ☁️ Cloud Deployment

### Deploy to Render

1. **Create Web Service**:
   - Connect your GitHub repository
   - Set Docker as runtime
   - Dockerfile will be auto-detected

2. **Configure Environment Variables** in Render Dashboard:
   ```
   NEO4J_URI
   NEO4J_PASSWORD
   POSTGRES_URL
   AWS_REGION
   AWS_ACCESS_KEY_ID
   AWS_SECRET_ACCESS_KEY
   SQS_QUEUE_URL
   ```

3. **Set Health Check**:
   - Path: `/health`
   - Port: `8080`

### Deploy to AWS ECS

1. **Push Image to ECR**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   docker tag celery-microservice:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/celery-microservice:latest
   
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/celery-microservice:latest
   ```

2. **Create ECS Task Definition**:
   - Image: Your ECR image URI
   - Port: 8080
   - Environment variables: Add all required vars
   - Task role: Ensure it has SQS permissions

3. **Create ECS Service**:
   - Use the task definition
   - Configure load balancer (optional)
   - Set desired count to 1+

### Deploy to Railway

1. **Create New Project**:
   - Connect GitHub repository
   - Railway auto-detects Dockerfile

2. **Add Environment Variables**:
   - Add all required variables in Railway dashboard

3. **Deploy**:
   - Automatic deployment on push

### Deploy to Google Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/celery-microservice

# Deploy to Cloud Run
gcloud run deploy celery-microservice \
  --image gcr.io/PROJECT_ID/celery-microservice \
  --platform managed \
  --region us-central1 \
  --port 8080 \
  --set-env-vars "NEO4J_URI=...,NEO4J_PASSWORD=...,POSTGRES_URL=...,AWS_REGION=...,AWS_ACCESS_KEY_ID=...,AWS_SECRET_ACCESS_KEY=...,SQS_QUEUE_URL=..."
```

## 🔍 Health Checks

The application provides health check endpoints:

- **Basic Health**: `GET /health`
  ```json
  {
    "status": "healthy",
    "sqs_consumer_running": true
  }
  ```

- **Root Endpoint**: `GET /`
  ```json
  {
    "service": "async_worker",
    "version": "1.0.0",
    "status": "running",
    "sqs_consumer": "active"
  }
  ```

## 📊 Monitoring

### View Logs

**Docker Compose**:
```bash
docker-compose logs -f web
```

**Docker**:
```bash
docker logs -f fastapi-app
```

**Cloud Platforms**:
- Render: View logs in dashboard
- AWS ECS: CloudWatch Logs
- Railway: Built-in logs viewer
- GCP Cloud Run: Cloud Logging

### Metrics to Monitor

- SQS consumer status (check `/health` endpoint)
- Message processing rate
- Database connection health
- Memory and CPU usage
- Error rates in logs

## 🔐 Security Considerations

1. **Never commit `.env` file** - Use environment variables in production
2. **Use IAM roles** when deploying to AWS (instead of access keys)
3. **Rotate AWS credentials** regularly
4. **Use secrets management**:
   - AWS Secrets Manager
   - Railway/Render secret management
   - Kubernetes secrets

## 🐛 Troubleshooting

### SQS Consumer Not Running

Check logs for:
```bash
"🚀 Starting SQS consumer in background thread..."
"✅ SQS consumer thread started"
```

If not present, verify:
- AWS credentials are correct
- SQS queue URL is valid
- IAM permissions include `sqs:ReceiveMessage`, `sqs:DeleteMessage`

### Database Connection Issues

- Verify `POSTGRES_URL` and `NEO4J_URI` are correct
- Check network connectivity
- Ensure databases are accessible from deployment environment

### Container Fails Health Check

- Ensure port 8080 is exposed
- Check if application is listening on `0.0.0.0`
- Verify `/health` endpoint returns 200 OK

## 📦 Scaling

The application can be scaled horizontally:

```bash
# Docker Compose
docker-compose up --scale web=3

# Kubernetes
kubectl scale deployment celery-microservice --replicas=3
```

**Note**: Multiple instances will consume from the same SQS queue, providing parallel processing.

## 🚀 CI/CD Pipeline Example

### GitHub Actions

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -t celery-microservice .
      
      - name: Push to registry
        run: |
          # Push to your container registry
          
      - name: Deploy
        run: |
          # Trigger deployment to your platform
```

## 📝 Environment-Specific Configs

### Development
- Enable hot reload (`--reload` flag in docker-compose)
- Verbose logging (`LOG_LEVEL=DEBUG`)
- Local databases

### Production
- Disable reload
- Set `LOG_LEVEL=INFO`
- Use managed databases (RDS, Neo4j Aura)
- Enable health checks
- Set up monitoring and alerts

## 🆘 Support

For issues or questions:
1. Check application logs
2. Verify environment variables
3. Test database connectivity
4. Check AWS SQS queue status

