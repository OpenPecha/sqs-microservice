# Deployment Guide for Render

## Prerequisites

1. A Render account (https://render.com)
2. Git repository with your code
3. Neo4j AuraDB instance

## Deployment Steps

### Option 1: Deploy using render.yaml (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Add Docker and Render configuration"
   git push origin main
   ```

2. **Create a New Blueprint on Render**
   - Go to https://dashboard.render.com/blueprints
   - Click "New Blueprint Instance"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Set Environment Variables**
   After creation, set these environment variables in Render Dashboard:
   - `NEO4J_URI`: Your Neo4j connection URI (e.g., `neo4j+s://xxx.databases.neo4j.io`)
   - `NEO4J_PASSWORD`: Your Neo4j password

4. **Deploy**
   - Render will automatically deploy all services
   - Wait for all services to become "Live"

### Option 2: Manual Deployment

#### 1. Deploy PostgreSQL
- Go to Render Dashboard → New → PostgreSQL
- Name: `celery-postgres`
- Database: `pecha`
- User: `admin`
- Copy the connection string

#### 2. Deploy Redis
- Go to Render Dashboard → New → Redis
- Name: `celery-redis`
- Plan: Free
- Copy the connection string

#### 3. Deploy FastAPI Web Service
- Go to Render Dashboard → New → Web Service
- Connect your repository
- Name: `celery-fastapi`
- Environment: Docker
- Dockerfile path: `./Dockerfile`
- Set environment variables:
  ```
  NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
  NEO4J_PASSWORD=your_password
  POSTGRES_URL=<from PostgreSQL service>
  CELERY_BROKER_URL=<from Redis service>
  CELERY_RESULT_BACKEND=<from Redis service>
  ```

#### 4. Deploy Celery Worker
- Go to Render Dashboard → New → Background Worker
- Connect your repository
- Name: `celery-worker`
- Environment: Docker
- Dockerfile path: `./Dockerfile.worker`
- Set the same environment variables as FastAPI

## Testing Your Deployment

Once deployed, test your API:

```bash
# Health check
curl https://your-app.onrender.com/health

# Create a job
curl -X POST https://your-app.onrender.com/relation/segments \
  -H "Content-Type: application/json" \
  -d '{
    "manifestation_id": "7rKyIQZvdaJcPSf8UDPFo",
    "segments": [
      {
        "segment_id": "Camk93lR3mTxe8kl1T3Jv",
        "span": {"start": 0, "end": 16}
      }
    ]
  }'

# Check job status
curl https://your-app.onrender.com/relation/{job_id}/status
```

## Run Migrations

After deployment, run Alembic migrations:

```bash
# SSH into your web service or run via Render Shell
alembic upgrade head
```

## Monitoring

- View logs in Render Dashboard
- Monitor Celery worker logs
- Check metrics and health status

## Troubleshooting

### Worker can't connect to Neo4j
- Verify `NEO4J_URI` and `NEO4J_PASSWORD` are set correctly
- Check Neo4j AuraDB allows connections from Render IPs

### Database connection errors
- Verify `POSTGRES_URL` is correct
- Run migrations with `alembic upgrade head`

### Redis connection errors
- Verify `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` are correct
- Check Redis service is running

## Free Tier Limitations

Render Free tier includes:
- Web services spin down after 15 minutes of inactivity
- 750 hours/month of runtime
- Background workers run 24/7 but use shared resources

Consider upgrading for production workloads.

