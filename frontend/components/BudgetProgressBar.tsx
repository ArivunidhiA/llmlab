import { Card, CardBody } from "./Card";
import { formatCurrency, getProgressColor } from "@/lib/utils";
import Alert from "./Alert";

interface BudgetProgressBarProps {
  spent: number;
  limit: number;
  showAlert?: boolean;
}

export const BudgetProgressBar = ({
  spent,
  limit,
  showAlert = true,
}: BudgetProgressBarProps) => {
  const percentage = (spent / limit) * 100;
  const remaining = Math.max(0, limit - spent);
  const isWarning = percentage >= 80;
  const isExceeded = spent > limit;

  const progressColor = getProgressColor(percentage);

  return (
    <Card variant="elevated">
      <CardBody>
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
                Budget Status
              </h3>
              <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
                {percentage.toFixed(0)}%
              </span>
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {formatCurrency(spent)} of {formatCurrency(limit)}
            </p>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full ${progressColor} transition-all duration-300`}
              style={{ width: `${Math.min(percentage, 100)}%` }}
            />
          </div>

          {/* Status Info */}
          {isExceeded ? (
            <p className="text-sm font-medium text-red-600 dark:text-red-400">
              Budget exceeded by {formatCurrency(spent - limit)}
            </p>
          ) : (
            <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
              {formatCurrency(remaining)} remaining
            </p>
          )}

          {/* Alerts */}
          {showAlert && (isWarning || isExceeded) && (
            <Alert
              variant={isExceeded ? "error" : "warning"}
              title={isExceeded ? "Budget Exceeded" : "Budget Warning"}
              className="mt-4"
            >
              {isExceeded
                ? "Your spending has exceeded the budget limit. Review your usage and consider adjusting your settings."
                : "You've used over 80% of your monthly budget. Monitor your usage carefully."}
            </Alert>
          )}
        </div>
      </CardBody>
    </Card>
  );
};

export default BudgetProgressBar;
