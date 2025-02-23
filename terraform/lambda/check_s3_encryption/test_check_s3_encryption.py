import json
import pytest
from unittest.mock import patch, MagicMock
from main import lambda_handler, UnencryptedBucket
from botocore.exceptions import ClientError

#Test that the Lambda returns the event when the bucket is encrypted
@patch("main.s3_client")
def test_encrypted_bucket(mock_s3_client):

    mock_s3_client.get_bucket_encryption.return_value = {
        "ServerSideEncryptionConfiguration": {
            "Rules": [
                {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}
            ]
        }
    }

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "encrypted-bucket"}
                }
            }
        ]
    }

    result = lambda_handler(event, None)

    assert result == event

    mock_s3_client.get_bucket_encryption.assert_called_once_with(Bucket="encrypted-bucket")

#Test that the Lambda raises UnencryptedBucket if SSE is missing
@patch("main.s3_client")
def test_unencrypted_bucket(mock_s3_client):

    mock_error = ClientError(
        {"Error": {"Code": "ServerSideEncryptionConfigurationNotFoundError"}},
        "GetBucketEncryption"
    )

    mock_s3_client.get_bucket_encryption.side_effect = mock_error

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "unencrypted-bucket"}
                }
            }
        ]
    }

    with pytest.raises(UnencryptedBucket) as exc:
        lambda_handler(event, None)

    assert "Bucket level SSE is missing" in str(exc.value)

#Test that any other ClientError is re-raised, not treated as unencrypted
@patch("main.s3_client")
def test_other_client_error(mock_s3_client):

    mock_s3_client.get_bucket_encryption.side_effect = Exception("SomeOtherClientError")

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "some-bucket"}
                }
            }
        ]
    }

    with pytest.raises(Exception) as exc:
        lambda_handler(event, None)

    assert "SomeOtherClientError" in str(exc.value)

#Test that a missing 'Records' or 'bucket' key triggers 'UnformedS3Event'
def test_missing_key():

    event = {
    }

    with pytest.raises(Exception) as exc:
        lambda_handler(event, None)

    assert "UnformedS3Event" in str(exc.value)
