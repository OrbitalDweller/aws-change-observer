import os
import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize outside the handler for connection reuse
dynamodb_resource = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

def lambda_handler(event, context):

    table_name = os.environ.get('TABLE_NAME')
    if not table_name:
        logger.error("TABLE_NAME environment variable is not set.")
        return

    bucket_name = os.environ['BUCKET_NAME']
    if not table_name:
        logger.error("BUCKET_NAME environment variable is not set.")
        return

    # Example: Upload a file to the bucket
    s3_client.put_object(
        Bucket=bucket_name,
        Key='example.txt',
        Body='This is some example content.'
    )
