import os
import boto3
import logging
from image_service import ImageService
from data_service import DataService  
from object_detection_service import ObjectDetectionService
from detected_objects import DetectedObjects
from shared_classes_layer.notification_service import NotificationService  # Import NotificationService

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

    sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
    if not sns_topic_arn:
        logger.error("SNS_TOPIC_ARN environment variable is not set.")
        return {
            "statusCode": 500,
            "body": "SNS_TOPIC_ARN environment variable is not set."
        }

    # Initialize services
    data_service = DataService(table_name=table_name, dynamodb_resource=dynamodb_resource)
    image_service = ImageService(s3_client, bucket_name)
    object_detecton_service = ObjectDetectionService()
    notification_service = NotificationService(sns_topic_arn=sns_topic_arn)  # Initialize NotificationService

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

            # Run object detection on the image
            detected_objects = object_detecton_service.detect_object(s3_bucket_name=image.get_s3_bucket_name(), s3_key=image.get_s3_key())
            marker.add_detected_objects(detected_objects)

            # Update the marker in DynamoDB
            data_service.update_marker(marker)
            logger.info(f"Successfully updated marker with ID {marker.get_marker_id()}.")

            # Check notification condition and notify subscribers
            if should_notify(marker):
                emails = marker.get('subscribedEmails', [])
                if emails:
                    try:
                        notification_service.notify_subscribers(marker.get_marker_id(), emails)
                        logger.info(f"Notifications sent for marker {marker.get_marker_id()} to {emails}.")
                    except Exception as e:
                        logger.error(f"Failed to notify subscribers for marker {marker.get_marker_id()}: {e}")
                else:
                    logger.info(f"No subscribers found for marker {marker.get_marker_id()}.")
        except Exception as e:
            logger.error(f"Failed to update marker with ID {marker.get_marker_id()}: {e}")

    return {
        "statusCode": 200,
        "body": f"Processed {len(markers)} markers."
    }

def should_notify(marker):
    """
    Condition for sending notifications.

    :param marker: The marker data from DynamoDB.
    :return: Boolean indicating whether to notify.
    """
    updated_at = marker.get('updatedAt')
    if updated_at:
        try:
            from datetime import datetime, timedelta
            updated_datetime = datetime.fromisoformat(updated_at)
            return updated_datetime >= datetime.utcnow() - timedelta(days=1)
        except ValueError:
            logger.warning(f"Invalid updatedAt format for marker {marker.get_marker_id()}: {updated_at}")
            return False
    return False
