import axios from "axios";
import { useState, useEffect } from "react";

export function useGetOrders() {
  const [orders, setOrders] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    const fetchData = () => {
      setIsError(false);
      setIsLoading(true);
      axios
        .get("http://localhost:8000/orders")
        .then((response) => {
          setOrders(response.data);
          console.log(response.data);
        })
        .catch(() => {
          setIsError(true);
        })
        .finally(() => setIsLoading(false));
    };

    fetchData();

    const interval = setInterval(fetchData, 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return [orders, isLoading, isError];
}
