from typing import List, Dict

class DetectedObjects:
    def __init__(self, date_detected: str, detected_objects: List[str]):
        """
        Constructor for the DetectedObjects class.
        
        :param date_detected: Date when the objects were detected, as a string.
        :param detected_objects: List of detected objects, each as a string.
        """
        self._date_detected = date_detected
        self._detected_objects = detected_objects

    # Setters
    def set_date_detected(self, date: str):
        self._date_detected = date

    def set_detected_objects(self, detected_objects: List[str]):
        self._detected_objects = detected_objects

    # Getters
    def get_date_detected(self) -> str:
        return self._date_detected

    def get_detected_objects(self) -> List[str]:
        return self._detected_objects

    # JSON Serialization
    def to_json(self) -> Dict[str, any]:
        """
        Converts the DetectedObjects instance to a JSON-compatible dictionary.
        
        :return: Dictionary with detected objects details.
        """
        return {
            "dateDetected": self._date_detected,
            "detectedObjects": self._detected_objects
        }

    @classmethod
    def from_json(cls, data: Dict[str, any]) -> 'DetectedObjects':
        """
        Creates a DetectedObjects instance from a JSON-compatible dictionary.
        
        :param data: Dictionary with detected objects details.
        :return: A new DetectedObjects instance.
        """
        return cls(
            date_detected=data.get("dateDetected", ""),
            detected_objects=data.get("detectedObjects", [])
        )

    def __repr__(self) -> str:
        """
        Returns a string representation of the DetectedObjects instance.
        
        :return: String representation of DetectedObjects.
        """
        return (f"DetectedObjects(date_detected='{self._date_detected}', "
                f"detected_objects={self._detected_objects})")

    def compare(self, other: 'DetectedObjects') -> str:
        """
        Compares the current instance with another DetectedObjects instance.

        :param other: Another DetectedObjects instance to compare against.
        :return: A string message indicating the differences.
        """
        differences = []

        set_self_objects = set(self._detected_objects)
        set_other_objects = set(other._detected_objects)

        missing_in_other = set_self_objects - set_other_objects
        new_in_other = set_other_objects - set_self_objects

        if new_in_other:
            differences.append(f"New objects: {sorted(new_in_other)}")
        if missing_in_other:
            differences.append(f"Objects no longer detected: {sorted(missing_in_other)}")

        if not differences:
            return "No object changes."

        return "\n".join(differences)
