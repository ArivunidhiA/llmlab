"use client";

import { useState, useEffect } from "react";
import Header from "@/components/Header";
import CostCard from "@/components/CostCard";
import BarChart from "@/components/BarChart";
import LineChart from "@/components/LineChart";
import BudgetProgressBar from "@/components/BudgetProgressBar";
import { Card, CardBody, CardHeader } from "@/components/Card";
import Alert from "@/components/Alert";
import { api, pollMetrics } from "@/lib/api";
import { DashboardMetrics, User } from "@/types";
import { formatCurrency } from "@/lib/utils";

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      setError("");

      // Load metrics
      const metricsData = await api.getDashboardMetrics();
      setMetrics(metricsData);

      // Load user (for demo, using mock data)
      const mockUser: User = {
        id: "1",
        email: "user@example.com",
        name: "John Doe",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setUser(mockUser);

      // Start polling for updates
      const unsubscribe = await pollMetrics(
        (newMetrics) => setMetrics(newMetrics),
        30000 // Poll every 30 seconds
      );

      return () => unsubscribe();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load dashboard data"
      );
      // Demo data fallback
      setMetrics(getMockMetrics());
      setUser({
        id: "1",
        email: "user@example.com",
        name: "John Doe",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!user || !metrics) {
    return (
      <>
        <Header showNav={true} user={user || undefined} />
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin">
              <svg
                className="w-12 h-12 text-blue-600"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
            <p className="mt-4 text-slate-600 dark:text-slate-400">
              Loading dashboard...
            </p>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Header showNav={true} user={user} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-slate-50 mb-2">
            Dashboard
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Welcome back, {user.name}. Here's your AI cost overview.
          </p>
        </div>

        {/* Alerts */}
        {error && (
          <Alert variant="warning" title="Data Loading" className="mb-6">
            {error}
          </Alert>
        )}

        {/* Cost Cards */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <CostCard
            title="Total Spend"
            amount={metrics.total_spend}
            change={15.3}
            trend="up"
          />
          <CostCard
            title="This Month"
            amount={metrics.monthly_spend}
            change={8.2}
            trend="up"
          />
          <CostCard
            title="Today"
            amount={metrics.daily_spend}
            change={-2.5}
            trend="down"
          />
          <CostCard
            title="Budget Remaining"
            amount={Math.max(
              0,
              metrics.budget_limit - metrics.monthly_spend
            )}
            change={0}
            trend="neutral"
          />
        </div>

        {/* Budget Status and Charts Grid */}
        <div className="grid lg:grid-cols-3 gap-8 mb-8">
          {/* Budget Progress */}
          <div className="lg:col-span-1">
            <BudgetProgressBar
              spent={metrics.monthly_spend}
              limit={metrics.budget_limit}
              showAlert={true}
            />
          </div>

          {/* Spend by Model */}
          <div className="lg:col-span-2">
            <Card variant="elevated">
              <CardHeader title="Spend by Model" />
              <CardBody>
                <BarChart
                  data={metrics.spend_by_model.map((item) => ({
                    name: item.model,
                    cost: item.cost,
                  }))}
                  dataKey="cost"
                  height={300}
                />
              </CardBody>
            </Card>
          </div>
        </div>

        {/* Spend Trends */}
        <div className="mb-8">
          <Card variant="elevated">
            <CardHeader title="Spend Trends" subtitle="Last 30 days" />
            <CardBody>
              <LineChart
                data={metrics.spend_trends.map((item) => ({
                  date: item.date,
                  amount: item.amount,
                }))}
                dataKey="amount"
                height={350}
              />
            </CardBody>
          </Card>
        </div>

        {/* Recommendations */}
        <div className="grid lg:grid-cols-2 gap-8">
          <Card variant="elevated">
            <CardHeader title="Recommendations" subtitle="Save up to 40% on costs" />
            <CardBody>
              {metrics.recommendations.length > 0 ? (
                <div className="space-y-4">
                  {metrics.recommendations.slice(0, 5).map((rec) => (
                    <div
                      key={rec.id}
                      className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-700 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-semibold text-slate-900 dark:text-slate-50">
                          {rec.title}
                        </h4>
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            rec.priority === "high"
                              ? "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400"
                              : rec.priority === "medium"
                              ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400"
                              : "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400"
                          }`}
                        >
                          {rec.priority}
                        </span>
                      </div>
                      <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                        {rec.description}
                      </p>
                      <p className="text-sm font-semibold text-green-600 dark:text-green-400">
                        Save {formatCurrency(rec.potential_savings)}/month
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center py-8 text-slate-500 dark:text-slate-400">
                  No recommendations at the moment
                </p>
              )}
            </CardBody>
          </Card>

          {/* Model Usage Details */}
          <Card variant="elevated">
            <CardHeader title="Model Usage" subtitle="Cost breakdown" />
            <CardBody>
              <div className="space-y-3">
                {metrics.spend_by_model.map((model) => (
                  <div
                    key={model.model}
                    className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-800"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-slate-900 dark:text-slate-50">
                        {model.model}
                      </p>
                      <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 mt-1">
                        <div
                          className="bg-blue-500 h-full rounded-full"
                          style={{ width: `${model.percentage}%` }}
                        />
                      </div>
                    </div>
                    <div className="ml-4 text-right">
                      <p className="font-semibold text-slate-900 dark:text-slate-50">
                        {formatCurrency(model.cost)}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {model.percentage.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>
      </main>
    </>
  );
}

// Mock data for demo
function getMockMetrics(): DashboardMetrics {
  return {
    total_spend: 4250.5,
    monthly_spend: 1240.75,
    daily_spend: 42.15,
    budget_limit: 2000,
    budget_percentage: 62.04,
    spend_by_model: [
      { model: "GPT-4", cost: 520.5, percentage: 41.9, tokens: 1250000 },
      { model: "Claude-3", cost: 380.25, percentage: 30.6, tokens: 950000 },
      { model: "GPT-3.5", cost: 240.0, percentage: 19.3, tokens: 2100000 },
      { model: "Llama-2", cost: 100.0, percentage: 8.2, tokens: 500000 },
    ],
    spend_trends: [
      { date: "Jan 1", amount: 35, model: "all" },
      { date: "Jan 5", amount: 45, model: "all" },
      { date: "Jan 10", amount: 38, model: "all" },
      { date: "Jan 15", amount: 52, model: "all" },
      { date: "Jan 20", amount: 48, model: "all" },
      { date: "Jan 25", amount: 42, model: "all" },
      { date: "Jan 30", amount: 50, model: "all" },
    ],
    recommendations: [
      {
        id: "1",
        title: "Switch 30% GPT-4 to GPT-3.5",
        description:
          "Reduce costs by using GPT-3.5 for less complex tasks while maintaining quality.",
        potential_savings: 156.15,
        category: "cost_reduction",
        priority: "high",
      },
      {
        id: "2",
        title: "Optimize prompt caching",
        description:
          "Implement prompt caching to reduce redundant API calls by 25%.",
        potential_savings: 310.19,
        category: "optimization",
        priority: "high",
      },
      {
        id: "3",
        title: "Batch process requests",
        description: "Combine multiple requests into batch operations for 15% savings.",
        potential_savings: 186.11,
        category: "optimization",
        priority: "medium",
      },
    ],
  };
}
