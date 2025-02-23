import json
import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.resource("dynamodb", region_name="eu-central-1", endpoint_url="http://host.docker.internal:4566")

class DynamoDBWriteError(Exception):
    pass

def lambda_handler(event, context):

    logger.info("Event Storing in DynamoDB: %s", json.dumps(event))

    table_name = os.environ.get("DYNAMODB_TABLE")
    if not table_name:
        logger.warning("DYNAMODB_TABLE is missing")
        raise Exception("DynamoDBTableNotSet")

    table = dynamodb_client.Table(table_name)

    try:
        record = event["Records"][0]
        filename = record["s3"]["object"]["key"]
        upload_timestamp = record["eventTime"]

        table.put_item(
            Item={
                "filename": filename,
                "upload_timestamp": upload_timestamp
            }
        )
        logger.info("Successfully stored metadata for %s", filename)

        return event

    except Exception as e:
        logger.error("Error storing metadata: %s", str(e))
        raise DynamoDBWriteError("Error Writting to Dyanamodb")
