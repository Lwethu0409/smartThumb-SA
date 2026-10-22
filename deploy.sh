#!/bin/bash
set -e
REGION="us-east-1"
SOURCE_BUCKET="hackathon-bucket-0001"
OUTPUT_BUCKET="hackathon-bucket-0002-output"
TOPIC_ARN="arn:aws:sns:us-east-1:315046343306:lambdaTopic"

echo "=== Deploying SmartThumb SA Pipeline ==="
echo "Creating S3 buckets..."
aws s3 mb s3://$SOURCE_BUCKET --region $REGION || true
aws s3 mb s3://$OUTPUT_BUCKET --region $REGION || true

echo "Deployment configuration complete!"
echo "Source Bucket: $SOURCE_BUCKET"
echo "Output Bucket: $OUTPUT_BUCKET"
echo "SNS Topic ARN: $TOPIC_ARN"
