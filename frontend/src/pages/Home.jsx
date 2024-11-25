import { useGetAllMarkers } from "@/apiQueries/queries";
import Map from "@/components/Map";
import Spinner from "@/components/ui/spinner";

const Home = () => {
  const { markers, isLoading, isError } = useGetAllMarkers();

  if (isLoading) {
    return (
      <div className="container mx-auto w-full h-[80vh] flex items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container mx-auto w-full">Error loading markers</div>
    );
  }

  return (
    <div className="container mx-auto w-full flex flex-col gap-4 items-center py-4">
      <div className="w-full">
        <Map markers={markers} />
      </div>
    </div>
  );
};

export default Home;
