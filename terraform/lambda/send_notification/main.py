import json
import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns_client = boto3.client("sns", region_name="eu-central-1", endpoint_url="http://host.docker.internal:4566")

def lambda_handler(event, context):

    logger.info("Sending notification for event: %s", json.dumps(event))

    topic_arn = os.environ.get("SNS_TOPIC_ARN")
    if not topic_arn:
        logger.warning("SNS_TOPIC_ARN is missing")
        raise Exception("SNSTopicNotSet")

    try:
        sns_client.publish(
            TopicArn=topic_arn,
            Message="Unencrypted S3 bucket or DynamoDB resource detected",
            Subject="Security Alert Mail"
        )
        logger.info("Notification sent to topic: %s", topic_arn)
        
    except Exception as e:
        logger.error("Error sending SNS notification: %s", str(e))
        raise e

    return {"status": "NotificationSent"}
