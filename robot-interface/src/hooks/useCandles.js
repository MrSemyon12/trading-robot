import axios from "axios";
import { useState, useEffect } from "react";

export function useGetCandles(currency) {
  const [candles, setCandles] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchData = () => {
      setError(false);
      axios
        .get("http://localhost:8000/candles", {
          params: {
            figi: currency,
          },
        })
        .then((response) => {
          setCandles(response.data);
          console.log(response.data);
        })
        .catch((error) => {
          setError(error?.response?.data?.detail);
        })
        .finally(() => setIsLoading(false));
    };

    fetchData();

    const interval = setInterval(fetchData, 60 * 1000);
    return () => clearInterval(interval);
  }, [currency]);

  return [candles, isLoading, error];
}
