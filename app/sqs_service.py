import boto3
import json
from app.config import get

sqs_client = boto3.client(
    'sqs',
    region_name=get('AWS_REGION'),
    aws_access_key_id=get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=get('AWS_SECRET_ACCESS_KEY')
)


def send_completed_mapping_text_to_sqs_service(
    text_id: str,
    segment_ids: list[str],
    total_segments: int,
):
    """
    Send a message to the SQS service to notify that the mapping text has been completed.
    """
    try:
        sqs_client.send_message(
            QueueUrl=get('SQS_COMPLETED_QUEUE_URL'),
            MessageBody=json.dumps(
                {
                    "text_id": text_id,
                    "segment_ids": segment_ids,
                    "total_segments": total_segments
                }
            )
        )
    except Exception as exc:
        raise exc
