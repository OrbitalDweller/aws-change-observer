import boto3
import logging
from typing import List

logger = logging.getLogger(__name__)

class DataService:
    """A service class for interacting with the DynamoDB LocationMarkers table."""

    def __init__(self, table_name: str, dynamodb_resource=None):
        """
        Initialize the DataService with the specified DynamoDB table.

        :param table_name: The name of the DynamoDB table to interact with.
        :param dynamodb_resource: Optional DynamoDB resource for dependency injection.
        """
        self.dynamodb = dynamodb_resource or boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def get_markers(self) -> List[dict]:
        """
        Retrieve all markers from the DynamoDB table.

        :return: A list of markers.
        :raises NotImplementedError: Indicates the method is not yet implemented.
        """
        try: 
            response = self.table.scan()
            markers = response.get('Items', [])
            return markers
        except Exception as e:
            logger.error(f"Error retrieving markers")

    def add_marker(self, markerId, name, longitude, latitude, imgurl, tags):
        """
        Add a new marker to the DynamoDB table.

        :param markerId: Unique identifier for the location.
        :param Name: Name of the location.
        :param Longitude: Longitude coordinate of the location.
        :param Latitude: Latitude coordinate of the location.
        :param ImgUrl: URL to an image of the location.
        :param Tags: Tags associated with the location.
        :return: The response from DynamoDB.
        """
        response = self.table.put_item(
            Item={
                'markerId': str(markerId),  #dynamoDB schema requires string here
                'name': name,
                'longitude': longitude,
                'Latitude': latitude,  
                'ImgUrl': imgurl,
                'Tags': tags
            }
        )
        logger.info(f"Marker added: {name} (ID: {markerId})")
        return response  #response for debugging


    def delete_marker(self, markerId):
        """
        Delete a marker from the DynamoDB table.

        :param markerId: Unique identifier for the location to delete.
        :return: The response from DynamoDB.
        """
        try:
            response = self.table.delete_item(
                Key={
                    'markerId': str(markerId)  #dynamoDB schema requires string here
                }
            )
            logger.info(f"Marker with markerId {markerId} deleted.")
            return response
        except Exception as e:
            logger.error(f"Error deleting marker with markerId {markerId}: {e}")
            return None
        
