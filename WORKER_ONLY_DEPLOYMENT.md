# Worker-Only Deployment Guide

Deploy ONLY the Celery worker to Render and trigger tasks from any other server.

## Architecture

```
Your Server → Redis (Render) → Celery Worker (Render) → Neo4j + PostgreSQL
```

No FastAPI endpoint needed! Your server sends tasks directly to Redis.

## Step 1: Deploy to Render

### 1. Push code to GitHub
```bash
git add .
git commit -m "Add worker-only deployment"
git push origin main
```

### 2. Deploy using render-worker-only.yaml
- Go to https://dashboard.render.com/blueprints
- Click "New Blueprint Instance"
- Connect your repository
- Select `render-worker-only.yaml`
- Set environment variables:
  - `NEO4J_URI`
  - `NEO4J_PASSWORD`
- Click "Apply"

### 3. Get Redis Connection String
After deployment:
- Go to your Redis service in Render Dashboard
- Copy the "External Connection String"
- It looks like: `redis://red-xxx:6379`
- **Important:** This is publicly accessible but secured by Render

## Step 2: Use from Your Other Server

### Option A: Python Client (Recommended)

1. **Install dependencies on your server:**
```bash
pip install celery redis
```

2. **Use the client:**
```python
from celery import Celery

# Use the Redis URL from Render
celery_app = Celery(
    'async_worker',
    broker='redis://red-xxx:6379',  # From Render
    backend='redis://red-xxx:6379'
)

# Send task
result = celery_app.send_task(
    'process_segment_task',
    kwargs={
        'job_id': 'my-job-123',
        'manifestation_id': '7rKyIQZvdaJcPSf8UDPFo',
        'segment_id': 'Camk93lR3mTxe8kl1T3Jv',
        'start': 0,
        'end': 16
    }
)

print(f"Task ID: {result.id}")

# Optional: Wait for result
result_data = result.get(timeout=300)
print(f"Result: {result_data}")
```

3. **Copy `celery_client_example.py` to your server** for a ready-to-use client!

### Option B: Node.js Client

```javascript
const redis = require('redis');
const { v4: uuidv4 } = require('uuid');

const client = redis.createClient({
  url: 'redis://red-xxx:6379'  // From Render
});

await client.connect();

// Send task
const taskMessage = {
  id: uuidv4(),
  task: 'process_segment_task',
  args: [],
  kwargs: {
    job_id: 'my-job-123',
    manifestation_id: '7rKyIQZvdaJcPSf8UDPFo',
    segment_id: 'Camk93lR3mTxe8kl1T3Jv',
    start: 0,
    end: 16
  },
  retries: 0
};

await client.lPush('celery', JSON.stringify(taskMessage));
console.log(`Task sent: ${taskMessage.id}`);
```

### Option C: REST API (If you still want HTTP)

If you need HTTP access from non-Python services, you can:
1. Keep the FastAPI endpoint as a thin proxy
2. Or build a simple task gateway service

## Step 3: Check Task Results

### From your server (Python):
```python
from celery import Celery

celery_app = Celery(broker='redis://red-xxx:6379')

# Check task status
result = celery_app.AsyncResult('task-id-here')
print(f"Status: {result.status}")
print(f"Result: {result.result if result.ready() else 'Not ready'}")
```

### Query PostgreSQL directly:
```python
import psycopg2

conn = psycopg2.connect("postgresql://...")
cursor = conn.cursor()

# Check job status
cursor.execute(
    "SELECT * FROM root_jobs WHERE job_id = %s",
    ('my-job-123',)
)
print(cursor.fetchone())

# Check segment tasks
cursor.execute(
    "SELECT * FROM segment_tasks WHERE job_id = %s",
    ('my-job-123',)
)
print(cursor.fetchall())
```

## Advantages of Worker-Only Deployment

✅ **Simpler**: No web server, just background workers
✅ **More secure**: No public HTTP endpoint
✅ **Direct**: Lower latency, no HTTP overhead
✅ **Flexible**: Call from any language/platform
✅ **Scalable**: Easy to add more workers

## Security Considerations

1. **Redis URL is public** - Anyone with the URL can send tasks
   - Solution: Use Render's private networking (paid plan)
   - Or: Implement authentication in your tasks
   - Or: Use VPN/SSH tunnel

2. **Rate limiting** - No built-in rate limiting without FastAPI
   - Solution: Implement rate limiting in your client
   - Or: Add a lightweight API gateway

3. **Input validation** - Tasks receive raw data
   - Solution: Validate in Celery tasks (already done in your code)

## Monitoring

### View worker logs:
```bash
# In Render Dashboard → Services → celery-worker → Logs
```

### Check task queue size:
```python
from celery import Celery
celery_app = Celery(broker='redis://red-xxx:6379')
inspect = celery_app.control.inspect()

print(inspect.active())      # Currently running tasks
print(inspect.scheduled())   # Scheduled tasks
print(inspect.reserved())    # Reserved tasks
```

## Cost Comparison

### Worker-Only (This approach):
- Redis: Free (25 MB)
- PostgreSQL: Free (1 GB)
- Worker: Free (512 MB RAM)
- **Total: $0/month**

### With FastAPI Endpoint:
- Add Web Service: Free (512 MB RAM)
- But sleeps after 15 min inactivity
- **Total: Still $0/month** (but slower cold starts)

## When to Use Worker-Only vs. with API

### Use Worker-Only when:
- ✅ Your other server is Python-based
- ✅ You need low latency
- ✅ You have direct network access to Render
- ✅ You don't need public HTTP access

### Use with FastAPI when:
- ✅ Need HTTP/REST interface
- ✅ Calling from browsers/mobile apps
- ✅ Need authentication/authorization
- ✅ Need input validation before queuing
- ✅ Calling from non-Python services

## Example: Full Integration

```python
# On your application server
from celery_client_example import CeleryTaskClient
import os

# Initialize once (reuse across requests)
celery_client = CeleryTaskClient(
    broker_url=os.getenv('RENDER_REDIS_URL'),
    backend_url=os.getenv('RENDER_REDIS_URL')
)

# In your application code
def process_document(doc_id):
    # Send task to remote Celery worker
    result = celery_client.process_segment_task(
        job_id=f"doc-{doc_id}",
        manifestation_id="7rKyIQZvdaJcPSf8UDPFo",
        segment_id="Camk93lR3mTxe8kl1T3Jv",
        start=0,
        end=16,
        async_mode=True
    )
    
    # Store task ID for later checking
    save_task_id(doc_id, result.id)
    
    return {"status": "processing", "task_id": result.id}

def check_document_status(doc_id):
    task_id = get_task_id(doc_id)
    status = celery_client.check_task_status(task_id)
    return status
```

## Next Steps

1. Deploy worker using `render-worker-only.yaml`
2. Get Redis connection string from Render
3. Copy `celery_client_example.py` to your server
4. Test task submission
5. Monitor worker logs in Render Dashboard

Happy deploying! 🚀

