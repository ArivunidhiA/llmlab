const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface RequestInit extends Omit<globalThis.RequestInit, "headers"> {
  headers?: Record<string, string>;
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
        window.location.href = "/login";
      }
    }
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // Auth
  signUp: (email: string, password: string, name: string) =>
    request("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    }),

  login: (email: string, password: string) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
    }
  },

  // Dashboard
  getDashboardMetrics: () =>
    request("/dashboard/metrics"),

  // API Keys
  getAPIKeys: () =>
    request("/api-keys"),

  createAPIKey: (name: string) =>
    request("/api-keys", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),

  deleteAPIKey: (id: string) =>
    request(`/api-keys/${id}`, {
      method: "DELETE",
    }),

  // Budget
  getBudgetSettings: () =>
    request("/budget"),

  updateBudgetLimit: (limit: number) =>
    request("/budget", {
      method: "PUT",
      body: JSON.stringify({ limit }),
    }),

  // Alerts
  getBudgetAlerts: () =>
    request("/alerts"),

  updateBudgetAlert: (id: string, threshold: number, email: string, enabled: boolean) =>
    request(`/alerts/${id}`, {
      method: "PUT",
      body: JSON.stringify({ threshold, email, enabled }),
    }),

  createBudgetAlert: (threshold: number, email: string) =>
    request("/alerts", {
      method: "POST",
      body: JSON.stringify({ threshold, email }),
    }),

  // User
  getUserProfile: () =>
    request("/user/profile"),

  updateUserProfile: (data: Record<string, any>) =>
    request("/user/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    }),
};

export async function pollMetrics(
  callback: (metrics: any) => void,
  interval: number = 30000
): Promise<() => void> {
  const pollId = setInterval(async () => {
    try {
      const metrics = await api.getDashboardMetrics();
      callback(metrics);
    } catch (error) {
      console.error("Failed to poll metrics:", error);
    }
  }, interval);

  return () => clearInterval(pollId);
}
