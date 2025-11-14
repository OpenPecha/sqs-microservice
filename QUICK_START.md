# 🚀 Quick Start: Deploy Celery Worker to Render

## What You'll Need (5 minutes to gather)

### 1. Neo4j Credentials
Go to your Neo4j Aura Console and get:
- ✅ **URI**: `neo4j+s://xxxxx.databases.neo4j.io`
- ✅ **Username**: Usually `neo4j`
- ✅ **Password**: Your Neo4j password

### 2. GitHub Repository
- Push your code to GitHub (any branch, but `main` is easiest)

## Deploy in 3 Steps

### Step 1: Deploy to Render (Using Blueprint)

1. Go to https://dashboard.render.com/blueprints
2. Click **"New Blueprint Instance"**
3. Connect your GitHub repository
4. Select the `render-worker-only.yaml` file
5. **When prompted, enter**:
   - `NEO4J_URI`: Your Neo4j URI from above
   - `NEO4J_PASSWORD`: Your Neo4j password
6. Click **"Apply"**

That's it! Render will:
- ✅ Create PostgreSQL database
- ✅ Create Redis instance
- ✅ Deploy your Celery worker
- ✅ Auto-configure everything

### Step 2: Get Redis URL

1. Go to Render Dashboard → **Redis** → `celery-redis`
2. Click **"Info"** tab
3. Copy the **"External Connection String"**
4. It looks like: `redis://red-abc123xyz:6379`

### Step 3: Send Tasks from Your Server

On your other server:

```bash
pip install celery redis
```

```python
from celery import Celery

# Use the Redis URL from Step 2
celery_app = Celery(
    'async_worker',
    broker='redis://red-abc123xyz:6379',  # Your Redis URL
    backend='redis://red-abc123xyz:6379'
)

# Send a task
result = celery_app.send_task(
    'process_segment_task',
    kwargs={
        'job_id': 'test-job-1',
        'manifestation_id': '7rKyIQZvdaJcPSf8UDPFo',
        'segment_id': 'Camk93lR3mTxe8kl1T3Jv',
        'start': 0,
        'end': 16
    }
)

print(f"✅ Task sent! ID: {result.id}")

# Optional: Wait for result
# result_data = result.get(timeout=300)
# print(f"Result: {result_data}")
```

## That's It! 🎉

Your architecture:

```
Your Server → Redis (Render) → Celery Worker (Render) → Neo4j + PostgreSQL
```

## Verify It's Working

Check worker logs:
1. Render Dashboard → Background Workers → `celery-worker`
2. Click "Logs"
3. Look for: `✅ [INFO] celery@... ready.`

## Environment Variables Recap

The worker needs these (auto-configured via `render-worker-only.yaml`):

| Variable | Source | Notes |
|----------|--------|-------|
| `NEO4J_URI` | You provide | During deployment |
| `NEO4J_USER` | Auto-set to `neo4j` | Can override if needed |
| `NEO4J_PASSWORD` | You provide | During deployment |
| `POSTGRES_URL` | Auto-configured | From Render PostgreSQL |
| `CELERY_BROKER_URL` | Auto-configured | From Render Redis |
| `CELERY_RESULT_BACKEND` | Auto-configured | From Render Redis |

## Troubleshooting

### "Connection refused" in logs
- Check Neo4j credentials are correct
- Make sure Neo4j URI is accessible (check firewall)

### Tasks not being received
- Verify Redis URL is correct in your client
- Check task name is exactly `'process_segment_task'`

### Worker crashes on startup
- Check logs for the specific error
- Usually Neo4j or PostgreSQL connection issue

## Cost

**Free Tier**: Everything you need
- Worker: Free (512 MB RAM)
- Redis: Free (25 MB)
- PostgreSQL: Free (1 GB)

**Total: $0/month** 💰

## Next Steps

See full guide: `DEPLOY_WORKER.md`
Client examples: `celery_client_example.py`
Environment setup: `env.example`

---

**Questions?** Check the logs in Render Dashboard first, they usually tell you exactly what's wrong!

