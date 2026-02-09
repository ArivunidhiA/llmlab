import Header from "@/components/Header";
import Button from "@/components/Button";
import { Card, CardBody } from "@/components/Card";
import Link from "next/link";

export default function LandingPage() {
  return (
    <>
      <Header showNav={true} />

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="text-center space-y-6 mb-16">
          <div className="inline-block px-4 py-2 bg-blue-50 dark:bg-blue-900/20 rounded-full border border-blue-200 dark:border-blue-800">
            <p className="text-sm font-medium text-blue-600 dark:text-blue-400">
              🚀 The simplest way to manage AI costs
            </p>
          </div>

          <h1 className="text-5xl sm:text-6xl font-bold text-slate-900 dark:text-slate-50 leading-tight">
            Track & Optimize Your<br />
            <span className="bg-gradient-to-r from-blue-600 to-blue-400 bg-clip-text text-transparent">
              AI Model Costs
            </span>
          </h1>

          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Real-time cost monitoring, budget alerts, and AI-powered recommendations to reduce your LLM spending.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link href="/signup">
              <Button size="lg" className="w-full sm:w-auto">
                Get Started Free
              </Button>
            </Link>
            <Link href="#features">
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                Learn More
              </Button>
            </Link>
          </div>
        </div>

        {/* Hero Image Placeholder */}
        <div className="rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-gradient-to-br from-blue-50 to-slate-50 dark:from-slate-900 dark:to-slate-950 aspect-video flex items-center justify-center">
          <div className="text-center">
            <svg
              className="w-32 h-32 mx-auto mb-4 text-slate-300 dark:text-slate-600"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" />
            </svg>
            <p className="text-slate-500 dark:text-slate-400">
              Beautiful analytics dashboard
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="bg-slate-50 dark:bg-slate-900 py-20 sm:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 dark:text-slate-50 mb-4">
              Powerful Features
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
              Everything you need to understand and reduce your LLM costs
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: "📊",
                title: "Real-Time Analytics",
                description: "Monitor your spending across all AI models in real-time with detailed breakdowns.",
              },
              {
                icon: "⚠️",
                title: "Smart Budget Alerts",
                description: "Get notified when you're approaching your budget limits with intelligent thresholds.",
              },
              {
                icon: "💡",
                title: "AI Recommendations",
                description: "Get personalized suggestions to optimize your model usage and reduce costs.",
              },
              {
                icon: "🔐",
                title: "Secure API Keys",
                description: "Safely manage your API credentials with encryption and access controls.",
              },
              {
                icon: "📈",
                title: "Trend Analysis",
                description: "Track cost trends over time and identify patterns in your spending.",
              },
              {
                icon: "🌙",
                title: "Dark Mode Support",
                description: "Comfortable viewing with automatic dark mode based on your preferences.",
              },
            ].map((feature, i) => (
              <Card key={i} variant="elevated">
                <CardBody className="space-y-3">
                  <div className="text-4xl">{feature.icon}</div>
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
                    {feature.title}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400">
                    {feature.description}
                  </p>
                </CardBody>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-slate-900 dark:text-slate-50 mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Choose the plan that fits your needs
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              name: "Starter",
              price: "Free",
              period: "",
              features: [
                "Up to 3 API keys",
                "Basic analytics",
                "Email alerts",
                "7-day history",
              ],
            },
            {
              name: "Professional",
              price: "$19",
              period: "/month",
              features: [
                "Unlimited API keys",
                "Advanced analytics",
                "Smart recommendations",
                "90-day history",
                "Custom budget alerts",
              ],
              highlighted: true,
            },
            {
              name: "Enterprise",
              price: "Custom",
              period: "",
              features: [
                "Everything in Pro",
                "Dedicated support",
                "Custom integrations",
                "Unlimited history",
                "Team management",
              ],
            },
          ].map((plan, i) => (
            <Card
              key={i}
              variant="elevated"
              className={
                plan.highlighted
                  ? "ring-2 ring-blue-500 scale-105 lg:scale-100"
                  : ""
              }
            >
              <CardBody className="space-y-6">
                <div>
                  <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-2">
                    {plan.name}
                  </h3>
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold text-slate-900 dark:text-slate-50">
                      {plan.price}
                    </span>
                    {plan.period && (
                      <span className="text-slate-600 dark:text-slate-400">
                        {plan.period}
                      </span>
                    )}
                  </div>
                </div>

                <ul className="space-y-3">
                  {plan.features.map((feature, j) => (
                    <li
                      key={j}
                      className="flex items-center gap-3 text-slate-700 dark:text-slate-300"
                    >
                      <svg
                        className="w-5 h-5 text-green-500"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>

                <Button
                  variant={plan.highlighted ? "primary" : "outline"}
                  className="w-full"
                >
                  Get Started
                </Button>
              </CardBody>
            </Card>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-400 py-16 sm:py-20 rounded-2xl mx-4 mb-20">
        <div className="max-w-2xl mx-auto text-center space-y-6">
          <h2 className="text-4xl font-bold text-white">
            Ready to optimize your AI costs?
          </h2>
          <p className="text-lg text-blue-100">
            Join thousands of teams using LLMLab to manage their LLM expenses.
          </p>
          <Link href="/signup">
            <Button
              size="lg"
              className="w-full sm:w-auto bg-white text-blue-600 hover:bg-slate-100"
            >
              Start Free Trial
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-slate-700 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-slate-600 dark:text-slate-400">
            <p>&copy; 2024 LLMLab. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </>
  );
}
