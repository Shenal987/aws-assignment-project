import pytest
import os
import json
from unittest.mock import patch, MagicMock
from main import lambda_handler, DynamoDBWriteError

@patch.dict(os.environ, {"DYNAMODB_TABLE": "Files"}, clear=True)
@patch("main.dynamodb_client.Table")

#Test that Lambda stores metadata successfully when environment and event are correct
def test_store_metadata_success(mock_table):

    mock_table_instance = MagicMock()
    mock_table.return_value = mock_table_instance

    event = {
        "Records": [
            {
                "s3": {
                    "object": {"key": "testfile.txt"}
                },
                "eventTime": "2025-02-24T10:00:00Z"
            }
        ]
    }

    result = lambda_handler(event, None)
    assert result == event

    mock_table_instance.put_item.assert_called_once_with(
        Item={
            "filename": "testfile.txt",
            "upload_timestamp": "2025-02-24T10:00:00Z"
        }
    )

#Test that Lambda raises Exception if DYNAMODB_TABLE is missing from environment
@patch.dict(os.environ, {}, clear=True)
def test_store_metadata_missing_table():

    event = {
        "Records": [
            {
                "s3": {
                    "object": {"key": "testfile.txt"}
                },
                "eventTime": "2025-02-24T10:00:00Z"
            }
        ]
    }

    with pytest.raises(Exception) as exc:
        lambda_handler(event, None)

    assert "DynamoDBTableNotSet" in str(exc.value)

@patch.dict(os.environ, {"DYNAMODB_TABLE": "Files"}, clear=True)
@patch("main.dynamodb_client.Table")
#Test that Lambda raises DynamoDBWriteError if put_item fails
def test_store_metadata_put_item_error(mock_table):

    mock_table_instance = MagicMock()
    mock_table.return_value = mock_table_instance
    mock_table_instance.put_item.side_effect = Exception("some put_item error")

    event = {
        "Records": [
            {
                "s3": {
                    "object": {"key": "testfile.txt"}
                },
                "eventTime": "2025-02-24T10:00:00Z"
            }
        ]
    }

    with pytest.raises(DynamoDBWriteError) as exc:
        lambda_handler(event, None)

    assert "Error Writting to Dyanamodb" in str(exc.value)
    mock_table_instance.put_item.assert_called_once()
