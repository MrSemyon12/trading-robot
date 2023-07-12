import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function Chart({ candles, indicator }) {
  return (
    <>
      <LineChart width={1000} height={400} data={candles}>
        <Line type="monotone" dataKey="close" stroke="red" />
        <Line
          type="monotone"
          dataKey={indicator === "ema" && "ema"}
          stroke="blue"
        />
        <XAxis dataKey="time" />
        <YAxis domain={["auto", "auto"]} />
        <CartesianGrid strokeDasharray="3 3" />
        <Tooltip />
      </LineChart>
      {indicator !== "none" && indicator !== "ema" ? (
        <LineChart width={1000} height={200} data={candles}>
          <Line type="monotone" dataKey={indicator} stroke="blue" />
          <XAxis dataKey="time" />
          <YAxis domain={["auto", "auto"]} />
          <CartesianGrid strokeDasharray="3 3" />
          <Tooltip />
        </LineChart>
      ) : null}
    </>
  );
}
