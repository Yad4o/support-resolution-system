"""
app/api/auth.py

Purpose:
--------
Defines authentication-related API endpoints.

Owner:
------
Om (Backend / Authentication)

Responsibilities:
-----------------
- Handle user login
- Validate credentials
- Issue JWT access tokens

DO NOT:
-------
- Store plain passwords
- Define database models here
- Implement ticket authorization logic here
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import UserLogin
from app.db.session import get_db

# TODO (later):
# from app.models.user import User
# from app.core.security import verify_password, create_access_token

router = APIRouter()


@router.post("/login")
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and issue a JWT token.

    Flow:
    -----
    1. Validate input using UserLogin schema
    2. Fetch user from database by email
    3. Verify password
    4. Create JWT access token
    5. Return token to client

    TODO (Implementation Steps):
    ----------------------------
    - Query User by email
    - If user not found → raise 401
    - Verify password using security utilities
    - Generate JWT token with user ID & role
    - Return token in response
    """

    # TODO: Fetch user from database
    # user = db.query(User).filter(User.email == credentials.email).first()

    # TODO: If user does not exist → raise HTTPException

    # TODO: Verify password
    # if not verify_password(credentials.password, user.hashed_password):
    #     raise HTTPException(status_code=401, detail="Invalid credentials")

    # TODO: Create JWT access token
    # token = create_access_token({"sub": user.id, "role": user.role})

    return {
        "access_token": "NOT_IMPLEMENTED",
        "token_type": "bearer",
    }
