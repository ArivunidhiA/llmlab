/**
 * LLMLab Frontend Types
 * @description Core TypeScript interfaces for the LLMLab dashboard
 */

export interface User {
  id: string;
  email: string;
  name: string;
  github_username?: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface APIKey {
  id: string;
  key: string;
  name: string;
  prefix: string;
  last_used: string | null;
  created_at: string;
}

export interface DailyCost {
  date: string;
  cost: number;
  requests: number;
}

export interface ModelCost {
  model: string;
  cost: number;
  percentage: number;
  requests: number;
  tokens: number;
}

export interface Stats {
  today: number;
  this_month: number;
  all_time: number;
  by_model: ModelCost[];
  daily_costs: DailyCost[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface APIError {
  detail: string;
  status_code?: number;
}
