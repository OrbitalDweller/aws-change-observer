import { Link, Outlet, useNavigate } from "react-router-dom";
import { useState } from "react";
import PulsatingButton from "@/components/ui/pulsating-button";
import MarkerFormDialog from "@/components/MarkerFormDialog";
import { useAddMarker } from "@/apiQueries/queries";

const Layout = () => {
  const [showMarkerModal, setShowMarkerModal] = useState(false);
  const { addMarker } = useAddMarker();
  const navigate = useNavigate();

  const handleAddMarker = async (data) => {
    const newMarker = await addMarker(data);
    navigate(`/marker/${newMarker.markerId}`);
  };

  return (
    <div className="flex flex-col min-h-screen bg-white">
      <div className="w-full">
        <MarkerFormDialog
          isOpen={showMarkerModal}
          setIsOpen={setShowMarkerModal}
          onSave={handleAddMarker}
          mode="add"
        />
        <header className="sticky top-0 z-10 max-w-7xl mx-auto py-6 flex items-center justify-between">
          <Link to="/">
            <span className="text-6xl">🛰️</span>
          </Link>
          <PulsatingButton
            className="items-end"
            onClick={() => setShowMarkerModal(true)}
          >
            Track a location
          </PulsatingButton>
        </header>
      </div>

      <main className="flex-grow w-full">
        <Outlet />
      </main>

      <div className="w-full bg-white">
        <footer className="sticky bottom-0 max-w-7xl mx-auto py-6 flex items-center justify-between">
          <span>Capstone Project by Mitchell Stahl, Dmitry, Lukas, P</span>
        </footer>
      </div>
    </div>
  );
};

export default Layout;
