resource "aws_dynamodb_table" "uploads_table" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "filename"
  range_key    = "upload_timestamp"

  attribute {
    name = "filename"
    type = "S"
  }

  attribute {
    name = "upload_timestamp"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }
}