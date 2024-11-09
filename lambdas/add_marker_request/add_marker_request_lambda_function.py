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

    # marker data is passed in the event body
    try:
        body = json.loads(event['body'])
    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Invalid or missing body in the request: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request body.'})
        }

    data_service = DataService(table_name=table_name, dynamodb_resource=dynamodb_resource)
    
    # TODO: Implement data_service or direct DynamoDB interaction here

    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'TODO: Marker addition logic not implemented yet'})
    }
    