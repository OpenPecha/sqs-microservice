# Deploy to Render - Quick Guide

This guide shows how to deploy your FastAPI + Celery application to Render manually from your GitHub repository.

## Architecture

Your application consists of two services that share the same Docker image:
1. **Web Service** - FastAPI server that receives requests and dispatches Celery tasks
2. **Background Worker** - Celery worker that processes tasks from Redis queue

## Prerequisites

- GitHub repository pushed with your code
- Render account (free tier works)
- Neo4j database (Aura or self-hosted)
- PostgreSQL database (will be created in Render)
- Redis instance (will be created in Render)

## Deployment Steps

### Step 1: Create PostgreSQL Database

1. Go to Render Dashboard
2. Click **New +** → **PostgreSQL**
3. Configure:
   - **Name**: `celery-postgres` (or your choice)
   - **Region**: Choose closest to your users
   - **Plan**: Free
4. Click **Create Database**
5. Wait for it to be ready
6. Copy the **Internal Database URL** (starts with `postgresql://`)

### Step 2: Create Redis Instance

1. Click **New +** → **Redis**
2. Configure:
   - **Name**: `celery-redis` (or your choice)
   - **Region**: Same as PostgreSQL
   - **Plan**: Free
   - **Maxmemory Policy**: `noeviction`
3. Click **Create Redis**
4. Wait for it to be ready
5. Copy the **Internal Redis URL** (starts with `redis://`)

### Step 3: Deploy Web Service (FastAPI)

1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `celery-web`
   - **Region**: Same as database
   - **Branch**: `main` (or your default branch)
   - **Runtime**: Docker
   - **Plan**: Free
   - **Docker Command**: Leave empty (uses default from Dockerfile)

4. **Environment Variables** - Add these:
   ```
   CELERY_BROKER_URL=<your-redis-internal-url>
   CELERY_RESULT_BACKEND=<your-redis-internal-url>
   POSTGRES_URL=<your-postgres-internal-url>
   NEO4J_URI=<your-neo4j-uri>
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=<your-neo4j-password>
   ```

5. Click **Create Web Service**
6. Wait for deployment to complete
7. Test by visiting: `https://your-service.onrender.com/health`

### Step 4: Deploy Background Worker (Celery)

1. Click **New +** → **Background Worker**
2. Connect the same GitHub repository
3. Configure:
   - **Name**: `celery-worker`
   - **Region**: Same as other services
   - **Branch**: `main`
   - **Runtime**: Docker
   - **Plan**: Free
   - **Docker Command**: 
     ```
     celery -A app.tasks worker --loglevel=info --pool=solo --concurrency=1
     ```

4. **Environment Variables** - Add the same variables as Web Service:
   ```
   CELERY_BROKER_URL=<your-redis-internal-url>
   CELERY_RESULT_BACKEND=<your-redis-internal-url>
   POSTGRES_URL=<your-postgres-internal-url>
   NEO4J_URI=<your-neo4j-uri>
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=<your-neo4j-password>
   C_FORCE_ROOT=1
   ```

5. Click **Create Background Worker**
6. Monitor logs to ensure worker connects successfully

### Step 5: Run Database Migrations

1. Go to your **Web Service** in Render
2. Click **Shell** tab
3. Run migrations:
   ```bash
   cd app
   alembic upgrade head
   ```

## Testing the Deployment

1. Get your web service URL from Render dashboard
2. Test the health endpoint:
   ```bash
   curl https://your-service.onrender.com/health
   ```

3. Send a test job:
   ```bash
   curl -X POST https://your-service.onrender.com/segments \
     -H "Content-Type: application/json" \
     -d '{
       "manifestation_id": "your-test-id",
       "segments": [
         {
           "segment_id": "segment-1",
           "span": {"start": 0, "end": 10}
         }
       ]
     }'
   ```

4. Check worker logs in Render to see task processing

## Important Notes

### Redis URL Format
- Use **Internal Redis URL** for both services (faster, no egress fees)
- Format: `redis://red-xxxxx:6379` (internal)
- External URL format: `rediss://red-xxxxx@location.keyvalue.render.com:6379`

### Free Tier Limitations
- Services sleep after 15 minutes of inactivity
- First request after sleep takes ~30-60 seconds to wake up
- Background workers don't sleep (they stay active)

### Updating Code
Render auto-deploys when you push to your connected branch:
```bash
git add .
git commit -m "Update code"
git push origin main
```

Both services will rebuild automatically.

### Viewing Logs
- Go to each service in Render dashboard
- Click **Logs** tab
- Real-time logs show requests, task processing, errors

### Environment Variables
To update environment variables:
1. Go to service in Render
2. Click **Environment** in left sidebar
3. Update values
4. Service will automatically restart

## Troubleshooting

### Worker not picking up tasks
- Check both services use the **same Redis URL**
- Verify worker logs show "Connected to redis://..."
- Ensure environment variables are set correctly

### Database connection errors
- Use **Internal Database URL**, not external
- Verify POSTGRES_URL is set in both services
- Check PostgreSQL is in same region

### Neo4j connection errors
- Verify NEO4J_URI format: `neo4j+s://xxxxx.databases.neo4j.io`
- Check NEO4J_USER is `neo4j` (not email)
- Verify password is correct

## Local Development

Use docker-compose for local testing:

```bash
# Set environment variables in .env file
cp env.example .env
# Edit .env with your values

# Start services
docker-compose up --build

# Access FastAPI at http://localhost:8080
```

## Support

For issues, check:
1. Render service logs
2. Worker logs for Celery errors
3. Web service logs for API errors
4. Environment variables are correct

