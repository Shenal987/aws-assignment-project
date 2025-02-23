resource "aws_s3_bucket" "uploads_bucket" {
  bucket = var.s3_bucket_name
  lifecycle_rule {
    id      = "expire_old_objects"
    enabled = true

    expiration {
      days = 90
    }
  }
}

resource "aws_s3_bucket_notification" "s3_event_notification" {
  bucket = aws_s3_bucket.uploads_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.s3_event_handler.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [
    aws_lambda_permission.allow_bucket
  ]
}