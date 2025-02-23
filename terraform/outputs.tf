output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.uploads_bucket.bucket
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.uploads_table.name
}

output "step_function_arn" {
  description = "ARN of the Step Function"
  value       = aws_sfn_state_machine.file_processing.arn
}

output "sns_topic_arn" {
  description = "ARN of the SNS Topic"
  value       = aws_sns_topic.security_alert.arn
}