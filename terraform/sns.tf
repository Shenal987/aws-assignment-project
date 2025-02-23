resource "aws_sns_topic" "security_alert" {
  name = "SecurityAlert"
}

resource "aws_sns_topic_subscription" "alert_email" {
  topic_arn = aws_sns_topic.security_alert.arn
  protocol  = "email"
  endpoint  = "shenal.m255@gmail.com"
}
