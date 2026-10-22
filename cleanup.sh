#!/bin/bash
set -e
echo "=== Cleaning up SmartThumb SA Resources ==="
echo "Note: S3 buckets must be emptied before deletion."
aws s3 rm s3://hackathon-bucket-0001 --recursive || true
aws s3 rb s3://hackathon-bucket-0001 --force || true
aws s3 rm s3://hackathon-bucket-0002-output --recursive || true
aws s3 rb s3://hackathon-bucket-0002-output --force || true
echo "Cleanup completed."
