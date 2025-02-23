resource "aws_lambda_function" "s3_event_handler" {
  function_name    = "s3_event_handler"
  role             = aws_iam_role.lambda_role.arn
  runtime          = "python3.9"
  handler          = "main.lambda_handler"
  source_code_hash = filebase64sha256("lambda/s3_event_handler/lambda.zip")
  filename         = "lambda/s3_event_handler/lambda.zip"
  environment {
    variables = {
      STATE_MACHINE_ARN = aws_sfn_state_machine.file_processing.arn
    }
  }
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3BucketEvent"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.s3_event_handler.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.uploads_bucket.arn
}

resource "aws_lambda_function" "check_s3_encryption" {
  function_name    = "check_s3_encryption"
  role             = aws_iam_role.lambda_role.arn
  runtime          = "python3.9"
  handler          = "main.lambda_handler"
  source_code_hash = filebase64sha256("lambda/check_s3_encryption/lambda.zip")
  filename         = "lambda/check_s3_encryption/lambda.zip"
}

resource "aws_lambda_function" "store_metadata_dynamodb" {
  function_name    = "store_metadata_dynamodb"
  filename         = "lambda/store_metadata_dynamodb/lambda.zip"
  source_code_hash = filebase64sha256("lambda/store_metadata_dynamodb/lambda.zip")
  handler          = "main.lambda_handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn
  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.uploads_table.name
    }
  }
}

resource "aws_lambda_function" "check_dynamodb_encryption" {
  function_name    = "check_dynamodb_encryption"
  filename         = "lambda/check_dynamodb_encryption/lambda.zip"
  source_code_hash = filebase64sha256("lambda/check_dynamodb_encryption/lambda.zip")
  handler          = "main.lambda_handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn
  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.uploads_table.name
    }
  }
}

resource "aws_lambda_function" "send_notification" {
  function_name    = "send_notification"
  filename         = "lambda/send_notification/lambda.zip"
  source_code_hash = filebase64sha256("lambda/send_notification/lambda.zip")
  handler          = "main.lambda_handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn
  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.security_alert.arn
    }
  }
}