import pytest
import os
import json
from unittest.mock import patch, MagicMock
from main import lambda_handler, UnencryptedDynamoDB

@patch.dict(os.environ, {"DYNAMODB_TABLE": "MyTable"}, clear=True)
@patch("main.dynamodb_client.describe_table")
#Test that Lambda returns the event when SSE is enabled
def test_dynamodb_encrypted(mock_describe_table):

    mock_describe_table.return_value = {
        "Table": {
            "SSEDescription": {"Status": "ENABLED"}
        }
    }

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "some-bucket"},
                    "object": {"key": "testfile.txt"}
                }
            }
        ]
    }

    result = lambda_handler(event, None)

    assert result == event
    mock_describe_table.assert_called_once_with(TableName="MyTable")


@patch.dict(os.environ, {"DYNAMODB_TABLE": "MyTable"}, clear=True)
@patch("main.dynamodb_client.describe_table")
#Test that Lambda raises UnencryptedDynamoDB if SSE is DISABLED
def test_dynamodb_unencrypted(mock_describe_table):

    mock_describe_table.return_value = {
        "Table": {
            "SSEDescription": {"Status": "DISABLED"}
        }
    }

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "some-bucket"},
                    "object": {"key": "testfile.txt"}
                }
            }
        ]
    }

    with pytest.raises(UnencryptedDynamoDB) as exc:
        lambda_handler(event, None)

    assert "DynamoDB is unencrypted" in str(exc.value)
    mock_describe_table.assert_called_once_with(TableName="MyTable")

#Test that Lambda raises an exception if DYNAMODB_TABLE is missing
def test_missing_table_env():

    if "DYNAMODB_TABLE" in os.environ:
        del os.environ["DYNAMODB_TABLE"]

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "some-bucket"},
                    "object": {"key": "testfile.txt"}
                }
            }
        ]
    }

    with pytest.raises(Exception) as exc:
        lambda_handler(event, None)

    assert "DynamoDBTableNotSet" in str(exc.value)


@patch.dict(os.environ, {"DYNAMODB_TABLE": "MyTable"}, clear=True)
@patch("main.dynamodb_client.describe_table")
#Test that any other error from describe_table is re-raised
def test_other_error(mock_describe_table):

    mock_describe_table.side_effect = Exception("Some other error")

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "some-bucket"},
                    "object": {"key": "testfile.txt"}
                }
            }
        ]
    }

    with pytest.raises(Exception) as exc:
        lambda_handler(event, None)

    assert "Some other error" in str(exc.value)
    mock_describe_table.assert_called_once_with(TableName="MyTable")
