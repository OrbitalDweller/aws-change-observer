import boto3
import logging
from typing import List
from location_marker import LocationMarker
import uuid

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

    def get_markers(self) -> List[LocationMarker]:
        """
        Retrieve all markers from the DynamoDB table.

        :return: A list of markers.
        :raises Exception: Raises an exception if there is an issue retrieving markers.
        """
        try: 
            response = self.table.scan()
            markers_data = response.get('Items', [])
            markers = [LocationMarker.from_json(marker_data) for marker_data in markers_data]
            return markers
        except Exception as e:
            raise Exception("Failed to retrieve markers from DynamoDB") from e

    def add_marker(self, marker: LocationMarker) -> LocationMarker:
        """
        Adds a new marker to the DynamoDB table.

        :param marker: A LocationMarker instance with location details.
        :return: marker with generated ID, or raises an exception on failure.
        """
        try:
            unique_id = str(uuid.uuid4()) #generate id
            marker.set_marker_id(unique_id)
           
            self.table.put_item(Item=marker.to_json())

            return marker
        except Exception as e:
            raise Exception("Failed to add marker to DynamoDB") from e        

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
