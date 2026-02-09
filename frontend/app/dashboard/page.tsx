/**
 * Dashboard Page
 * @description Main dashboard with cost summary, model chart, and daily table
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Navigation from '@/components/Navigation';
import CostCard from '@/components/CostCard';
import ModelChart from '@/components/ModelChart';
import DailyTable from '@/components/DailyTable';
import { api, isAuthenticated, getUser } from '@/lib/api';
import { Stats, User } from '@/types';

// Mock data for demo/development
const MOCK_STATS: Stats = {
  today: 12.47,
  this_month: 342.89,
  all_time: 1247.56,
  by_model: [
    { model: 'gpt-4', cost: 156.23, percentage: 45.5, requests: 2341, tokens: 450000 },
    { model: 'gpt-4-turbo', cost: 89.12, percentage: 26.0, requests: 1567, tokens: 890000 },
    { model: 'gpt-3.5-turbo', cost: 45.67, percentage: 13.3, requests: 8934, tokens: 2100000 },
    { model: 'claude-3-opus', cost: 34.21, percentage: 10.0, requests: 234, tokens: 120000 },
    { model: 'claude-3-sonnet', cost: 17.66, percentage: 5.2, requests: 567, tokens: 340000 },
  ],
  daily_costs: Array.from({ length: 30 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - i);
    return {
      date: date.toISOString().split('T')[0],
      cost: Math.random() * 20 + 5,
      requests: Math.floor(Math.random() * 500 + 100),
    };
  }),
};

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  /**
   * Fetch stats from API
   */
  const fetchStats = useCallback(async () => {
    try {
      const data = await api.getStats();
      setStats(data);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      // Use mock data if API fails (for demo purposes)
      console.warn('Using mock data:', err);
      setStats(MOCK_STATS);
      setLastUpdated(new Date());
    }
  }, []);

  /**
   * Initial load and auth check
   */
  useEffect(() => {
    const init = async () => {
      // Check authentication
      if (!isAuthenticated()) {
        router.push('/');
        return;
      }

      // Load user from storage
      const storedUser = getUser();
      if (storedUser) {
        setUser(storedUser);
      }

      // Fetch initial stats
      await fetchStats();
      setIsLoading(false);
    };

    init();
  }, [router, fetchStats]);

  /**
   * Poll for updates every 5 seconds
   */
  useEffect(() => {
    if (isLoading) return;

    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, [isLoading, fetchStats]);

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
        <Navigation showUserMenu={true} />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-slate-300 border-t-slate-900 dark:border-slate-600 dark:border-t-white" />
            <p className="mt-4 text-slate-500 dark:text-slate-400">Loading dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Navigation showUserMenu={true} />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                Dashboard
              </h1>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                {user?.name ? `Welcome back, ${user.name}` : 'Your LLM cost overview'}
              </p>
            </div>
            {lastUpdated && (
              <p className="text-xs text-slate-400 dark:text-slate-500">
                Updated {lastUpdated.toLocaleTimeString()}
              </p>
            )}
          </div>
        </div>

        {/* Error banner */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Cost Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <CostCard
            title="Today"
            amount={stats?.today || 0}
            subtitle="Current day spend"
          />
          <CostCard
            title="This Month"
            amount={stats?.this_month || 0}
            subtitle="Month to date"
          />
          <CostCard
            title="All Time"
            amount={stats?.all_time || 0}
            subtitle="Total spend"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Model Chart */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              Cost by Model
            </h2>
            <ModelChart data={stats?.by_model || []} />
          </div>

          {/* Daily Costs Table */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              Daily Costs
            </h2>
            <div className="max-h-80 overflow-y-auto">
              <DailyTable data={stats?.daily_costs || []} />
            </div>
          </div>
        </div>

        {/* Model breakdown details */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            Model Breakdown
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {stats?.by_model.map((model) => (
              <div
                key={model.model}
                className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-slate-900 dark:text-white text-sm">
                    {model.model}
                  </span>
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    {model.percentage.toFixed(1)}%
                  </span>
                </div>
                <p className="text-2xl font-semibold text-slate-900 dark:text-white">
                  ${model.cost.toFixed(2)}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {model.requests.toLocaleString()} requests
                </p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
