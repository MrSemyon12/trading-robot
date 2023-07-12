import React, { useState } from "react";
import { useGetCandles } from "../../../../hooks/useCandles";
import { INDICATORS, CURRENCIES } from "./constants";
import Chart from "./Chart";
import { Card, Select, Spin } from "antd";

export default function ChartCard() {
  const [indicator, setIndicator] = useState(INDICATORS[0].value);
  const [currency, setCurrency] = useState(CURRENCIES[0].value);
  const [candles, isLoading, error] = useGetCandles(currency);

  if (error)
    return (
      <Card>
        <h3>Возникла ошибка при загрузке свеч {error}</h3>
      </Card>
    );

  return (
    <Card>
      <Select
        defaultValue={indicator}
        style={{ width: 290, marginBottom: 10, marginRight: 10 }}
        onChange={(value) => setIndicator(value)}
        options={INDICATORS}
      />
      <Select
        defaultValue={currency}
        style={{ width: 220, marginBottom: 10 }}
        onChange={(value) => setCurrency(value)}
        options={CURRENCIES}
      />
      {isLoading ? <Spin /> : <Chart candles={candles} indicator={indicator} />}
    </Card>
  );
}
