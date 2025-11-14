# Deploy Celery Worker Only - Quick Guide

Deploy your Celery worker to Render in 5 minutes!

## What Gets Deployed

✅ **Celery Worker** - Processes tasks in the background
✅ **Redis** - Message broker (tasks queue)
✅ **PostgreSQL** - Stores job results

❌ **No FastAPI** - No HTTP endpoint needed!

## Step 1: Prepare Environment Variables

**IMPORTANT**: Before deploying, gather these credentials:

```bash
# Neo4j Credentials (from Neo4j Aura Dashboard)
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# You can test locally first with .env file
cp env.example .env
# Edit .env with your values
```

## Step 2: Test Docker Image Locally (Optional)

```bash
# Build
docker build -f Dockerfile.worker -t celery-worker .

# Test run (loads from .env or set directly)
docker run --env-file .env celery-worker

# Or set env vars directly:
docker run \
  -e NEO4J_URI="neo4j+s://xxx.databases.neo4j.io" \
  -e NEO4J_USER="neo4j" \
  -e NEO4J_PASSWORD="your_password" \
  -e POSTGRES_URL="postgresql://user:pass@host:5432/db" \
  -e CELERY_BROKER_URL="redis://localhost:6379" \
  -e CELERY_RESULT_BACKEND="redis://localhost:6379" \
  celery-worker
```

## Step 3: Push to GitHub

```bash
git add Dockerfile.worker app/ requirements.txt
git commit -m "Add Celery worker for Render deployment"
git push origin main
```

## Step 4: Deploy to Render

### Option A: Manual Deployment (Easiest)

1. **Create PostgreSQL Database**
   - Go to https://dashboard.render.com
   - Click "New +" → "PostgreSQL"
   - Name: `celery-postgres`
   - Database: `pecha`
   - Plan: Free
   - Click "Create Database"
   - **Copy the Internal Connection String**

2. **Create Redis**
   - Click "New +" → "Redis"
   - Name: `celery-redis`
   - Plan: Free (25 MB)
   - Click "Create Redis"
   - **Copy the Connection String**

3. **Create Worker Service**
   - Click "New +" → "Background Worker"
   - Connect your GitHub repository
   - Settings:
     - **Name**: `celery-worker`
     - **Region**: Oregon (or closest to you)
     - **Branch**: `main`
     - **Root Directory**: Leave empty
     - **Dockerfile Path**: `./Dockerfile.worker`
     - **Plan**: Free
   
4. **Set Environment Variables** (in the worker settings):
   ```
   NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_neo4j_password
   POSTGRES_URL=<paste from step 1>
   CELERY_BROKER_URL=<paste from step 2>
   CELERY_RESULT_BACKEND=<paste from step 2>
   ```
   
   **⚠️ CRITICAL**: Make sure to set your actual Neo4j credentials here!

5. **Click "Create Background Worker"**

### Option B: Using Blueprint (Automated)

Use the `render-worker-only.yaml` file:

1. Go to https://dashboard.render.com/blueprints
2. Click "New Blueprint Instance"
3. Connect your repository
4. Select `render-worker-only.yaml`
5. Set `NEO4J_URI` and `NEO4J_PASSWORD`
6. Click "Apply"

## Step 5: Verify Deployment

### Check Worker Logs
1. Go to Render Dashboard → Background Workers → `celery-worker`
2. Click "Logs" tab
3. You should see:
   ```
   [INFO] celery@... ready.
   [INFO] Connected to redis://...
   ```

### Send a Test Task

From your other server:

```python
from celery import Celery

# Use Redis URL from Render
celery_app = Celery(
    'async_worker',
    broker='redis://red-xxx:6379',  # Your Redis URL
    backend='redis://red-xxx:6379'
)

# Send test task
result = celery_app.send_task(
    'app.tasks.add_numbers',
    args=[5, 3]
)

print(f"Task ID: {result.id}")
print(f"Result: {result.get(timeout=30)}")  # Should print 8
```

