resource "aws_sfn_state_machine" "file_processing" {
  name     = "FileProcessingStateMachine"
  role_arn = aws_iam_role.lambda_role.arn
  definition = <<EOF
  {
  "Comment": "File Processing Workflow",
  "StartAt": "CheckS3Encryption",
  "States": {
    "CheckS3Encryption": {
      "Type": "Task",
      "Resource": "${aws_lambda_function.check_s3_encryption.arn}",
      "Next": "StoreMetadata",
      "Catch": [
        {
          "ErrorEquals": ["UnencryptedBucket"],
          "Next": "SendNotification"
        }
      ]
    },
    "StoreMetadata": {
      "Type": "Task",
      "Resource": "${aws_lambda_function.store_metadata_dynamodb.arn}",
      "Next": "CheckDynamoDBEncryption",
      "Catch": [
        {
          "ErrorEquals": ["DynamoDBWriteError"],
          "Next": "SendNotification"
        }
      ]
    },
    "CheckDynamoDBEncryption": {
      "Type": "Task",
      "Resource": "${aws_lambda_function.check_dynamodb_encryption.arn}",
      "Next": "SuccessState",
      "Catch": [
        {
          "ErrorEquals": ["UnencryptedDynamoDB"],
          "Next": "SendNotification"
        }
      ]
    },
    "SendNotification": {
      "Type": "Task",
      "Resource": "${aws_lambda_function.send_notification.arn}",
      "End": true
    },
    "SuccessState": {
      "Type": "Succeed"
    }
  }
}
EOF
}