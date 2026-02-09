"use client";

import { useState, useEffect } from "react";
import Header from "@/components/Header";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Alert from "@/components/Alert";
import { Card, CardBody, CardHeader, CardFooter } from "@/components/Card";
import { api } from "@/lib/api";
import { APIKey, BudgetAlert, User } from "@/types";
import { copyToClipboard, formatDate } from "@/lib/utils";

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null);
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [budgetLimit, setBudgetLimit] = useState(2000);
  const [budgetAlerts, setBudgetAlerts] = useState<BudgetAlert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [newKeyName, setNewKeyName] = useState("");
  const [showNewKeyInput, setShowNewKeyInput] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Mock user for demo
  const mockUser: User = {
    id: "1",
    email: "user@example.com",
    name: "John Doe",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  const mockApiKeys: APIKey[] = [
    {
      id: "key_1",
      key: "sk-proj-abc123def456ghi789",
      name: "Production",
      last_used: new Date().toISOString(),
      created_at: new Date().toISOString(),
    },
    {
      id: "key_2",
      key: "sk-proj-xyz789uvw456qrs123",
      name: "Development",
      last_used: new Date(Date.now() - 86400000).toISOString(),
      created_at: new Date(Date.now() - 2592000000).toISOString(),
    },
  ];

  const mockAlerts: BudgetAlert[] = [
    {
      id: "alert_1",
      threshold: 1500,
      email: "user@example.com",
      enabled: true,
      created_at: new Date().toISOString(),
    },
    {
      id: "alert_2",
      threshold: 1800,
      email: "user@example.com",
      enabled: false,
      created_at: new Date().toISOString(),
    },
  ];

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setIsLoading(true);
      // In production, these would be API calls
      setUser(mockUser);
      setApiKeys(mockApiKeys);
      setBudgetAlerts(mockAlerts);
    } catch (error) {
      console.error("Failed to load settings:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateApiKey = async () => {
    if (!newKeyName.trim()) return;

    try {
      setIsSaving(true);
      // In production: const response = await api.createAPIKey(newKeyName);
      const newKey: APIKey = {
        id: `key_${Date.now()}`,
        key: `sk-proj-${Math.random().toString(36).substr(2, 20)}`,
        name: newKeyName,
        last_used: null,
        created_at: new Date().toISOString(),
      };

      setApiKeys([...apiKeys, newKey]);
      setNewKeyName("");
      setShowNewKeyInput(false);
      setSuccessMessage("API key created successfully");
      setTimeout(() => setSuccessMessage(""), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteApiKey = async (id: string) => {
    if (!confirm("Are you sure you want to delete this API key?")) return;

    try {
      setIsSaving(true);
      // In production: await api.deleteAPIKey(id);
      setApiKeys(apiKeys.filter((key) => key.id !== id));
      setSuccessMessage("API key deleted");
      setTimeout(() => setSuccessMessage(""), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCopyKey = async (key: string, id: string) => {
    const success = await copyToClipboard(key);
    if (success) {
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    }
  };

  const handleSaveBudget = async () => {
    try {
      setIsSaving(true);
      // In production: await api.updateBudgetLimit(budgetLimit);
      setSuccessMessage("Budget limit updated successfully");
      setTimeout(() => setSuccessMessage(""), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleAlert = async (id: string, currentState: boolean) => {
    try {
      const alert = budgetAlerts.find((a) => a.id === id);
      if (!alert) return;

      // In production: await api.updateBudgetAlert(id, alert.threshold, alert.email, !currentState);
      setBudgetAlerts(
        budgetAlerts.map((a) =>
          a.id === id ? { ...a, enabled: !a.enabled } : a
        )
      );
      setSuccessMessage(
        `Alert ${!currentState ? "enabled" : "disabled"} successfully`
      );
      setTimeout(() => setSuccessMessage(""), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <>
        <Header showNav={true} user={user || undefined} />
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin">
              <svg className="w-12 h-12 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              </svg>
            </div>
            <p className="mt-4 text-slate-600 dark:text-slate-400">Loading settings...</p>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Header showNav={true} user={user || undefined} />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-slate-50 mb-2">
            Settings
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Manage your API keys, budget, and alerts
          </p>
        </div>

        {successMessage && (
          <Alert variant="success" title="Success" className="mb-6">
            {successMessage}
          </Alert>
        )}

        {/* API Keys Section */}
        <Card variant="elevated" className="mb-8">
          <CardHeader title="API Keys" subtitle="Manage your integration keys" />
          <CardBody className="space-y-4">
            {apiKeys.length > 0 ? (
              <div className="space-y-3">
                {apiKeys.map((apiKey) => (
                  <div
                    key={apiKey.id}
                    className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700"
                  >
                    <div className="flex-1">
                      <p className="font-semibold text-slate-900 dark:text-slate-50">
                        {apiKey.name}
                      </p>
                      <p className="text-sm text-slate-500 dark:text-slate-400 font-mono">
                        {apiKey.key.substring(0, 10)}...{apiKey.key.substring(apiKey.key.length - 10)}
                      </p>
                      {apiKey.last_used && (
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                          Last used: {formatDate(apiKey.last_used)}
                        </p>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleCopyKey(apiKey.key, apiKey.id)}
                      >
                        {copiedId === apiKey.id ? "Copied!" : "Copy"}
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDeleteApiKey(apiKey.id)}
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center py-8 text-slate-500 dark:text-slate-400">
                No API keys yet
              </p>
            )}

            {showNewKeyInput ? (
              <div className="space-y-3 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                <Input
                  label="Key Name"
                  placeholder="e.g., Production, Development"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                />
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    isLoading={isSaving}
                    onClick={handleCreateApiKey}
                  >
                    Create Key
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      setShowNewKeyInput(false);
                      setNewKeyName("");
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <Button
                variant="secondary"
                className="w-full"
                onClick={() => setShowNewKeyInput(true)}
              >
                Create New Key
              </Button>
            )}
          </CardBody>
        </Card>

        {/* Budget Settings */}
        <Card variant="elevated" className="mb-8">
          <CardHeader title="Budget" subtitle="Set your monthly spending limit" />
          <CardBody>
            <Input
              label="Monthly Budget Limit"
              type="number"
              value={budgetLimit}
              onChange={(e) => setBudgetLimit(parseFloat(e.target.value))}
              helper="Set a monthly limit for your AI API spending"
            />
          </CardBody>
          <CardFooter>
            <Button
              isLoading={isSaving}
              onClick={handleSaveBudget}
            >
              Save Budget
            </Button>
          </CardFooter>
        </Card>

        {/* Budget Alerts */}
        <Card variant="elevated">
          <CardHeader title="Budget Alerts" subtitle="Get notified when spending reaches thresholds" />
          <CardBody className="space-y-4">
            {budgetAlerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700"
              >
                <div className="flex-1">
                  <p className="font-semibold text-slate-900 dark:text-slate-50">
                    Alert at ${alert.threshold}
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {alert.email}
                  </p>
                </div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={alert.enabled}
                    onChange={() => handleToggleAlert(alert.id, alert.enabled)}
                    className="w-4 h-4 rounded border-slate-300 dark:border-slate-600 text-blue-600"
                  />
                  <span className="text-sm text-slate-600 dark:text-slate-400">
                    {alert.enabled ? "Enabled" : "Disabled"}
                  </span>
                </label>
              </div>
            ))}
          </CardBody>
        </Card>
      </main>
    </>
  );
}
