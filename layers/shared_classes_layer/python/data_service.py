import boto3
from typing import List
from location_marker import LocationMarker
import uuid

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

    def add_marker(self, marker: LocationMarker) -> str:
        """
        Adds a new marker to the DynamoDB table.

        :param marker: A LocationMarker instance with location details.
        :return: marker with generated ID, or raises an exception on failure.
        """
        try:
            unique_id = str(uuid.uuid4()) #generate id
            marker.set_marker_id(unique_id)
           
            self.table.put_item(Item=marker.to_json())

            return unique_id
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
            return response
        except Exception as e:
            return None
        
    def update_marker(self, marker: LocationMarker):
        """
        Update an existing marker in DynamoDB
        :param marker: A LocationMarker with updated information. Replaces marker with identical ID
        :return: The updated LocationMarker.
        :raises Exception: Raises an exception if there is an issue updating the marker.
        """
        try:
            marker_id = marker.get_marker_id()
            if not marker_id:
                raise ValueError("Marker must have an ID")

            #get original marker data
            original_marker_data = self.table.get_item(
                Key={'markerId': str(marker_id)}
            ).get('Item')

            if not original_marker_data:
                raise ValueError(f"Marker with ID {marker_id} does not exist")

            #compare markers to create status
            original_marker = LocationMarker.from_json(original_marker_data)
            new_status = marker.compare(original_marker)
            marker.set_status(new_status)

            #remove old entry
            self.delete_marker(marker_id)

            #replace with updated entry
            self.table.put_item(Item=marker.to_json())
        
        except Exception as e:
            raise Exception(f"Failed to update marker in DynamoDB: {e}")
        
    def get_marker(self, marker_id: str) -> LocationMarker:
        """
        Retrieve a specific marker from DynamoDB by marker_id.
        
        :param marker_id: Unique identifier for the marker.
        :return: The corresponding LocationMarker instance, or raises an exception if not found.
        :raises Exception: Raises an exception if there is an issue retrieving the marker.
        """
        try:
            #get the marker data from
            marker_data = self.table.get_item(
                Key={'markerId': str(marker_id)}
            ).get('Item')

            #check if marker exists
            if not marker_data:
                raise ValueError(f"Marker with ID {marker_id} does not exist")

            #return marker object
            marker = LocationMarker.from_json(marker_data)
            return marker

        except Exception as e:
            raise Exception("Failed to retrieve marker from DynamoDB") from e
