import { useState } from "react";
import { GoogleMap, useLoadScript, Marker } from "@react-google-maps/api";

const MapSelector = ({ onSelectLocation, initialLocation = null }) => {
  const [marker, setMarker] = useState(initialLocation);

  const { isLoaded } = useLoadScript({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
  });

  const defaultCenter = {
    lat: 30.1895,
    lng: -85.7232,
  };

  const handleMapClick = (event) => {
    const newLocation = {
      lat: event.latLng.lat(),
      lng: event.latLng.lng(),
    };
    setMarker(newLocation);
    onSelectLocation({
      latitude: newLocation.lat.toString(),
      longitude: newLocation.lng.toString(),
    });
  };

  if (!isLoaded) return <div>Loading map...</div>;

  return (
    <GoogleMap
      zoom={10}
      center={marker || defaultCenter}
      mapContainerClassName="w-full h-[300px] rounded-lg"
      onClick={handleMapClick}
    >
      {marker && <Marker position={marker} />}
    </GoogleMap>
  );
};

export default MapSelector;
