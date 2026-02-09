"use client";

import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { formatCurrency } from "@/lib/utils";

interface BarChartData {
  [key: string]: any;
  name: string;
}

interface BarChartProps {
  data: BarChartData[];
  dataKey: string;
  xAxis?: string;
  title?: string;
  height?: number;
}

export const BarChart = ({
  data,
  dataKey,
  xAxis = "name",
  title,
  height = 300,
}: BarChartProps) => {
  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50 mb-4">
          {title}
        </h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsBarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.2)" />
          <XAxis
            dataKey={xAxis}
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
            cursor={{ fill: "rgba(59, 130, 246, 0.1)" }}
          />
          <Legend wrapperStyle={{ paddingTop: "20px" }} />
          <Bar dataKey={dataKey} fill="#3b82f6" radius={[8, 8, 0, 0]} />
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default BarChart;
