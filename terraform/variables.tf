variable "s3_bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
  default     = "localstack-bucket"
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  type        = string
  default     = "localstack-table"
}