import React from 'react'
import Link from 'next/link'
import { ArrowRight, Zap, TrendingDown, AlertCircle } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-black text-white">
      {/* Header */}
      <header className="px-4 py-6 border-b border-purple-800/30">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Zap className="w-8 h-8 text-yellow-400" />
            <h1 className="text-2xl font-bold">LLMlab</h1>
          </div>
          <nav className="flex gap-6">
            <Link href="/login" className="hover:text-purple-300 transition">
              Login
            </Link>
            <Link href="/signup" className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg transition">
              Sign Up
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="px-4 py-20 border-b border-purple-800/30">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Track LLM Costs in Real-Time
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Monitor spending across OpenAI, Anthropic, Google, and more. Get budget alerts. Optimize costs. Ship faster.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/signup" className="bg-purple-600 hover:bg-purple-700 px-8 py-3 rounded-lg font-semibold flex items-center gap-2 transition">
              Get Started Free <ArrowRight className="w-4 h-4" />
            </Link>
            <button className="border border-purple-400 hover:border-purple-300 px-8 py-3 rounded-lg font-semibold transition">
              View Docs
            </button>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="px-4 py-20">
        <div className="max-w-6xl mx-auto">
          <h3 className="text-3xl font-bold text-center mb-16">Why LLMlab?</h3>
          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-purple-900/30 border border-purple-700/50 p-8 rounded-lg hover:border-purple-500 transition">
              <Zap className="w-8 h-8 text-yellow-400 mb-4" />
              <h4 className="text-xl font-bold mb-2">Real-Time Tracking</h4>
              <p className="text-gray-400">
                See exactly how much you spend on LLMs, updated instantly across all providers.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-purple-900/30 border border-purple-700/50 p-8 rounded-lg hover:border-purple-500 transition">
              <AlertCircle className="w-8 h-8 text-red-400 mb-4" />
              <h4 className="text-xl font-bold mb-2">Smart Alerts</h4>
              <p className="text-gray-400">
                Get notified when you hit 50%, 80%, or 100% of your monthly budget via email, Slack, or Discord.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-purple-900/30 border border-purple-700/50 p-8 rounded-lg hover:border-purple-500 transition">
              <TrendingDown className="w-8 h-8 text-green-400 mb-4" />
              <h4 className="text-xl font-bold mb-2">Cost Optimization</h4>
              <p className="text-gray-400">
                Get AI-powered recommendations to save money: switch models, change providers, batch requests.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="px-4 py-20 border-t border-purple-800/30 bg-purple-900/10">
        <div className="max-w-6xl mx-auto">
          <h3 className="text-3xl font-bold text-center mb-16">3 Steps to Start</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">1</div>
              <h4 className="text-xl font-bold mb-2">Sign Up</h4>
              <p className="text-gray-400">Create a free account in 30 seconds. No credit card required.</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">2</div>
              <h4 className="text-xl font-bold mb-2">Install SDK</h4>
              <p className="text-gray-400"><code className="bg-black px-2 py-1 rounded">pip install llmlab</code> or use our webhook.</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">3</div>
              <h4 className="text-xl font-bold mb-2">Track & Optimize</h4>
              <p className="text-gray-400">Watch your dashboard in real-time. Get cost insights automatically.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-4 py-20 border-t border-purple-800/30">
        <div className="max-w-4xl mx-auto text-center">
          <h3 className="text-3xl font-bold mb-4">Ready to take control of your LLM costs?</h3>
          <p className="text-xl text-gray-300 mb-8">
            Join hundreds of AI engineers who are saving thousands with LLMlab.
          </p>
          <Link href="/signup" className="bg-purple-600 hover:bg-purple-700 px-8 py-4 rounded-lg font-semibold inline-flex items-center gap-2 transition text-lg">
            Start Free Trial <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-4 py-8 border-t border-purple-800/30 text-gray-400 text-center">
        <p>LLMlab © 2024. Built for AI engineers, by AI engineers.</p>
      </footer>
    </div>
  )
}
