# SmartThumb SA 

SmartThumb SA is an automated, event-driven serverless image processing pipeline built on AWS for modern digital asset management. Whenever an image is uploaded to the source S3 bucket, an AWS Lambda function automatically triggers, resizes the image into an optimized thumbnail using Python and Pillow, extracts descriptive AI tags via Amazon Rekognition, stores the thumbnail in an output S3 bucket, and broadcasts real-time email notifications via Amazon SNS.

## Architecture & AWS Services
* **Amazon S3 (Source):** `hackathon-bucket-0001` (Triggers pipeline on image upload)
* **Amazon S3 (Output):** `hackathon-bucket-0002-output` (Stores generated thumbnails)
* **AWS Lambda:** Python 3.10 runtime bundled with Pillow for image resizing
* **Amazon Rekognition:** Computer vision API (`DetectLabels`) for automated image tagging
* **Amazon SNS:** `arn:aws:sns:us-east-1:315046343306:lambdaTopic` (`lambdaTopic`) for email notifications
* **Amazon CloudWatch:** Logging and error monitoring

---

## Quick Start (AWS CloudShell)

Follow these steps in your own AWS account using CloudShell (`us-east-1`):

1. **Clone or Download Repository**
   Ensure you have the repository files ready or downloaded in CloudShell.

2. **Run Deployment Script**
   Execute the automated deployment script to set up buckets, IAM roles, and the Lambda function:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Test the Pipeline**
   Upload a sample test image to your source bucket:
   ```bash
   aws s3 cp sample.jpg s3://hackathon-bucket-0001/
   ```
   *Check your email for the SNS notification containing the thumbnail location and AI tags!*

4. **Cleanup Resources (When Done)**
   To remove deployed AWS resources and avoid charges:
   ```bash
   chmod +x cleanup.sh
   ./cleanup.sh
   ```

---

## 📊 Real Test Results & Execution Sample
* **Source Images Tested:** `drawing1.jpg`, `eclipse.jpg`, `handbags/WhatsApp Image.jpeg`
* **AI Suggested Categories (Amazon Rekognition):** `Accessories`, `Bag`, `Handbag`, `Purse`, `Tote Bag`
* **Notification Email Subject:** `SmartThumb SA: Thumbnail & AI Tags Ready!`
