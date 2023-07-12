import React from "react";
import { Card, Spin } from "antd";
import { useGetOrders } from "../../../../hooks/useOrders";
import { parseDateTime } from "../../../../utils/parseDateTime";

export default function Orders() {
  const [orders, isLoading, isError] = useGetOrders();

  if (isError) {
    return (
      <Card>
        <h3>Ошибка при загрузке заявок</h3>
      </Card>
    );
  }

  if (isLoading) {
    return <Spin />;
  }

  return (
    <div>
      {orders.map((order) => (
        <Card key={order.id}>
          <p>figi={order.figi}</p>
          {order.status === "CLOSE" ? (
            <p style={{ color: "red", fontWeight: 500 }}>
              status={order.status}
            </p>
          ) : (
            <p style={{ color: "green", fontWeight: 500 }}>
              status={order.status}
            </p>
          )}
          <p>probability={order.probability} %</p>
          <p>price={order.price}</p>
          <p>quantity={order.quantity}</p>
          <p>{parseDateTime(order.time)}</p>
        </Card>
      ))}
    </div>
  );
}
