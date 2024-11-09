import json
import os
import logging
import boto3
from data_service import DataService
from location_marker import LocationMarker

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize outside the handler for connection reuse
dynamodb_resource = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    AWS Lambda handler function to add a new location marker.

    :param event: AWS Lambda event object, expected to contain the marker data in the body.
    :param context: AWS Lambda context object.
    :return: HTTP response with status code and body.
    """
    table_name = os.environ.get('TABLE_NAME')
    if not table_name:
        logger.error("TABLE_NAME environment variable is not set.")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Server configuration error.'})
        }

    try:
        body = json.loads(event.get('body', '{}'))
        marker = LocationMarker.from_json(body)
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Invalid or missing body in the request: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request body.'})
        }
    except Exception as e:
        logger.error(f"Error creating LocationMarker from JSON: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid marker data format.'})
        }

    data_service = DataService(table_name=table_name, dynamodb_resource=dynamodb_resource)

    try:
        saved_marker = data_service.add_marker(marker)
        logger.info(f"Successfully added marker with ID: {saved_marker.get_marker_id()}")
        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Marker added successfully', 'marker': saved_marker.to_json()})
        }
    except Exception as e:
        logger.error(f"Failed to add marker to DynamoDB: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to add marker to DynamoDB.'})
        }