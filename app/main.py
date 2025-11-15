from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import threading
from app.relation import relation
from app.config import get

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.sqs_service import consumer

consumer_thread = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI.
    Runs startup and shutdown logic.
    """
    # Startup: Start SQS consumer in background thread
    logger.info("🚀 Starting SQS consumer in background thread...")
    global consumer_thread
    consumer_thread = threading.Thread(
        target=consumer.start,
        daemon=True,  # Thread will exit when main program exits
        name="SQSConsumerThread"
    )
    consumer_thread.start()
    logger.info("✅ SQS consumer thread started")
    
    yield  # Application runs here
    
    # Shutdown: Clean up (optional)
    logger.info("🛑 Shutting down SQS consumer...")
    # Note: daemon threads are automatically terminated on shutdown

app = FastAPI(
    title="async_worker",
    description="SQS worker service for OpenPecha segment processing",
    version="1.0.0",
    lifespan=lifespan  # Register the lifespan handler
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "service": "async_worker",
        "version": "1.0.0",
        "status": "running",
        "sqs_consumer": "active" if consumer_thread and consumer_thread.is_alive() else "inactive"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "sqs_consumer_running": consumer_thread.is_alive() if consumer_thread else False
    }

app.include_router(relation)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=8080, reload=True)