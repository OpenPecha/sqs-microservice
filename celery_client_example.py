"""
Celery Client - Use this on your other server to send tasks to the Celery worker
No need for FastAPI endpoint!
"""

from celery import Celery
import os

class CeleryTaskClient:
    def __init__(self, broker_url: str, backend_url: str):
        """
        Initialize Celery client to send tasks to remote worker
        
        Args:
            broker_url: Redis URL from Render (e.g., redis://red-xxx:6379)
            backend_url: Same as broker_url for Render Redis
        """
        self.celery_app = Celery(
            'async_worker',
            broker=broker_url,
            backend=backend_url
        )
    
    def process_segment_task(
        self, 
        job_id: str,
        manifestation_id: str,
        segment_id: str,
        start: int,
        end: int,
        async_mode: bool = True
    ):
        """
        Send a segment processing task to the remote Celery worker
        
        Args:
            job_id: Unique job identifier
            manifestation_id: Manifestation ID to process
            segment_id: Segment ID to process
            start: Start position
            end: End position
            async_mode: If True, returns immediately. If False, waits for result.
        
        Returns:
            AsyncResult object if async_mode=True, or the actual result if async_mode=False
        """
        result = self.celery_app.send_task(
            'process_segment_task',
            kwargs={
                'job_id': job_id,
                'manifestation_id': manifestation_id,
                'segment_id': segment_id,
                'start': start,
                'end': end
            }
        )
        
        if async_mode:
            print(f"Task sent! Task ID: {result.id}")
            return result
        else:
            print(f"Waiting for result... Task ID: {result.id}")
            return result.get(timeout=300)  # Wait up to 5 minutes
    
    def add_numbers(self, x: int, y: int):
        """Example: Send simple add task"""
        result = self.celery_app.send_task(
            'app.tasks.add_numbers',
            args=[x, y]
        )
        return result.get(timeout=10)
    
    def check_task_status(self, task_id: str):
        """Check status of a previously submitted task"""
        result = self.celery_app.AsyncResult(task_id)
        return {
            'task_id': task_id,
            'status': result.status,
            'ready': result.ready(),
            'successful': result.successful() if result.ready() else None,
            'result': result.result if result.ready() else None
        }


# Example usage
if __name__ == "__main__":
    # Get Redis URL from environment or Render dashboard
    BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379')
    
    # Initialize client
    client = CeleryTaskClient(
        broker_url=BROKER_URL,
        backend_url=BROKER_URL
    )
    
    # Example 1: Send task asynchronously (fire and forget)
    result = client.process_segment_task(
        job_id='test-job-123',
        manifestation_id='7rKyIQZvdaJcPSf8UDPFo',
        segment_id='Camk93lR3mTxe8kl1T3Jv',
        start=0,
        end=16,
        async_mode=True
    )
    print(f"Task submitted with ID: {result.id}")
    
    # Example 2: Send task and wait for result
    # result = client.process_segment_task(
    #     job_id='test-job-456',
    #     manifestation_id='7rKyIQZvdaJcPSf8UDPFo',
    #     segment_id='Camk93lR3mTxe8kl1T3Jv',
    #     start=0,
    #     end=16,
    #     async_mode=False
    # )
    # print(f"Task result: {result}")
    
    # Example 3: Check task status later
    # status = client.check_task_status(result.id)
    # print(f"Task status: {status}")

