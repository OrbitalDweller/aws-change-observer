import http.client
import json
from datetime import datetime, timedelta
from base64 import b64encode
from typing import List

class ImageFetcher:
    """
    A lightweight class to fetch satellite images from Sentinel Hub using http.client.
    """

    def __init__(self, client_id: str, client_secret: str, buffer: float = 0.005):
        """
        Initialize the fetcher with Sentinel Hub credentials and optional buffer size.
        :param client_id: Sentinel Hub Client ID.
        :param client_secret: Sentinel Hub Client Secret.
        :param buffer: Buffer distance in degrees to create the bounding box.
        """
        if not client_id or not client_secret:
            raise ValueError("Client ID and Client Secret are required.")
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.buffer = buffer
        self.token = self._get_access_token()
        self.aoi = None  # Area of Interest

    def _get_access_token(self) -> str:
        """
        Obtain an access token from Sentinel Hub using http.client.
        :return: Access token as a string.
        """
        conn = http.client.HTTPSConnection("services.sentinel-hub.com")
        credentials = f"{self.client_id}:{self.client_secret}"
        headers = {
            "Authorization": f"Basic {b64encode(credentials.encode()).decode()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = "grant_type=client_credentials"
        
        conn.request("POST", "/oauth/token", body=payload, headers=headers)
        response = conn.getresponse()
        if response.status != 200:
            raise Exception(f"Failed to fetch access token: {response.status} {response.reason}")
        data = json.loads(response.read())
        return data["access_token"]

    def set_coordinates(self, lon: str, lat: str):
        """
        Set the latitude and longitude of the center point for the Area of Interest (AOI).
        :param lon: Longitude as a string (-180 to 180).
        :param lat: Latitude as a string (-90 to 90).
        :raises ValueError: If the input strings cannot be converted to floats or are out of bounds.
        """
        try:
            lon = float(lon)
            lat = float(lat)
        except ValueError:
            raise ValueError("Longitude and Latitude must be valid numbers in string format.")

        if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
            raise ValueError("Coordinates are out of bounds. Longitude must be between -180 and 180, and Latitude must be between -90 and 90.")

        min_lon = lon - self.buffer
        min_lat = lat - self.buffer
        max_lon = lon + self.buffer
        max_lat = lat + self.buffer
        self.aoi = [min_lon, min_lat, max_lon, max_lat]

    def get_images_by_date(self, start_date: str, end_date: str) -> bytes:
        """
        Fetch images from a specific date range.
        
        :param start_date: Start date in "YYYY-MM-DD" format.
        :param end_date: End date in "YYYY-MM-DD" format.
        :return: Image data as bytes.
        """
        if not self.aoi:
            raise ValueError("Coordinates not set. Use set_coordinates() first.")

        conn = http.client.HTTPSConnection("services.sentinel-hub.com")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        evalscript = """
        //VERSION=3
        function setup() {
            return {
                input: ["B02", "B03", "B04"],
                output: { bands: 3 }
            };
        }

        function evaluatePixel(sample) {
            return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
        }
        """
        payload = json.dumps({
            "input": {
                "bounds": {
                    "bbox": self.aoi
                },
                "data": [
                    {
                        "type": "S2L1C",
                        "dataFilter": {
                            "timeRange": {
                                "from": f"{start_date}T00:00:00Z",
                                "to": f"{end_date}T23:59:59Z"
                            }
                        }
                    }
                ]
            },
            "output": {
                "width": 512,
                "height": 512,
                "responses": [
                    {"identifier": "default", "format": {"type": "image/png"}}
                ]
            },
            "evalscript": evalscript.strip()
        })
        
        conn.request("POST", "/api/v1/process", body=payload, headers=headers)
        response = conn.getresponse()
        if response.status != 200:
            raise Exception(f"Failed to fetch image: {response.status} {response.reason}")
        
        return response.read()

    def get_latest_image(self) -> bytes:
        """
        Fetch the latest available satellite image.
        
        :return: Image data as bytes.
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        return self.get_images_by_date(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

    def get_image_6_months_ago(self) -> bytes:
        """
        Fetch the image from 6 months ago.
        
        :return: Image data as bytes.
        """
        end_date = datetime.utcnow() - timedelta(days=30 * 6)
        start_date = end_date - timedelta(days=30)
        return self.get_images_by_date(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

    def get_image_1_year_ago(self) -> bytes:
        """
        Fetch the image from 1 year ago.
        
        :return: Image data as bytes.
        """
        end_date = datetime.utcnow() - timedelta(days=365)
        start_date = end_date - timedelta(days=30)
        return self.get_images_by_date(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

    def get_image_2_years_ago(self) -> bytes:
        """
        Fetch the image from 2 years ago.
        
        :return: Image data as bytes.
        """
        end_date = datetime.utcnow() - timedelta(days=365 * 2)
        start_date = end_date - timedelta(days=30)
        return self.get_images_by_date(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

    def get_image_5_years_ago(self) -> bytes:
        """
        Fetch the image from 5 years ago.
        
        :return: Image data as bytes.
        """
        end_date = datetime.utcnow() - timedelta(days=365 * 5)
        start_date = end_date - timedelta(days=30)
        return self.get_images_by_date(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
