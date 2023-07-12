import { Row, Col } from "antd";
import ChartCard from "./chart/ChartCard";
import CapitalCard from "./capital/CapitalCard";
import Orders from "./orders/Orders";

export default function Home() {
  return (
    <Row>
      <Col>
        <ChartCard />
        <CapitalCard />
      </Col>
      <Col>
        <Orders />
      </Col>
    </Row>
  );
}
