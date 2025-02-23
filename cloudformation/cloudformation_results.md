### How I Resolved Security Issues ###

1. S3 Bucket Should Have Access Logging Configured (W35)

To enable access logging for the (S3Bucket), I created a separate log bucket (S3LogBucket) to store the logs. This ensures that access logs are captured while keeping the main bucket clean and secure.
```yaml
    S3Bucket:
      Type: AWS::S3::Bucket
      Properties: 
        BucketName: !Sub ${BucketName}-s3
        LoggingConfiguration:
          DestinationBucketName: !Ref S3LogBucket
          LogFilePrefix: 'access_logs/'
```
However for the log bucket itself (S3LogBucket), I did not enable logging again to avoid recursive logging loops. To overcome this I added a suppression rule under tag cfn_nag:
```yaml
    S3LogBucket:
        Type: AWS::S3::Bucket
        Properties:
          BucketName: !Sub ${BucketName}-access-logs
        Metadata:
          cfn_nag:
            rules_to_suppress:
              - id: W35
                reason: "This is a logging bucket neglect server access log property"
```
2. S3 Bucket Should Have a Bucket Policy (W51)

To address the warning about missing bucket policy, I added an explicit bucket policy to (S3Bucket) enforce security controls, ensuring deny public accees and that HTTP connections are not allowed.
```yaml
    Bucket: !Ref S3Bucket
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Sid: DenyPublicReadAccess
          Effect: Deny
          Principal: "*"
          Action:
            - "s3:GetObject"
            - "s3:ListBucket"
          Resource:
            - !Sub "arn:aws:s3:::${S3Bucket}/*"
            - !Sub "arn:aws:s3:::${S3Bucket}"
          Condition:
            Bool:
              "aws:SecureTransport": "false"
```
Additionally, I added a bucket policy to the logging bucket (S3LogBucket) to allow S3 access logging:
```yaml  
    Bucket: !Ref S3LogBucket
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Sid: AllowS3AccessLogging
          Effect: Allow
          Principal:
            Service: "logging.s3.amazonaws.com"
          Action: "s3:PutObject"
          Resource: !Sub "arn:aws:s3:::${S3LogBucket}/*"
```
3. S3 Bucket Should Have Encryption Enabled (W41)

To enable encryption for the S3 buckets, I added the BucketEncryption property with AES-256 encryption on both
```yaml
    S3Bucket:
      Type: AWS::S3::Bucket
      Properties: 
        BucketName: !Sub ${BucketName}-s3
        BucketEncryption:
          ServerSideEncryptionConfiguration:
            - ServerSideEncryptionByDefault:
                SEAlgorithm: AES256
```