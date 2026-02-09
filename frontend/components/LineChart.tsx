"use client";

import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { formatCurrency } from "@/lib/utils";

interface LineChartData {
  [key: string]: any;
  date: string;
}

interface LineChartProps {
  data: LineChartData[];
  dataKey: string;
  title?: string;
  height?: number;
}

export const LineChart = ({
  data,
  dataKey,
  title,
  height = 300,
}: LineChartProps) => {
  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50 mb-4">
          {title}
        </h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsLineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.2)" />
          <XAxis
            dataKey="date"
            stroke="rgba(148, 163, 184, 0.5)"
            style={{ fontSize: "12px" }}
          />
          <YAxis
            stroke="rgba(148, 163, 184, 0.5)"
            style={{ fontSize: "12px" }}
            tickFormatter={(value) => `$${(value / 1000).toFixed(1)}k`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(15, 23, 42, 0.95)",
              border: "1px solid rgba(148, 163, 184, 0.2)",
              borderRadius: "8px",
              padding: "8px",
            }}
            labelStyle={{ color: "#f1f5f9" }}
            formatter={(value: any) => formatCurrency(value as number)}
            cursor={{ stroke: "rgba(59, 130, 246, 0.2)" }}
          />
          <Legend wrapperStyle={{ paddingTop: "20px" }} />
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ fill: "#3b82f6", r: 4 }}
            activeDot={{ r: 6 }}
          />
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LineChart;
