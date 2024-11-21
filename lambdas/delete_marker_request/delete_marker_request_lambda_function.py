import json
import os
import logging
import boto3
from data_service import DataService

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize outside the handler for connection reuse
dynamodb_resource = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    AWS Lambda handler function to delete a location marker.

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
        marker_id = event["queryStringParameters"]["markerId"]
    except:
        logger.error(f"markerId is missing: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # Allow all origins for testing
                'Access-Control-Allow-Methods': 'GET,OPTIONS',  # Allowed methods
                'Access-Control-Allow-Headers': 'Content-Type',  # Allowed headers
            },
            'body': json.dumps({'error': 'Failed to retrieve markerId.'})
        }

    try:
        marker = data_service.delete_marker(marker_id)
        logger.info(f"Successfully deleted marker.")
        return {
            'statusCode': 201,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # Allow all origins for testing
                'Access-Control-Allow-Methods': 'GET,OPTIONS',  # Allowed methods
                'Access-Control-Allow-Headers': 'Content-Type',  # Allowed headers
            },
            'body': json.dumps({'message': 'Marker deleted successfully'})
        }
    except Exception as e:
        logger.error(f"Error deleting marker: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # Allow all origins for testing
                'Access-Control-Allow-Methods': 'GET,OPTIONS',  # Allowed methods
                'Access-Control-Allow-Headers': 'Content-Type',  # Allowed headers
            },
            'body': json.dumps({'error': 'Failed to delete marker.'})
        }
