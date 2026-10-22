import boto3
import os
import urllib.parse
from PIL import Image

# Initialize the AWS clients
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
rekognition_client = boto3.client('rekognition')

# Output bucket and SNS topic configuration
OUTPUT_BUCKET_NAME = 'hackathon-bucket-0002-output'
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:315046343306:lambdaTopic')
MAX_SIZE = (300, 300)

def lambda_handler(event, context):
    try:
        # 1. Get source bucket and URL-decode the image key to handle spaces/special chars
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        raw_key = event['Records'][0]['s3']['object']['key']
        image_key = urllib.parse.unquote_plus(raw_key)
        
        print(f"Processing image {image_key} from bucket {source_bucket}")
        
        # 2. Call Amazon Rekognition to analyze the image directly from S3 (AI Extension)
        suggested_labels = []
        try:
            rek_response = rekognition_client.detect_labels(
                Image={
                    'S3Object': {
                        'Bucket': source_bucket,
                        'Name': image_key
                    }
                },
                MaxLabels=5,
                MinConfidence=75.0
            )
            suggested_labels = [label['Name'] for label in rek_response['Labels']]
            print(f"AI Suggested Tags for {image_key}: {suggested_labels}")
        except Exception as rek_error:
            print(f"Rekognition labeling skipped or failed: {str(rek_error)}")

        # 3. Download the image from S3 into Lambda's temporary storage (/tmp)
        download_path = f"/tmp/{image_key.split('/')[-1]}"
        s3_client.download_file(source_bucket, image_key, download_path)
        
        resized_path = f"/tmp/resized_{image_key.split('/')[-1]}"
        
        # 4. Open image, normalize to RGB (handles CMYK, RGBA, etc.), and generate aspect-ratio-preserving thumbnail
        with Image.open(download_path) as image:
            if image.mode != "RGB":
                image = image.convert("RGB")
                
            image.thumbnail(MAX_SIZE)
            image.save(resized_path)
            
        # 5. Upload the resized thumbnail to your output bucket
        thumbnail_name = f"thumb-{image_key.split('/')[-1]}"
        s3_client.upload_file(resized_path, OUTPUT_BUCKET_NAME, thumbnail_name)
        
        print(f"Successfully generated and uploaded thumbnail: {thumbnail_name} to {OUTPUT_BUCKET_NAME}")
        
        # 6. Optional SNS Notification (including AI tags!)
        try:
            tags_text = ", ".join(suggested_labels) if suggested_labels else "None detected"
            message = (f"SmartThumb SA Alert:\n"
                       f"- Image: {image_key}\n"
                       f"- Thumbnail: {thumbnail_name} (in {OUTPUT_BUCKET_NAME})\n"
                       f"- AI Suggested Categories: {tags_text}")
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject="SmartThumb SA: Thumbnail & AI Tags Ready!"
            )
        except Exception as sns_error:
            print(f"Notification skipped or failed: {str(sns_error)}")
        
        return {
            'statusCode': 200,
            'body': f"Thumbnail created and AI labels generated for {image_key}!"
        }
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        raise e

