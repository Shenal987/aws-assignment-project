import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3", endpoint_url="http://host.docker.internal:4566")

class UnencryptedBucket(Exception):
    pass

def lambda_handler(event, context):

    logger.info("Received S3 event: %s", json.dumps(event))

    try:
        record = event["Records"][0]
        bucket_name = record["s3"]["bucket"]["name"]

        try:
            response = s3_client.get_bucket_encryption(Bucket=bucket_name)
            encryption_rules = response.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
            
            if encryption_rules:
                sse_algorithm = encryption_rules[0]["ApplyServerSideEncryptionByDefault"].get("SSEAlgorithm", "NONE")
                logger.info("Bucket %s is encrypted with: %s", bucket_name, sse_algorithm)
                return event

        except ClientError as e: 
            if "ServerSideEncryptionConfigurationNotFoundError" in str(e):
                logger.info("Bucket %s is NOT encrypted", bucket_name)
                raise UnencryptedBucket("Bucket level SSE is missing")
            else:
                logger.error("Error checking bucket encryption: %s", str(e))
                raise e

    except KeyError as e:
        logger.error("Missing S3 key events: %s", str(e))
        raise Exception("UnformedS3Event")