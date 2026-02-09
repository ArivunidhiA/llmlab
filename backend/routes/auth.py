"""Authentication routes."""

from fastapi import APIRouter, HTTPException, status, Depends
from models import SignupRequest, LoginRequest, AuthResponse
from database import get_db
from utils.auth import get_password_hash, verify_password, create_access_token
from datetime import timedelta
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Mock database for demo (in production, use real Supabase)
users_db = {}


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest, db=Depends(get_db)):
    """
    User signup endpoint.
    
    Args:
        request: Signup request with email, password, and name
        db: Database client
    
    Returns:
        AuthResponse with access token
    """
    try:
        # Check if user exists
        if request.email in users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(request.password)
        
        users_db[request.email] = {
            "id": user_id,
            "email": request.email,
            "name": request.name,
            "password": hashed_password,
        }
        
        # Create token
        access_token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(hours=24)
        )
        
        logger.info(f"User signed up: {request.email}")
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db=Depends(get_db)):
    """
    User login endpoint.
    
    Args:
        request: Login request with email and password
        db: Database client
    
    Returns:
        AuthResponse with access token
    """
    try:
        # Check if user exists
        if request.email not in users_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = users_db[request.email]
        
        # Verify password
        if not verify_password(request.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create token
        access_token = create_access_token(
            data={"sub": user["id"]},
            expires_delta=timedelta(hours=24)
        )
        
        logger.info(f"User logged in: {request.email}")
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user["id"],
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/logout")
async def logout():
    """
    User logout endpoint.
    
    Note: With JWT, logout is typically handled client-side by removing the token.
    This endpoint is here for consistency.
    
    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}
