import { Card, CardBody } from "./Card";
import { formatCurrency } from "@/lib/utils";

interface CostCardProps {
  title: string;
  amount: number;
  change?: number;
  trend?: "up" | "down" | "neutral";
}

export const CostCard = ({
  title,
  amount,
  change,
  trend,
}: CostCardProps) => {
  const trendColor =
    trend === "up"
      ? "text-red-600 dark:text-red-400"
      : trend === "down"
      ? "text-green-600 dark:text-green-400"
      : "text-slate-600 dark:text-slate-400";

  return (
    <Card variant="elevated" className="h-full">
      <CardBody>
        <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
          {title}
        </p>
        <p className="text-3xl font-bold text-slate-900 dark:text-slate-50 mb-2">
          {formatCurrency(amount)}
        </p>
        {change !== undefined && (
          <p className={`text-sm font-medium flex items-center gap-1 ${trendColor}`}>
            {trend === "up" ? "↑" : trend === "down" ? "↓" : "→"}
            {Math.abs(change).toFixed(1)}% vs last month
          </p>
        )}
      </CardBody>
    </Card>
  );
};

export default CostCard;
