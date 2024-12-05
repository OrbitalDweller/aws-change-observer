import axios from "axios";
import { toast } from "sonner";
import { useMutation, useQuery, useQueryClient } from "react-query";
import { useNavigate } from "react-router-dom";

const API_URL = "https://api.change-observer.com";

export const useAddMarker = () => {
  const queryClient = useQueryClient();
  const addMarkerRequest = async (markerData) => {
    const response = await axios.post(`${API_URL}/marker`, markerData);
    return response.data;
  };

  const {
    mutateAsync: addMarker,
    isLoading,
    isError,
    isSuccess,
  } = useMutation(addMarkerRequest, {
    onSuccess: () => {
      toast.success("Marker added successfully");
      queryClient.invalidateQueries(["markers"]);
    },
    onError: (error) => {
      toast.error(error.response?.data?.message || "Error adding marker");
      console.log(error);
    },
  });

  return { addMarker, isLoading, isError, isSuccess };
};

export const useDeleteMarker = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const deleteMarkerRequest = async (markerId) => {
    const response = await axios.delete(
      `${API_URL}/marker?markerId=${markerId}`
    );
    return response.data;
  };

  const {
    mutateAsync: deleteMarker,
    isLoading,
    isError,
    isSuccess,
  } = useMutation(deleteMarkerRequest, {
    onSuccess: () => {
      toast.success("Marker deleted successfully");
      queryClient.invalidateQueries(["markers"]);
      navigate("/");
    },
    onError: (error) => {
      toast.error(error.response?.data?.message || "Error deleting marker");
      console.log(error);
    },
  });

  return { deleteMarker, isLoading, isError, isSuccess };
};

export const useGetMarker = (markerId) => {
  const getMarkerRequest = async () => {
    const response = await axios.get(`${API_URL}/marker?markerId=${markerId}`);
    return response.data;
  };

  const {
    data: marker,
    isLoading,
    isError,
    isSuccess,
  } = useQuery(["marker", markerId], getMarkerRequest, {
    enabled: !!markerId,
    onSuccess: () => {},
    onError: (error) => {
      toast.error(error.response?.data?.message || "Error fetching marker");
      console.log(error);
    },
  });

  return { marker, isLoading, isError, isSuccess };
};

export const useGetAllMarkers = () => {
  const getAllMarkersRequest = async () => {
    const response = await axios.get(`${API_URL}/markers`);
    console.log("Full response:", response);
    console.log("Response data:", response.data);
    return response.data;
  };

  const {
    data: markers,
    isLoading,
    isError,
    isSuccess,
  } = useQuery(["markers"], getAllMarkersRequest, {
    onSuccess: () => {},
    onError: (error) => {
      toast.error(error.response?.data?.message || "Error fetching markers");
      console.log(error);
    },
  });

  return { markers, isLoading, isError, isSuccess };
};

export const useEditMarker = () => {
  const queryClient = useQueryClient();

  const editMarkerRequest = async ({ markerId, data }) => {
    const response = await axios.put(
      `${API_URL}/marker?markerId=${markerId}`,
      data
    );
    return { data: response.data, markerId };
  };

  const {
    mutateAsync: editMarker,
    isLoading,
    isError,
    isSuccess,
  } = useMutation(editMarkerRequest, {
    onSuccess: (response) => {
      toast.success("Marker edited successfully");
      queryClient.invalidateQueries(["markers"]);
      queryClient.invalidateQueries(["marker", response.markerId]);
    },
    onError: (error) => {
      toast.error(error.response?.data?.message || "Error editing marker");
      console.log(error);
    },
  });

  return { editMarker, isLoading, isError, isSuccess };
};
