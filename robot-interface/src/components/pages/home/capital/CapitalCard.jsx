import React from "react";
import { Card, Spin } from "antd";
import { useGetCredits } from "../../../../hooks/useCredits";
import Capital from "./Capital";

export default function CapitalCard() {
  const [credits, isLoading, isError] = useGetCredits();

  if (isError)
    return (
      <Card>
        <h3>Не удалось загрузить линию капитала</h3>
      </Card>
    );

  return <Card>{isLoading ? <Spin /> : <Capital credits={credits} />}</Card>;
}
