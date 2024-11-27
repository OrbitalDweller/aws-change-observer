import boto3
from typing import List
from datetime import datetime
from detected_objects import DetectedObjects

class ObjectDetectionService:
    """
    A service class to interact with AWS Rekognition for object detection.
    """
    def __init__(self, rekognition_resource=None):
        """
        Initialize the Rekognition client.

        :param rekognition_resource: Optional Rekognitionn resource for dependency injection.
        """        
        self.reko = rekognition_resource or boto3.client("rekognition")

    def detect_object(self, s3_bucket_name: str, s3_key: str) -> DetectedObjects:
        """
        Detects objects in an image stored in an S3 bucket.

        :param s3_bucket_name: The name of the S3 bucket.
        :param s3_key: The key of the image in the S3 bucket.
        :return: DetectedObjects instance containing detection details.
        """
        try:
            response = self.reko.detect_labels(
                    Image={"S3Object": {"Bucket": s3_bucket_name, "Name": s3_key}},
                    MaxLabels=10, MinConfidence=50
            )
            names = [label["Name"] for label in response.get("Labels",[])]
            date_taken = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            return DetectedObjects(date_detected=date_taken, detected_objects=names)

        except Exception as e:
            print(f"Error detecting objects: {e}")
            return DetectedObjects(date_detected="", detected_objects=[])
