import { GoogleMap, useLoadScript, MarkerF } from "@react-google-maps/api";
import { useNavigate } from "react-router-dom";

const libraries = ["places"];
const mapContainerStyle = {
  width: "100%",
  height: "80vh",
};

const center = {
  lat: 0,
  lng: 0,
};

function Map({ markers }) {
  const navigate = useNavigate();

  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    libraries,
  });

  if (loadError) return "Error loading maps";
  if (!isLoaded) return "Loading Maps";

  return (
    <GoogleMap mapContainerStyle={mapContainerStyle} zoom={2} center={center}>
      {markers.map((marker) => {
        const lat = parseFloat(marker.coordinate.latitude) || 0;
        const lng = parseFloat(marker.coordinate.longitude) || 0;

        return (
          <MarkerF
            key={marker.markerId}
            position={{ lat, lng }}
            onClick={() => navigate(`/marker/${marker.markerId}`)}
            title={marker?.name || "Untitled Marker"}
            label={{
              text: marker.name,
              color: "black",
              className: "marker-label",
              fontSize: "14px",
              fontWeight: "bold",
              backgroundColor: "white",
              padding: "4px 8px",
              borderRadius: "4px",
              border: "1px solid #ccc",
            }}
          />
        );
      })}
    </GoogleMap>
  );
}

export default Map;
