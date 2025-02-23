resource "aws_iam_role" "lambda_role" {
  name = "lambda_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Action": "sts:AssumeRole",
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"}
  }]
}
EOF
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "lambda_policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:GetBucketEncryption"
        ],
        Resource = [
          "${aws_s3_bucket.uploads_bucket.arn}",
          "${aws_s3_bucket.uploads_bucket.arn}/*"
        ]
      },
      {
        Effect   = "Allow",
        Action   = [
          "dynamodb:GetItem",
          "dynamodb:Scan",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ],
        Resource = "${aws_dynamodb_table.uploads_table.arn}"
      },
      {
        Effect   = "Allow",
        Action   = [
          "sns:Publish"
        ],
        Resource = "${aws_sns_topic.security_alert.arn}"
      },
      {
        Effect   = "Allow",
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:eu-central-1:000000000000:log-group:/aws/lambda/*"
      },
      {
        Effect   = "Allow",
        Action   = [
          "states:StartExecution"
        ],
        Resource = "${aws_sfn_state_machine.file_processing.arn}"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_iam_role" "step_functions_role" {
  name = "step_functions_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Action": "sts:AssumeRole",
    "Effect": "Allow",
    "Principal": { "Service": "states.amazonaws.com" }
  }]
}
EOF
}

resource "aws_iam_policy" "step_functions_invoke_lambda" {
  name = "step_functions_invoke_lambda"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "lambda:InvokeFunction",
        Resource = [
          "${aws_lambda_function.check_s3_encryption.arn}",
          "${aws_lambda_function.store_metadata_dynamodb.arn}",
          "${aws_lambda_function.check_dynamodb_encryption.arn}",
          "${aws_lambda_function.send_notification.arn}"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "step_functions_lambda_invoke" {
  role       = aws_iam_role.step_functions_role.name
  policy_arn = aws_iam_policy.step_functions_invoke_lambda.arn
}