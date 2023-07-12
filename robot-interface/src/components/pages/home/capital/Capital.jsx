import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

const gradientOffset = (data) => {
  const dataMax = Math.max(...data.map((i) => i.value_rub));
  const dataMin = Math.min(...data.map((i) => i.value_rub));

  if (dataMax <= 0) {
    return 0;
  }
  if (dataMin >= 0) {
    return 1;
  }

  return dataMax / (dataMax - dataMin);
};

export default function Capital({ credits }) {
  const off = gradientOffset(credits);

  return (
    <AreaChart width={1000} height={400} data={credits}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="time" />
      <YAxis domain={["auto", "auto"]} />
      <Tooltip />
      <defs>
        <linearGradient id="splitColor" x1="0" y1="0" x2="0" y2="1">
          <stop offset={off} stopColor="green" stopOpacity={1} />
          <stop offset={off} stopColor="red" stopOpacity={1} />
        </linearGradient>
      </defs>
      <Area
        type="monotone"
        dataKey="value_rub"
        stroke="#000"
        fill="url(#splitColor)"
      />
    </AreaChart>
  );
}
