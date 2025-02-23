import json
import os
import pytest
from unittest.mock import patch, MagicMock
from main import lambda_handler

@patch.dict(os.environ, {"STATE_MACHINE_ARN": "arn:aws:states:eu-central-1:000000000000:stateMachine:FileProcessingStateMachine"}, clear=True)
@patch("main.client")

#Test the "happy path"
def test_s3_event_handler_success(mock_stepfunctions_client):

    mock_stepfunctions_client.start_execution.return_value = {
        "executionArn": "arn:aws:states:eu-central-1:000000000000:execution:FileProcessingStateMachine:abcdef"
    }

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "localstack-bucket"},
                    "object": {"key": "testfile.txt"}
                }
            }
        ]
    }

    result = lambda_handler(event, None)

    assert result["statusCode"] == 200
    assert "Step Function execution started: arn:aws:states:eu-central-1:000000000000:execution:FileProcessingStateMachine:abcdef" in result["body"]

    mock_stepfunctions_client.start_execution.assert_called_once_with(
        stateMachineArn="arn:aws:states:eu-central-1:000000000000:stateMachine:FileProcessingStateMachine",
        input=json.dumps(event)
    )

#Test when STATE_MACHINE_ARN is missing from environment
def test_s3_event_handler_missing_arn():

    if "STATE_MACHINE_ARN" in os.environ:
        del os.environ["STATE_MACHINE_ARN"]

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "localstack-bucket"},
                    "object": {"key": "testfile.txt"}
                }
            }
        ]
    }

    result = lambda_handler(event, None)

    assert result["statusCode"] == 500
    assert "Error: STATE_MACHINE_ARN Missing" in result["body"]


# Test a failure in start_execution
@patch.dict(os.environ, {"STATE_MACHINE_ARN": "arn:aws:states:eu-central-1:000000000000:stateMachine:FileProcessingStateMachine"}, clear=True)
@patch("main.client")
def test_s3_event_handler_start_execution_error(mock_stepfunctions_client):

    mock_stepfunctions_client.start_execution.side_effect = Exception("Some step function error")

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "localstack-bucket"},
                    "object": {"key": "testfile.txt"}
                }
            }
        ]
    }

    result = lambda_handler(event, None)

    assert result["statusCode"] == 500
    assert "Error: Some step function error" in result["body"]