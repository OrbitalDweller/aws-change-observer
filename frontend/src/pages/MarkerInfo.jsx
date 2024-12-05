import { useParams } from "react-router-dom";
import { ArrowLeft, Pencil, Trash } from "lucide-react";
import { Link } from "react-router-dom";
import { formatDistanceToNow } from "date-fns";
import ShinyButton from "@/components/ui/shiny-button";
import Spinner from "@/components/ui/spinner";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip";
import { useDeleteMarker } from "@/apiQueries/queries";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import MarkerFormDialog from "@/components/MarkerFormDialog";
import { useEditMarker, useGetMarker } from "@/apiQueries/queries";
// Access environment variable
const MAP_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

const formatDate = (utcDateString) => {
  const utcMs = Date.parse(utcDateString);
  const offsetMinutes = new Date().getTimezoneOffset();
  const localMs = utcMs - offsetMinutes * 60 * 1000;
  const localDate = new Date(localMs);

  const result = formatDistanceToNow(localDate, {
    addSuffix: true,
    includeSeconds: true,
  });

  return result;
};

const MarkerInfo = () => {
  const { markerId } = useParams();
  const { marker, isLoading, isError } = useGetMarker(markerId);
  const { deleteMarker } = useDeleteMarker();
  const [showEditMarkerModal, setShowEditMarkerModal] = useState(false);
  const { editMarker } = useEditMarker();

  console.log("MARKER:", marker);

  const handleEditMarker = async (data) => {
    console.log("Form data:", data);
    await editMarker({ markerId, data });
    setShowEditMarkerModal(false);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto w-full h-[80vh] flex items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (isError) return <div>Error: {isError.message}</div>;

  const mapImageUrl = `https://maps.googleapis.com/maps/api/staticmap?center=${marker.coordinate.latitude},${marker.coordinate.longitude}&zoom=16&scale=2&size=600x600&maptype=satellite&key=${MAP_API_KEY}&style=feature:poi|visibility:off`;

  return (
    <div className="container mx-auto w-full flex flex-col gap-4">
      <MarkerFormDialog
        isOpen={showEditMarkerModal}
        setIsOpen={setShowEditMarkerModal}
        onSave={(data) => handleEditMarker(data)}
        initialData={marker}
        mode="edit"
      />
      <Link to="/" className="flex items-center gap-2 group">
        <ArrowLeft className="size-4 text-gray-500 group-hover:-translate-x-1 transition-transform duration-300 ease-in-out" />
        <span className="text-base underline text-gray-500">
          Back to all markers
        </span>
      </Link>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <ShinyButton className="w-fit p-0">
                  <div className="bg-yellow-400 w-3 h-3 rounded-full shadow-2xl bg-gradient-to-b from-yellow-400 to-yellow-500"></div>
                </ShinyButton>
              </TooltipTrigger>
              <TooltipContent>
                <p>This is a tooltip</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          <h1 className="text-4xl font-bold">
            {marker?.name || "Untitled Location"} (
            {`${marker.coordinate.latitude}, ${marker.coordinate.longitude}`})
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <p className="text-gray-500">
              tracking created {formatDate(marker.dateCreated)}
            </p>
          </div>
          <Button
            className=" bg-red-100 p-4 rounded-md hover:bg-red-200 transition-colors duration-300 ease-in-out"
            onClick={() => deleteMarker(marker.markerId)}
          >
            <Trash className="text-red-900" />
          </Button>
          <Button
            className=" bg-gray-100 p-4 rounded-md hover:bg-red-200 transition-colors duration-300 ease-in-out"
            onClick={() => setShowEditMarkerModal(true)}
          >
            <Pencil className="text-gray-900" />
          </Button>
        </div>
      </div>

      <img
        src={mapImageUrl}
        alt="Map"
        className="rounded-lg h-96 w-full object-cover"
      />

      <div className="flex gap-4">
        {marker?.currentImage?.imageURL && (
          <div className="flex flex-col gap-4">
            <h2 className="text-lg font-bold">Latest image:</h2>
            <img
              src={marker.currentImage.imageURL}
              className="h-32 w-32 rounded-md border-2 border-gray-200"
            ></img>
          </div>
        )}
        <div className="flex flex-col gap-4">
          {marker?.detectedObjects?.length > 0 && (
            <h2 className="text-lg font-bold">Detected objects:</h2>
          )}
          <ul className="space-y-4">
            {marker?.detectedObjects?.map((detection, index) => (
              <li key={index} className="border rounded-md p-4">
                <p className="text-sm text-gray-500 mb-2">
                  {formatDate(detection.dateDetected)}
                </p>
                <ul className="flex flex-wrap gap-2">
                  {detection.detectedObjects.map((object, objectIndex) => (
                    <li
                      key={objectIndex}
                      className="bg-gray-100 px-3 py-1 rounded-full text-sm"
                    >
                      {object}
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        </div>
        <div className="flex flex-col gap-4">
          {marker?.historicalImages?.length > 0 && (
            <h2 className="text-lg font-bold">Historical images:</h2>
          )}
          <ul className="space-y-4">
            {marker?.historicalImages?.map((image, index) => (
              <li key={index} className="border rounded-md p-4">
                <p className="text-sm text-gray-500 mb-2">
                  {image.description}
                </p>
                <img
                  src={image.imageURL}
                  className="h-32 w-32 rounded-md border-2 border-gray-200"
                ></img>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default MarkerInfo;
