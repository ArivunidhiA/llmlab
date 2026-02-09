"""FastAPI middleware for authentication and request handling."""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from utils.auth import decode_token
from typing import Callable, Optional
import logging
import time

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """Authentication middleware."""
    
    # Public endpoints that don't require auth
    PUBLIC_ENDPOINTS = {
        "/api/health",
        "/api/auth/signup",
        "/api/auth/login",
        "/docs",
        "/redoc",
        "/openapi.json",
    }
    
    @staticmethod
    def is_public_endpoint(path: str) -> bool:
        """Check if endpoint is public."""
        return path in AuthMiddleware.PUBLIC_ENDPOINTS or path.startswith("/api/auth")
    
    @staticmethod
    async def verify_token(request: Request) -> Optional[str]:
        """Verify JWT token from Authorization header."""
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return None
        
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return None
            
            payload = decode_token(token)
            if not payload:
                return None
            
            return payload.get("user_id")
        except ValueError:
            return None


async def auth_middleware(request: Request, call_next: Callable) -> JSONResponse:
    """Middleware to verify authentication."""
    
    # Skip auth check for public endpoints
    if AuthMiddleware.is_public_endpoint(request.url.path):
        return await call_next(request)
    
    # Verify token
    user_id = await AuthMiddleware.verify_token(request)
    
    if not user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or missing authentication token"}
        )
    
    # Attach user_id to request state
    request.state.user_id = user_id
    
    return await call_next(request)


async def request_logging_middleware(request: Request, call_next: Callable):
    """Middleware for request logging."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response
