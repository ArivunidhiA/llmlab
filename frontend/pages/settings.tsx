import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '../lib/hooks/useAuth'
import { apiClient } from '../lib/api'
import { Settings as SettingsIcon, ArrowLeft } from 'lucide-react'

export default function SettingsPage() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [slackWebhook, setSlackWebhook] = useState('')
  const [discordWebhook, setDiscordWebhook] = useState('')
  const [emailAlerts, setEmailAlerts] = useState(true)
  const [monthlyBudget, setMonthlyBudget] = useState('')
  const [alertChannel, setAlertChannel] = useState('email')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!user) return
    loadSettings()
  }, [user])

  const loadSettings = async () => {
    try {
      const [budgets] = await Promise.all([
        apiClient.get('/api/budgets'),
      ])
      
      if (budgets.data.length > 0) {
        setMonthlyBudget(budgets.data[0].monthly_limit)
        setAlertChannel(budgets.data[0].alert_channel)
      }
    } catch (error) {
      console.error('Failed to load settings:', error)
    }
  }

  const handleSaveWebhooks = async () => {
    setSaving(true)
    try {
      await apiClient.put('/api/webhooks', {
        slack_webhook: slackWebhook || null,
        discord_webhook: discordWebhook || null,
        email_alerts: emailAlerts,
      })
      setMessage('Webhooks saved successfully!')
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      setMessage('Failed to save webhooks')
    } finally {
      setSaving(false)
    }
  }

  const handleSaveBudget = async () => {
    if (!monthlyBudget) return
    
    setSaving(true)
    try {
      const budgets = await apiClient.get('/api/budgets')
      
      if (budgets.data.length > 0) {
        // Update existing
        await apiClient.put(`/api/budgets/${budgets.data[0].id}`, {
          monthly_limit: parseFloat(monthlyBudget),
          alert_channel: alertChannel,
        })
      } else {
        // Create new
        await apiClient.post('/api/budgets', {
          monthly_limit: parseFloat(monthlyBudget),
          alert_channel: alertChannel,
        })
      }
      setMessage('Budget saved successfully!')
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      setMessage('Failed to save budget')
    } finally {
      setSaving(false)
    }
  }

  const handleLogout = () => {
    logout()
    router.push('/')
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-black text-white">
      {/* Header */}
      <header className="px-6 py-4 border-b border-purple-800/30 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <button onClick={() => router.push('/dashboard')} className="p-2 hover:bg-purple-700 rounded-lg transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-2xl font-bold">Settings</h1>
        </div>
      </header>

      <main className="px-6 py-8 max-w-4xl mx-auto">
        {message && (
          <div className={`mb-6 px-4 py-3 rounded-lg ${message.includes('Failed') ? 'bg-red-900/30 text-red-300 border border-red-700/50' : 'bg-green-900/30 text-green-300 border border-green-700/50'}`}>
            {message}
          </div>
        )}

        {/* Budget Section */}
        <div className="bg-purple-900/30 border border-purple-700/50 p-8 rounded-lg mb-8">
          <h2 className="text-2xl font-bold mb-6">Budget Settings</h2>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">Monthly Budget (USD)</label>
              <input
                type="number"
                value={monthlyBudget}
                onChange={(e) => setMonthlyBudget(e.target.value)}
                placeholder="1000"
                className="w-full px-4 py-2 bg-purple-950 border border-purple-700 rounded-lg focus:outline-none focus:border-purple-500 transition"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Alert Channel</label>
              <select
                value={alertChannel}
                onChange={(e) => setAlertChannel(e.target.value)}
                className="w-full px-4 py-2 bg-purple-950 border border-purple-700 rounded-lg focus:outline-none focus:border-purple-500 transition"
              >
                <option value="email">Email</option>
                <option value="slack">Slack</option>
                <option value="discord">Discord</option>
              </select>
            </div>

            <button
              onClick={handleSaveBudget}
              disabled={saving || !monthlyBudget}
              className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 px-6 py-2 rounded-lg font-semibold transition"
            >
              {saving ? 'Saving...' : 'Save Budget'}
            </button>
          </div>
        </div>

        {/* Webhooks Section */}
        <div className="bg-purple-900/30 border border-purple-700/50 p-8 rounded-lg mb-8">
          <h2 className="text-2xl font-bold mb-6">Notification Webhooks</h2>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">Slack Webhook URL</label>
              <input
                type="text"
                value={slackWebhook}
                onChange={(e) => setSlackWebhook(e.target.value)}
                placeholder="https://hooks.slack.com/services/..."
                className="w-full px-4 py-2 bg-purple-950 border border-purple-700 rounded-lg focus:outline-none focus:border-purple-500 transition"
              />
              <p className="text-xs text-gray-400 mt-1">Optional: Get budget alerts in Slack</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Discord Webhook URL</label>
              <input
                type="text"
                value={discordWebhook}
                onChange={(e) => setDiscordWebhook(e.target.value)}
                placeholder="https://discord.com/api/webhooks/..."
                className="w-full px-4 py-2 bg-purple-950 border border-purple-700 rounded-lg focus:outline-none focus:border-purple-500 transition"
              />
              <p className="text-xs text-gray-400 mt-1">Optional: Get budget alerts in Discord</p>
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="emailAlerts"
                checked={emailAlerts}
                onChange={(e) => setEmailAlerts(e.target.checked)}
                className="w-4 h-4 rounded"
              />
              <label htmlFor="emailAlerts" className="text-sm">
                Send email alerts
              </label>
            </div>

            <button
              onClick={handleSaveWebhooks}
              disabled={saving}
              className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 px-6 py-2 rounded-lg font-semibold transition"
            >
              {saving ? 'Saving...' : 'Save Webhooks'}
            </button>
          </div>
        </div>

        {/* Account Section */}
        <div className="bg-purple-900/30 border border-purple-700/50 p-8 rounded-lg">
          <h2 className="text-2xl font-bold mb-6">Account</h2>
          
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-400">Email Address</p>
              <p className="font-semibold">{user.email}</p>
            </div>

            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 px-6 py-2 rounded-lg font-semibold transition"
            >
              Log Out
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
