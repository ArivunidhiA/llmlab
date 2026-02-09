"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Alert from "@/components/Alert";
import { Card, CardBody } from "@/components/Card";
import { api } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [generalError, setGeneralError] = useState("");

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) newErrors.name = "Name is required";
    if (!formData.email.trim()) newErrors.email = "Email is required";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Please enter a valid email";
    }
    if (!formData.password) newErrors.password = "Password is required";
    if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError("");

    if (!validateForm()) return;

    setIsLoading(true);
    try {
      const response = await api.signUp(
        formData.email,
        formData.password,
        formData.name
      );
      
      if (response.token) {
        localStorage.setItem("token", response.token);
        router.push("/dashboard");
      } else {
        setGeneralError(response.message || "Sign up failed");
      }
    } catch (error) {
      setGeneralError(
        error instanceof Error ? error.message : "An error occurred"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Header showNav={false} />

      <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-slate-50 dark:bg-slate-900">
        <div className="w-full max-w-md">
          <Card>
            <CardBody className="space-y-6">
              <div className="text-center">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-2">
                  Create your account
                </h1>
                <p className="text-slate-600 dark:text-slate-400">
                  Start optimizing your AI costs today
                </p>
              </div>

              {generalError && (
                <Alert variant="error" title="Error">
                  {generalError}
                </Alert>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  label="Full Name"
                  type="text"
                  placeholder="John Doe"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  error={errors.name}
                />

                <Input
                  label="Email"
                  type="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  error={errors.email}
                />

                <Input
                  label="Password"
                  type="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={(e) =>
                    setFormData({ ...formData, password: e.target.value })
                  }
                  error={errors.password}
                  helper="At least 8 characters"
                />

                <Input
                  label="Confirm Password"
                  type="password"
                  placeholder="••••••••"
                  value={formData.confirmPassword}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      confirmPassword: e.target.value,
                    })
                  }
                  error={errors.confirmPassword}
                />

                <Button
                  type="submit"
                  isLoading={isLoading}
                  className="w-full"
                >
                  Sign Up
                </Button>
              </form>

              <div className="text-center text-sm text-slate-600 dark:text-slate-400">
                Already have an account?{" "}
                <Link
                  href="/login"
                  className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
                >
                  Login here
                </Link>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </>
  );
}
