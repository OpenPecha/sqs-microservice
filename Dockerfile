# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    C_FORCE_ROOT=1

# Expose port for FastAPI (only used by web service)
EXPOSE 8080

# Default command runs FastAPI web service
# Override this in Render or docker-compose for worker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
