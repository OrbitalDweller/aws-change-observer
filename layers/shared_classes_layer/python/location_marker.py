from typing import List, Dict, Optional
from datetime import datetime
import re

from coordinate import Coordinate
from image import Image
from detected_objects import DetectedObjects

class LocationMarker:
    def __init__(self, coordinate: Coordinate, name: str = "name me", status: str = "created",
                 subscribed_emails: List[str] = None, current_image: Image = None,
                 historical_images: List[Image] = None, detected_objects: List[DetectedObjects] = None):
        """
        Constructor for the LocationMarker class.
        
        :param coordinate: Coordinate instance representing the location.
        :param status: Status of the marker (default is "created").
        :param subscribed_emails: List of emails subscribed to the marker.
        :param current_image: Current Image instance.
        :param historical_images: List of historical Image instances.
        :param detected_objects: List of DetectedObjects instances.
        """
        self._marker_id = None  # Initially set to None, to be assigned later by Data Service
        self._coordinate = coordinate
        self._name = name
        self._status = status
        self._date_created = datetime.now()  # Set to current date and time
        self._subscribed_emails = subscribed_emails or []
        self._current_image = current_image
        self._historical_images = historical_images or []
        self._detected_objects = detected_objects or []

    # Getters and Setters
    def get_name(self):
        return self._name

    def set_name(self, name: str):
        self._name = name

    def get_marker_id(self) -> Optional[str]:
        return self._marker_id

    def set_marker_id(self, marker_id: str):
        self._marker_id = marker_id

    def add_subscription_email(self, email: str):
        self._subscribed_emails.append(email)

    def get_subscription_emails(self) -> List[str]:
        return self._subscribed_emails

    def set_status(self, status: str):
        self._status = status

    def get_status(self) -> str:
        return self._status

    def set_current_image(self, image: Image):
        self._current_image = image

    def get_current_image(self) -> Image:
        return self._current_image

    def get_historical_images(self) -> List[Image]:
        return self._historical_images

    def set_historical_images(self, images: List[Image]):
        self._historical_images = images

    def add_image_to_history(self, image: Image):
        self._historical_images.append(image)

    def add_detected_objects(self, detected_objects: DetectedObjects):
        self._detected_objects.append(detected_objects)

    def get_detected_objects(self) -> List[DetectedObjects]:
        return self._detected_objects

    def get_date_created(self) -> datetime:
        return self._date_created
    
    def set_date_created(self,date_created:datetime):
        self._date_created = date_created

    def get_coordinate(self) -> Coordinate:
        return self._coordinate

    def set_current_image(self, image: Image):
        self._current_image = image

    # JSON Serialization
    def to_json(self) -> Dict[str, any]:
        """
        Converts the LocationMarker instance to a JSON-compatible dictionary.
        
        :return: Dictionary with LocationMarker details.
        """
        return {
            "markerId": self._marker_id,
            "name": self._name,
            "subscribedEmails": self._subscribed_emails,
            "coordinate": self._coordinate.to_json(),
            "status": self._status,
            "dateCreated": self._date_created.isoformat(),
            "currentImage": self._current_image.to_json() if self._current_image else None,
            "historicalImages": [image.to_json() for image in self._historical_images],
            "detectedObjects": [obj.to_json() for obj in self._detected_objects]
        }

    @classmethod
    def from_json(cls, data: Dict[str, any]) -> 'LocationMarker':
        """
        Creates a LocationMarker instance from a JSON-compatible dictionary.
        
        :param data: Dictionary with LocationMarker details.
        :return: A new LocationMarker instance.
        """
        # Initialize the instance with data converted from JSON
        instance = cls(
            name=data.get("name", None),
            coordinate=Coordinate.from_json(data.get("coordinate", {})),
            status=data.get("status", "created"),
            subscribed_emails=data.get("subscribedEmails", []),
            current_image=Image.from_json(data.get("currentImage")) if data.get("currentImage") else None,
            historical_images=[Image.from_json(img) for img in data.get("historicalImages", [])],
            detected_objects=[DetectedObjects.from_json(obj) for obj in data.get("detectedObjects", [])]
        )
        # Set the marker ID and creation date
        instance.set_marker_id(data.get("markerId"))
        instance._date_created = datetime.fromisoformat(data["dateCreated"]) if "dateCreated" in data else datetime.now()
        return instance

    def __repr__(self) -> str:
        """
        Returns a string representation of the LocationMarker instance.
        
        :return: String representation of LocationMarker.
        """
        return (f"LocationMarker(marker_id='{self._marker_id}', "
                f"coordinate={self._coordinate}, "
                f"status='{self._status}', "
                f"date_created={self._date_created}, "
                f"subscribed_emails={self._subscribed_emails}, "
                f"current_image={self._current_image}, "
                f"historical_images={self._historical_images}, "
                f"detected_objects={self._detected_objects})")

    def _validate_email(self) -> None:
        """
        Validates email addresses using a regular expression.
        
        :raises ValueError: If any email is invalid.
        """
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        for email in self._subscribed_emails:
            if not re.match(email_pattern, email):
                raise ValueError(f"Invalid email address: {email}")

    def _validate_coordinate(self) -> None:
        """
        Validates the coordinate. Ensures it's not None and calls the `validate` method on the `Coordinate` object.

        :raises ValueError: If the coordinate is None or invalid.
        """
        if self._coordinate is None:
            raise ValueError("Coordinate cannot be None.")
        if not self._coordinate.validate():
            raise ValueError(f"Invalid coordinate: {self._coordinate}")

    def validate(self) -> None:
        """
        Validates the LocationMarker instance by checking its coordinate and subscribed emails.
        
        :raises ValueError: If any validation fails.
        """
        self._validate_coordinate()
        self._validate_email()