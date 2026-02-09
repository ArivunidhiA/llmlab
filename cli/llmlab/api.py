"""HTTP client for LLMLab backend API."""

import time
from typing import Any, Dict, Optional

import httpx

from .config import get_token


# Backend URL - will be configurable
API_BASE_URL = "https://api.llmlab.dev"

# Request settings
TIMEOUT = 30.0
MAX_RETRIES = 3
RETRY_DELAY = 1.0


class APIError(Exception):
    """API error with status code and message."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(APIError):
    """Authentication failed."""
    pass


class NetworkError(APIError):
    """Network connectivity error."""
    pass


def get_headers() -> Dict[str, str]:
    """Get request headers with auth token if available."""
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "llmlab-cli/0.1.0",
    }
    token = get_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def request(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    retry: bool = True,
) -> Dict[str, Any]:
    """
    Make an HTTP request to the backend API.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint (e.g., "/auth/login")
        data: Request body data
        params: Query parameters
        retry: Whether to retry on failure
        
    Returns:
        Response JSON data
        
    Raises:
        APIError: On API errors
        AuthenticationError: On auth failures
        NetworkError: On network issues
    """
    url = f"{API_BASE_URL}{endpoint}"
    attempts = MAX_RETRIES if retry else 1
    last_error: Optional[Exception] = None
    
    for attempt in range(attempts):
        try:
            with httpx.Client(timeout=TIMEOUT) as client:
                response = client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=get_headers(),
                )
                
                # Handle response
                if response.status_code == 401:
                    raise AuthenticationError(
                        "Not authenticated. Run 'llmlab login' first.",
                        status_code=401,
                    )
                
                if response.status_code == 403:
                    raise AuthenticationError(
                        "Access denied. Check your permissions.",
                        status_code=403,
                    )
                
                if response.status_code >= 500:
                    raise APIError(
                        "Server error. Please try again later.",
                        status_code=response.status_code,
                    )
                
                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                        message = error_data.get("detail", error_data.get("message", "Request failed"))
                    except Exception:
                        message = response.text or "Request failed"
                    raise APIError(message, status_code=response.status_code)
                
                # Success
                if response.status_code == 204:
                    return {}
                return response.json()
                
        except httpx.ConnectError:
            last_error = NetworkError("Cannot connect to server. Check your internet connection.")
        except httpx.TimeoutException:
            last_error = NetworkError("Request timed out. Please try again.")
        except (AuthenticationError, APIError):
            raise  # Don't retry auth or API errors
        except Exception as e:
            last_error = APIError(f"Unexpected error: {str(e)}")
        
        # Wait before retry
        if attempt < attempts - 1:
            time.sleep(RETRY_DELAY * (attempt + 1))
    
    # All retries failed
    if last_error:
        raise last_error
    raise APIError("Request failed after retries")


def get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a GET request."""
    return request("GET", endpoint, params=params)


def post(endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a POST request."""
    return request("POST", endpoint, data=data)


def delete(endpoint: str) -> Dict[str, Any]:
    """Make a DELETE request."""
    return request("DELETE", endpoint)


# Specific API methods

def exchange_code(code: str) -> Dict[str, Any]:
    """Exchange OAuth code for JWT token."""
    return post("/auth/callback", {"code": code})


def get_proxy_key() -> Dict[str, Any]:
    """Get the user's proxy API key."""
    return get("/keys/proxy")


def get_stats(period: str = "month") -> Dict[str, Any]:
    """Get usage statistics."""
    return get("/stats", params={"period": period})


def store_provider_key(provider: str, key: str) -> Dict[str, Any]:
    """Store a provider API key on the backend."""
    return post("/keys/provider", {"provider": provider, "key": key})
