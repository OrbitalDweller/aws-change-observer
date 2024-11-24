import os
import boto3
import logging
from image_service import ImageService
from data_service import DataService  # Assuming you have a DataService class

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize resources outside the handler for connection reuse
dynamodb_resource = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Get environment variables
    table_name = os.environ.get('TABLE_NAME')
    if not table_name:
        logger.error("TABLE_NAME environment variable is not set.")
        return {
            "statusCode": 500,
            "body": "TABLE_NAME environment variable is not set."
        }

    bucket_name = os.environ.get('BUCKET_NAME')
    if not bucket_name:
        logger.error("BUCKET_NAME environment variable is not set.")
        return {
            "statusCode": 500,
            "body": "BUCKET_NAME environment variable is not set."
        }

    # Initialize services
    data_service = DataService(table_name=table_name, dynamodb_resource=dynamodb_resource)
    image_service = ImageService(s3_client, bucket_name)

    try:
        # Retrieve markers
        markers = data_service.get_markers()
        logger.info(f"Successfully retrieved {len(markers)} markers.")
    except Exception as e:
        logger.error(f"Error retrieving markers: {e}")
        return {
            "statusCode": 500,
            "body": f"Error retrieving markers: {e}"
        }

    for marker in markers:
        try:
            # Fetch the latest image for the marker
            image = image_service.get_latest_image(marker.get_coordinate())
            marker.set_current_image(image)

            # Update the marker in DynamoDB
            data_service.update_marker(marker)
            logger.info(f"Successfully updated marker with ID {marker.get_marker_id()}.")
        except Exception as e:
            logger.error(f"Failed to update marker with ID {marker.get_marker_id()}: {e}")

    return {
        "statusCode": 200,
        "body": f"Processed {len(markers)} markers."
    }
