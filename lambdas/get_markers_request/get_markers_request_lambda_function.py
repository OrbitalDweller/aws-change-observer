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
    AWS Lambda handler function to retrieve location markers.

    :param event: AWS Lambda event object.
    :param context: AWS Lambda context object.
    :return: HTTP response with status code and body.
    """
    table_name = os.environ.get('TABLE_NAME')
    if not table_name:
        logger.error("TABLE_NAME environment variable is not set.")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # Allow all origins for testing
                'Access-Control-Allow-Methods': 'GET,OPTIONS',  # Allowed methods
                'Access-Control-Allow-Headers': 'Content-Type',  # Allowed headers
            },
            'body': json.dumps({'error': 'Server configuration error.'})
        }

    data_service = DataService(table_name=table_name, dynamodb_resource=dynamodb_resource)
    
    try:
        markers = data_service.get_markers()
        logger.info(f"Successfully retrieved {len(markers)} markers.")
    except Exception as e:
        logger.error(f"Error retrieving markers: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # Allow all origins for testing
                'Access-Control-Allow-Methods': 'GET,OPTIONS',  # Allowed methods
                'Access-Control-Allow-Headers': 'Content-Type',  # Allowed headers
            },
            'body': json.dumps({'error': 'Failed to retrieve markers.'})
        }

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',  # Allow all origins for testing
            'Access-Control-Allow-Methods': 'GET,OPTIONS',  # Allowed methods
            'Access-Control-Allow-Headers': 'Content-Type',  # Allowed headers
        },
        'body': json.dumps([marker.to_json() for marker in markers])
    }
