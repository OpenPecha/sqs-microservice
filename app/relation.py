from fastapi import APIRouter, HTTPException

from app.models import SegmentsRelationRequest
from app.db.postgres import SessionLocal
from app.db.models import RootJob, SegmentTask
from datetime import datetime, timezone
from uuid import uuid4
from app.config import get
import json

import boto3

relation = APIRouter(
    prefix="/relation",
    tags=["Segments Relation"]
)

# Initialize SQS client with proper configuration
sqs_client = boto3.client(
    'sqs',
    region_name=get('AWS_REGION'),
    aws_access_key_id=get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=get('AWS_SECRET_ACCESS_KEY')
)

@relation.get("/{job_id}/status")
def get_job_status(job_id: str):
    try:
        with SessionLocal() as session:
            job = session.query(RootJob).filter(RootJob.job_id == job_id).first()
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            
            return job
    except:
        raise HTTPException(status_code=500, detail="Failed to get job status, Database read error")

@relation.post("/segments")
def get_segments_relation(request: SegmentsRelationRequest):

    job_id = str(uuid4())

    _create_root_job(
        job_id = job_id,
        total_segments = len(request.segments),
        manifestation_id = request.manifestation_id
    )

    # Create segment task records
    _create_segment_tasks(
        job_id = job_id,
        segments = request.segments
    )

    dispatched_count = 0
    for segment in request.segments:
        message_body = {
            "job_id": job_id,
            "manifestation_id": request.manifestation_id,
            "segment_id": segment.segment_id,
            "start": segment.span.start,
            "end": segment.span.end
        }
        
        response = sqs_client.send_message(
            QueueUrl=get("SQS_QUEUE_URL"),
            MessageBody=json.dumps(message_body),
        )
        dispatched_count += 1
        print(f"Dispatched task {dispatched_count} to SQS for segment {segment.segment_id}, MessageId: {response['MessageId']}")

    return {
        "job_id": job_id,
        "status": "QUEUED",
        "message": f"Segments relation job created successfully. Dispatched {dispatched_count} tasks."
    }

def _create_root_job(job_id: uuid4, total_segments: int, manifestation_id: str):
    try:
        with SessionLocal() as session:
            session.add(
                RootJob(
                    job_id = job_id,
                    manifestation_id = manifestation_id,
                    total_segments = total_segments,
                    completed_segments = 0,
                    status = "QUEUED",
                    created_at = datetime.now(timezone.utc),
                    updated_at = datetime.now(timezone.utc)
                )
            )
            session.commit()

    except:
        raise HTTPException(status_code=500, detail="Failed to create root job, Database write error")

def _create_segment_tasks(job_id: str, segments: list):
    try:
        with SessionLocal() as session:
            for segment in segments:
                session.add(
                    SegmentTask(
                        task_id = uuid4(),
                        job_id = job_id,
                        segment_id = segment.segment_id,
                        status = "QUEUED",
                        created_at = datetime.now(timezone.utc),
                        updated_at = datetime.now(timezone.utc)
                    )
                )
            session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create segment tasks: {str(e)}")