## Step 6: Run Database Migrations

If this is the first deployment, create database tables:

```bash
# Option 1: In Render Shell (click "Shell" tab in worker service)
cd /app
alembic upgrade head

# Option 2: Use one-off job
# In Render Dashboard → Worker → Manual Deploy → Shell
# Then run: alembic upgrade head
```

## Step 7: Get Redis URL for Your Other Server

1. Go to Render Dashboard → Redis → `celery-redis`
2. Click "Info" tab
3. Copy "**External Connection String**"
4. Use this in your other server's code

Example:
```
redis://red-abc123xyz:6379
```

## Configuration Options

### Increase Concurrency (Paid Plans)

Edit `Dockerfile.worker`, change:
```dockerfile
CMD ["celery", "-A", "app.tasks", "worker", \
     "--loglevel=info", \
     "--pool=prefork", \      # Change from solo
     "--concurrency=4"]       # Process 4 tasks simultaneously
```

### Auto-scale Workers

```dockerfile
CMD ["celery", "-A", "app.tasks", "worker", \
     "--loglevel=info", \
     "--autoscale=10,2"]      # Min 2, max 10 workers
```

### Enable Task Events (for monitoring)

```dockerfile
CMD ["celery", "-A", "app.tasks", "worker", \
     "--loglevel=info", \
     "--pool=solo", \
     "--events"]              # Enable events for Flower
```

## Monitoring

### View Logs
```bash
# In Render Dashboard
Services → celery-worker → Logs
```

### Check Queue Size
```python
from celery import Celery
celery_app = Celery(broker='redis://red-xxx:6379')
inspect = celery_app.control.inspect()

print(f"Active tasks: {inspect.active()}")
print(f"Scheduled: {inspect.scheduled()}")
```

### Deploy Flower (Optional Monitoring UI)

Add to your services:
```yaml
# In render.yaml
- type: web
  name: celery-flower
  env: docker
  dockerCommand: celery -A app.tasks flower --port=5555
  envVars:
    - key: CELERY_BROKER_URL
      fromService:
        type: redis
        name: celery-redis
```

## Troubleshooting

### Worker shows "Connection refused"
- Check Redis URL is correct
- Verify Redis service is running
- Check environment variables are set

### Tasks not being processed
- Check worker logs for errors
- Verify task name matches: `process_segment_task`
- Check Neo4j credentials are correct

### Out of memory errors
- Reduce concurrency to 1
- Use `--max-tasks-per-child=100` to restart workers
- Upgrade to paid plan for more RAM

### Slow performance
- Check Neo4j connection latency
- Upgrade Redis plan for better performance
- Increase worker concurrency (paid plan)

## Cost Breakdown (Free Tier)

- **Worker**: Free (512 MB RAM, shared CPU)
- **Redis**: Free (25 MB storage)
- **PostgreSQL**: Free (1 GB storage)
- **Total**: **$0/month** ✨

## Scaling to Paid (When Needed)

- **Worker**: $7/month (512 MB) → $21/month (2 GB)
- **Redis**: $10/month (1 GB)
- **PostgreSQL**: $7/month (1 GB) → $20/month (10 GB)

## What's Next?

1. ✅ Worker deployed and running
2. ✅ Redis accessible externally
3. ✅ PostgreSQL storing results
4. **→ Copy `celery_client_example.py` to your other server**
5. **→ Start sending tasks!**

Example from your other server:
```python
from celery import Celery

client = Celery(
    'async_worker',
    broker='redis://red-YOUR-ID:6379',  # From Render
    backend='redis://red-YOUR-ID:6379'
)

# Send task
result = client.send_task('process_segment_task', kwargs={
    'job_id': 'test-1',
    'manifestation_id': '7rKyIQZvdaJcPSf8UDPFo',
    'segment_id': 'segment-1',
    'start': 0,
    'end': 16
})

print(f"✅ Task sent! ID: {result.id}")
```

Happy deploying! 🚀

