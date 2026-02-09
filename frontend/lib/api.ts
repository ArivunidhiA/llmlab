/**
 * LLMLab API Client
 * @description HTTP client with JWT auth, auto-logout on 401, and error handling
 */

import { Stats, APIKey, User, AuthResponse, APIError } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Get the stored JWT token
 */
function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('llmlab_token');
}

/**
 * Store JWT token
 */
export function setToken(token: string): void {
  localStorage.setItem('llmlab_token', token);
}

/**
 * Remove JWT token and redirect to login
 */
export function logout(): void {
  localStorage.removeItem('llmlab_token');
  localStorage.removeItem('llmlab_user');
  window.location.href = '/';
}

/**
 * Store user data
 */
export function setUser(user: User): void {
  localStorage.setItem('llmlab_user', JSON.stringify(user));
}

/**
 * Get stored user data
 */
export function getUser(): User | null {
  if (typeof window === 'undefined') return null;
  const data = localStorage.getItem('llmlab_user');
  return data ? JSON.parse(data) : null;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getToken();
}

/**
 * API fetch wrapper with auth and error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Auto-logout on 401
  if (response.status === 401) {
    logout();
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    const error: APIError = await response.json().catch(() => ({ 
      detail: 'An error occurred' 
    }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Exchange GitHub OAuth code for JWT token
 */
export async function githubCallback(code: string): Promise<AuthResponse> {
  return apiFetch<AuthResponse>('/auth/github/callback', {
    method: 'POST',
    body: JSON.stringify({ code }),
  });
}

/**
 * Get user's cost statistics
 */
export async function getStats(): Promise<Stats> {
  return apiFetch<Stats>('/api/v1/stats');
}

/**
 * Get user's API keys
 */
export async function getKeys(): Promise<APIKey[]> {
  return apiFetch<APIKey[]>('/api/v1/keys');
}

/**
 * Create a new API key
 */
export async function createKey(name: string): Promise<APIKey> {
  return apiFetch<APIKey>('/api/v1/keys', {
    method: 'POST',
    body: JSON.stringify({ name }),
  });
}

/**
 * Delete an API key
 */
export async function deleteKey(keyId: string): Promise<void> {
  await apiFetch<void>(`/api/v1/keys/${keyId}`, {
    method: 'DELETE',
  });
}

/**
 * Get current user info
 */
export async function getMe(): Promise<User> {
  return apiFetch<User>('/api/v1/me');
}

// Export all API functions
export const api = {
  githubCallback,
  getStats,
  getKeys,
  createKey,
  deleteKey,
  getMe,
};

export default api;
