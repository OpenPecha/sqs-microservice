import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

Config = {
    "CELERY_BROKER_URL": os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379'),
    "CELERY_RESULT_BACKEND": os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379'),
    "NEO4J_URI": os.getenv('NEO4J_URI', None),
    "NEO4J_USER": os.getenv('NEO4J_USER', None),
    "NEO4J_PASSWORD": os.getenv('NEO4J_PASSWORD', None),
    "POSTGRES_URL": os.getenv('POSTGRES_URL', 'postgresql://admin:pechaAdmin@localhost:5435/pecha'),
}


def get(key: str, default=None):
    return Config.get(key, default)