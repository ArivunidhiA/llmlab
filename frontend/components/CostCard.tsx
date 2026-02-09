/**
 * CostCard Component
 * @description Display a single cost metric with title and formatted amount
 */

import { formatCurrency } from '@/lib/utils';

export interface CostCardProps {
  title: string;
  amount: number;
  subtitle?: string;
}

export default function CostCard({ title, amount, subtitle }: CostCardProps) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 transition-all hover:shadow-md">
      <p className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">
        {title}
      </p>
      <p className="text-3xl font-semibold text-slate-900 dark:text-white tracking-tight">
        {formatCurrency(amount)}
      </p>
      {subtitle && (
        <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
          {subtitle}
        </p>
      )}
    </div>
  );
}
