import boto3
import os
from io import BytesIO
from PIL import Image

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
sns = boto3.client('sns')

OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET', 'hackathon-bucket-0002-output')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:315046343306:lambdaTopic')

def lambda_handler(event, context):
    try:
        record = event['Records'][0]
        source_bucket = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        if source_bucket == OUTPUT_BUCKET:
            return {'status': 'Skipped output bucket event'}
            
        print(f"Processing image {object_key} from {source_bucket}")
        
        # Download image
        response = s3.get_object(Bucket=source_bucket, Key=object_key)
        image_content = response['Body'].read()
        
        # Rekognition AI labeling
        rek_response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': source_bucket, 'Name': object_key}},
            MaxLabels=5,
            MinConfidence=75
        )
        tags = [label['Name'] for label in rek_response['Labels']]
        tags_str = ", ".join(tags)
        
        # Resize image using Pillow
        image = Image.open(BytesIO(image_content))
        image.thumbnail((300, 300))
        
        buffer = BytesIO()
        img_format = image.format if image.format else 'JPEG'
        image.save(buffer, format=img_format)
        buffer.seek(0)
        
        thumbnail_key = f"thumb-{os.path.basename(object_key)}"
        s3.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=thumbnail_key,
            Body=buffer,
            ContentType=response['ContentType']
        )
        
        # SNS Notification
        message = (
            f"SmartThumb SA Alert:\n"
            f"- Image: {object_key}\n"
            f"- Thumbnail: {thumbnail_key} (in {OUTPUT_BUCKET})\n"
            f"- AI Suggested Categories: {tags_str}"
        )
        
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="SmartThumb SA: Thumbnail & AI Tags Ready!",
            Message=message
        )
        
        return {'statusCode': 200, 'body': 'Success'}
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e
