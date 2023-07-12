import axios from "axios";
import { useState, useEffect } from "react";
import { parseDateTime } from "../utils/parseDateTime";

export function useGetCredits() {
  const [credits, setCredits] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    const fetchData = () => {
      setIsError(false);
      setIsLoading(true);
      axios
        .get("http://localhost:8000/credits")
        .then((response) => {
          const creds = response.data.map((cred) => {
            return {
              id: cred.id,
              value_rub: cred.value_rub,
              time: parseDateTime(cred.time),
            };
          });
          setCredits(creds);
          console.log(creds);
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

  return [credits, isLoading, isError];
}
