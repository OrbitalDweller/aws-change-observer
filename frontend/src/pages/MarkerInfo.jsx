import { useParams } from "react-router-dom";
import { useGetMarker } from "@/apiQueries/queries";
import { ArrowLeft } from "lucide-react";
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

// Access environment variable
const MAP_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

const MarkerInfo = () => {
  const { markerId } = useParams();
  const { marker, isLoading, isError } = useGetMarker(markerId);

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

        <div className="flex items-center gap-2">
          <p className="text-gray-500">
            tracking created{" "}
            {formatDistanceToNow(marker.dateCreated, { addSuffix: true })}
          </p>
        </div>
      </div>

      <img
        src={mapImageUrl}
        alt="Map"
        className="rounded-lg h-96 w-full object-cover"
      />

      <h2>Latest image:</h2>
      <img
        src={marker?.currentImage?.imageURL}
        className="h-32 w-32 rounded-md"
      ></img>
    </div>
  );
};

export default MarkerInfo;
