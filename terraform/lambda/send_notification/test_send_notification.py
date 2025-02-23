import pytest
import os
from unittest.mock import patch, MagicMock
from main import lambda_handler

@patch.dict(os.environ, {"SNS_TOPIC_ARN": "arn:aws:sns:eu-central-1:000000000000:SecurityAlert"}, clear=True)
@patch("main.sns_client.publish")
#Test that Lambda publishes successfully to SNS when the topic ARN is set
def test_send_notification_success(mock_publish):
 
    event = {"Error": "UnencryptedDynamoDB", "Cause": "some error cause"}
    
    result = lambda_handler(event, None)

    assert result == {"status": "NotificationSent"}

    mock_publish.assert_called_once_with(
        TopicArn="arn:aws:sns:eu-central-1:000000000000:SecurityAlert",
        Message="Unencrypted S3 bucket or DynamoDB resource detected",
        Subject="Security Alert Mail"
    )

@patch.dict(os.environ, {}, clear=True)
#Test that Lambda raises an exception if SNS_TOPIC_ARN is missing
def test_send_notification_missing_topic():

    event = {"Error": "UnencryptedObject"}
    
    with pytest.raises(Exception) as exc:
        lambda_handler(event, None)
    
    assert "SNSTopicNotSet" in str(exc.value)

@patch.dict(os.environ, {"SNS_TOPIC_ARN": "arn:aws:sns:eu-central-1:000000000000:SecurityAlert"}, clear=True)
@patch("main.sns_client.publish")
#Test that Lambda re-raises an error if publish fails
def test_send_notification_publish_error(mock_publish):

    mock_publish.side_effect = Exception("Some SNS publish error")
    
    event = {"Error": "UnencryptedObject"}
    
    with pytest.raises(Exception) as exc:
        lambda_handler(event, None)
    
    assert "Some SNS publish error" in str(exc.value)
    mock_publish.assert_called_once()
