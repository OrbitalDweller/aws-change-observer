class ImageFetcher:
    """
    A class to fetch satellite images from Sentinel Hub for specified locations and date ranges.
    """

    def __init__(self, client_id, client_secret, buffer=0.005):
        """
        Initialize the fetcher with optional buffer size.

        :param client_id: Sentinel Hub Client ID.
        :param client_secret: Sentinel Hub Client Secret.
        :param buffer: Buffer distance in degrees to create the bounding box.
        """
        if not client_id or not client_secret:
            raise ValueError("Client ID and Client Secret must be provided.")
        
        self.lon = None
        self.lat = None
        self.buffer = buffer
        self.aoi = None
        self.client_id = client_id
        self.client_secret = client_secret
        self.config = self._setup_sh_config()

    def update_coordinates(self, lon, lat, buffer=None):
        """
        Update the latitude and longitude, and optionally the buffer size.

        :param lon: New longitude of the center point (-180 to 180).
        :param lat: New latitude of the center point (-90 to 90).
        :param buffer: Optional new buffer size in degrees.
        """
        try:
            if buffer is not None:
                self.buffer = buffer
            self.lon = lon
            self.lat = lat
            self.aoi = self._create_aoi(lon, lat, self.buffer)
        except ValueError as e:
            raise ValueError(f"Error updating coordinates: {e}")

    def _setup_sh_config(self):
        """
        Set up the Sentinel Hub configuration with the provided credentials.

        :return: SHConfig object with the client ID and client secret.
        """
        try:
            config = SHConfig()
            config.instance_id = None  # Not needed for OAuth authentication
            config.sh_client_id = self.client_id
            config.sh_client_secret = self.client_secret
            return config
        except Exception as e:
            raise RuntimeError(f"Failed to configure Sentinel Hub: {e}")

    @staticmethod
    def _create_aoi(lon, lat, buffer=0.005):
        """
        Create a square Area of Interest (AOI) around a given point.

        :param lon: Longitude of the center point (-180 to 180).
        :param lat: Latitude of the center point (-90 to 90).
        :param buffer: Buffer distance in degrees to create the bounding box.
        :return: Geometry object representing the AOI.
        :raises ValueError: If input parameters are out of bounds.
        """
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees.")
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if buffer <= 0:
            raise ValueError("Buffer size must be a positive value.")

        try:
            aoi_geometry = box(lon - buffer, lat - buffer, lon + buffer, lat + buffer)
            aoi_geojson = mapping(aoi_geometry)
            return Geometry(aoi_geojson, CRS.WGS84)
        except Exception as e:
            raise RuntimeError(f"Error creating AOI: {e}")

    def _create_sh_request(self, date_range):
        """
        Create a Sentinel Hub request for the given date range.

        :param date_range: Tuple of (start_date, end_date).
        :return: SentinelHubRequest object.
        """
        try:
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
            request = SentinelHubRequest(
                evalscript=evalscript,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L1C,
                        time_interval=(date_range[0].isoformat(), date_range[1].isoformat()),
                        mosaicking_order='leastCC'
                    )
                ],
                responses=[
                    SentinelHubRequest.output_response('default', MimeType.PNG)
                ],
                bbox=self.aoi.bbox,
                size=bbox_to_dimensions(self.aoi.bbox, resolution=10),
                config=self.config
            )
            return request
        except Exception as e:
            raise RuntimeError(f"Error creating Sentinel Hub request: {e}")

    def get_latest_image(self):
        """
        Fetch the latest available image.

        :return: Image data as a NumPy array, or None if not found.
        """
        try:
            start_date = datetime.utcnow().date() - timedelta(days=30)
            end_date = datetime.utcnow().date()
            date_range = (start_date, end_date)
            request = self._create_sh_request(date_range)
            data = request.get_data()
            if not data:
                raise ValueError("No image data found for the latest date range.")
            return data[0]
        except Exception as e:
            raise RuntimeError(f"Error fetching latest image: {e}")
