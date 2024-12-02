from image_fetcher import ImageFetcher
from coordinate import Coordinate
from image import Image
from datetime import datetime
from typing import List

class ImageService:
    """
    A service class for fetching and uploading images, and creating image objects for further processing.
    """

    def __init__(self, s3_client, bucket_name: str, image_fetcher: ImageFetcher = None):
        """
        Initialize the ImageService with dependencies.

        :param s3_client: A boto3 S3 client for uploading images.
        :param bucket_name: The name of the S3 bucket.
        :param image_fetcher: An instance of ImageFetcher to handle image fetching.
        """
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.image_fetcher = image_fetcher or ImageFetcher('358ae742-66b9-4560-8834-2da11bc1dbb9', 'ycDjUjtUAI5qcSAPxCnyd7WlFynKdqcu')

    def get_latest_image(self, coordinate: Coordinate) -> Image:
        """
        Fetch the latest image for a coordinate, upload it to S3, and return an Image object.

        :param coordinate: A Coordinate object representing the location.
        :return: An Image object containing the uploaded image metadata.
        :raises ValueError: If the image fetching or uploading fails.
        """
        # Fetch the latest image
        try:
            self.image_fetcher.set_coordinates(
                coordinate.get_longitude(), coordinate.get_latitude()
            )
            png_image = self.image_fetcher.get_latest_image()
            if not png_image:
                raise ValueError("Failed to fetch image: No data returned.")
        except Exception as e:
            raise RuntimeError(f"Error fetching the latest image: {e}")

        # Upload image to S3
        try:
            s3_key = f"images/{coordinate.get_latitude()}_{coordinate.get_longitude()}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.png"
            image_url = self.upload_image_to_s3(png_image, s3_key)
        except Exception as e:
            raise RuntimeError(f"Error uploading image to S3: {e}")

        # Create an Image object
        image = self.create_image(image_url, s3_key, "Latest available image")
        return image

    def get_historical_images(self, coordinate: Coordinate) -> List[Image]:
        """
        Fetch historical images for a coordinate, upload them to S3, and return a list of Image objects.

        :param coordinate: A Coordinate object representing the location.
        :return: A list of Image objects containing the uploaded image metadata.
        :raises ValueError: If the image fetching or uploading fails.
        """
        images = []

        # Set the coordinates for the area of interest
        try:
            self.image_fetcher.set_coordinates(
                coordinate.get_longitude(), coordinate.get_latitude()
            )
        except Exception as e:
            raise RuntimeError(f"Error setting coordinates: {e}")

        # Define the historical image fetchers and their descriptions
        historical_image_fetchers = [
            (self.image_fetcher.get_image_6_months_ago, "Image from 6 months ago"),
            (self.image_fetcher.get_image_1_year_ago, "Image from 1 year ago"),
            (self.image_fetcher.get_image_2_years_ago, "Image from 2 years ago"),
            (self.image_fetcher.get_image_5_years_ago, "Image from 5 years ago"),
        ]

        # Fetch, upload, and create Image objects for each historical image
        for fetcher, description in historical_image_fetchers:
            try:
                png_image = fetcher()
                if not png_image:
                    raise ValueError(f"Failed to fetch image: No data returned for {description}")

                # Generate a unique S3 key for each image
                s3_key = f"images/{coordinate.get_latitude()}_{coordinate.get_longitude()}_{description.replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.png"
                image_url = self.upload_image_to_s3(png_image, s3_key)

                # Create an Image object with a description
                image = self.create_image(image_url, s3_key, description)
                images.append(image)
            except Exception as e:
                raise RuntimeError(f"Error processing {description}: {e}")

        return images

    def upload_image_to_s3(self, image_data: bytes, object_key: str) -> str:
        """
        Upload image data to S3 and return the public URL.

        :param image_data: The image data as bytes.
        :param object_key: The key (filename) to use for the uploaded image in S3.
        :return: The public URL of the uploaded image.
        """
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=object_key,
            Body=image_data,
            ContentType="image/png",
        )

        # Construct the public URL
        region = self.s3_client.meta.region_name
        return f"https://{self.bucket_name}.s3.{region}.amazonaws.com/{object_key}"

    def create_image(self, image_url: str, s3_key: str, description: str) -> Image:
        """
        Create an Image object with the provided metadata.

        :param description: description of the image.
        :param image_url: The URL of the uploaded image.
        :param s3_key: The S3 key where the image is stored.
        :return: An Image object.
        """

        return Image(
            description=description,
            image_url=image_url,
            s3_key=s3_key,
            s3_bucket_name=self.bucket_name
        )
