import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '../lib/hooks/useAuth'
import { apiClient } from '../lib/api'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, AlertCircle, Settings, LogOut, Zap } from 'lucide-react'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [costSummary, setCostSummary] = useState(null)
  const [budgets, setBudgets] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    fetchData()
  }, [user])

  const fetchData = async () => {
    try {
      const [summary, budgetList, recs] = await Promise.all([
        apiClient.get('/api/costs/summary'),
        apiClient.get('/api/budgets'),
        apiClient.get('/api/recommendations'),
      ])
      
      setCostSummary(summary.data)
      setBudgets(budgetList.data)
      setRecommendations(recs.data)
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    router.push('/')
  }

  if (!user || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-900 to-purple-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-black text-white">
      {/* Header */}
      <header className="px-6 py-4 border-b border-purple-800/30 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Zap className="w-8 h-8 text-yellow-400" />
          <h1 className="text-2xl font-bold">LLMlab Dashboard</h1>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-gray-300">{user.email}</span>
          <button onClick={() => router.push('/settings')} className="p-2 hover:bg-purple-700 rounded-lg transition">
            <Settings className="w-5 h-5" />
          </button>
          <button onClick={handleLogout} className="p-2 hover:bg-purple-700 rounded-lg transition">
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </header>

      <main className="px-6 py-8 max-w-7xl mx-auto">
        {/* Summary Cards */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card title="Today" value={`$${costSummary?.today || 0}`} icon="💵" />
          <Card title="This Week" value={`$${costSummary?.this_week || 0}`} icon="📊" />
          <Card title="This Month" value={`$${costSummary?.this_month || 0}`} icon="📈" />
          <Card title="Total" value={`$${costSummary?.total || 0}`} icon="💰" />
        </div>

        {/* Budget Section */}
        {budgets.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Budget</h2>
            <div className="bg-purple-900/30 border border-purple-700/50 p-6 rounded-lg">
              {budgets.map(budget => (
                <BudgetProgressBar key={budget.id} budget={budget} />
              ))}
            </div>
          </div>
        )}

        {/* Charts */}
        <div className="grid md:grid-cols-2 gap-8 mb-8">
          {/* Spend by Provider */}
          {costSummary?.by_provider && (
            <div className="bg-purple-900/30 border border-purple-700/50 p-6 rounded-lg">
              <h3 className="text-lg font-bold mb-4">Spend by Provider</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={Object.entries(costSummary.by_provider).map(([provider, cost]) => ({
                  name: provider,
                  cost: parseFloat(cost)
                }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                  <XAxis dataKey="name" stroke="#999" />
                  <YAxis stroke="#999" />
                  <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #444' }} />
                  <Bar dataKey="cost" fill="#8b5cf6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Spend Trends */}
          {costSummary?.by_day && (
            <div className="bg-purple-900/30 border border-purple-700/50 p-6 rounded-lg">
              <h3 className="text-lg font-bold mb-4">Daily Spend Trend</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={Object.entries(costSummary.by_day).map(([date, cost]) => ({
                  date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                  cost: parseFloat(cost)
                }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                  <XAxis dataKey="date" stroke="#999" />
                  <YAxis stroke="#999" />
                  <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #444' }} />
                  <Line type="monotone" dataKey="cost" stroke="#8b5cf6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Cost Optimization Tips</h2>
            <div className="space-y-4">
              {recommendations.map((rec, idx) => (
                <div key={idx} className="bg-purple-900/30 border border-purple-700/50 p-4 rounded-lg hover:border-purple-500 transition">
                  <div className="flex gap-4">
                    <AlertCircle className="w-6 h-6 text-yellow-400 flex-shrink-0 mt-1" />
                    <div className="flex-1">
                      <h4 className="font-bold">{rec.title}</h4>
                      <p className="text-gray-300 text-sm">{rec.description}</p>
                      <div className="mt-2 text-sm">
                        <span className="text-green-400">💰 Save: ${rec.potential_savings}/month</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

function Card({ title, value, icon }) {
  return (
    <div className="bg-purple-900/30 border border-purple-700/50 p-6 rounded-lg hover:border-purple-500 transition">
      <p className="text-gray-400 text-sm mb-2">{title}</p>
      <p className="text-3xl font-bold">{value}</p>
      <p className="text-2xl mt-2">{icon}</p>
    </div>
  )
}

function BudgetProgressBar({ budget }) {
  const percentage = budget.percentage_used
  const isWarning = percentage >= 80
  const isCritical = percentage >= 100

  return (
    <div className="mb-4 last:mb-0">
      <div className="flex justify-between mb-2">
        <span className="font-semibold">Monthly Budget</span>
        <span className={isWarning ? 'text-red-400' : 'text-gray-300'}>
          ${budget.current_spend.toFixed(2)} / ${budget.monthly_limit.toFixed(2)}
        </span>
      </div>
      <div className="w-full bg-purple-950 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full transition-all ${isCritical ? 'bg-red-500' : isWarning ? 'bg-yellow-500' : 'bg-green-500'}`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        ></div>
      </div>
      <div className="text-sm text-gray-400 mt-1">{percentage.toFixed(1)}% used</div>
    </div>
  )
}
