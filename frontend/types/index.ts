export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface APIKey {
  id: string;
  key: string;
  name: string;
  last_used: string | null;
  created_at: string;
}

export interface CostData {
  date: string;
  amount: number;
  model: string;
}

export interface ModelCost {
  model: string;
  cost: number;
  percentage: number;
  tokens: number;
}

export interface BudgetAlert {
  id: string;
  threshold: number;
  email: string;
  enabled: boolean;
  created_at: string;
}

export interface DashboardMetrics {
  total_spend: number;
  monthly_spend: number;
  daily_spend: number;
  budget_limit: number;
  budget_percentage: number;
  spend_by_model: ModelCost[];
  spend_trends: CostData[];
  recommendations: Recommendation[];
}

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  potential_savings: number;
  category: "optimization" | "cost_reduction" | "usage";
  priority: "low" | "medium" | "high";
}

export interface AuthResponse {
  success: boolean;
  message: string;
  token?: string;
  user?: User;
}
