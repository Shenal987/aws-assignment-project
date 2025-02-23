import json
import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb", region_name="eu-central-1", endpoint_url="http://host.docker.internal:4566")

class UnencryptedDynamoDB(Exception):
    pass

def lambda_handler(event, context):

    logger.info("Checking DynamoDB encryption for event: %s", json.dumps(event))

    table_name = os.environ.get("DYNAMODB_TABLE")
    if not table_name:
        logger.warning("DYNAMODB_TABLE is missing")
        raise Exception("DynamoDBTableNotSet")

    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        sse_status = response["Table"].get("SSEDescription", {}).get("Status", "DISABLED")

        if sse_status != "ENABLED":
            logger.error("DynamoDB table %s is NOT encrypted", table_name)
            raise UnencryptedDynamoDB("DynamoDB is unencrypted")

        logger.info("DynamoDB table is encrypted: %s", table_name)
        return event

    except Exception as e:
        logger.error("Error checking DynamoDB encryption: %s", str(e))
        raise e
