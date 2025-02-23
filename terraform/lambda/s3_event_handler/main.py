import json
import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('stepfunctions', region_name="eu-central-1", endpoint_url='http://host.docker.internal:4566')

def lambda_handler(event, context):
    logger.info("Received S3 Event: %s", json.dumps(event))

    state_machine_arn = os.environ.get("STATE_MACHINE_ARN")
    if not state_machine_arn:
        logger.warning("STATE_MACHINE_ARN is missing")
        return {
            "statusCode": 500,
            "body": "Error: STATE_MACHINE_ARN Missing"
        }

    try:
        response = client.start_execution(
            stateMachineArn=state_machine_arn,
            input=json.dumps(event)
        )
        logger.info("Step Function execution started: %s", response["executionArn"])

        return {
            "statusCode": 200,
            "body": f"Step Function execution started: {response['executionArn']}"
        }

    except Exception as e:
        logger.error("Error starting Step Function: %s", str(e))
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }