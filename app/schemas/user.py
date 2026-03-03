"""
app/schemas/user.py

Purpose:
--------
Defines Pydantic schemas for User-related API requests and responses.

Owner:
------
Om (Backend / API Contracts)

Responsibilities:
-----------------
- Validate incoming user data (login, registration)
- Shape API responses (never expose hashed_password)
- Define the Token response schema for JWT auth

DO NOT:
-------
- Access database here
- Hash passwords here
- Implement authentication logic here

Reference: Technical Spec § 5.4 (Schema Layer)
"""

from pydantic import BaseModel, EmailStr


# -------------------------------------------------
# Request Schemas
# -------------------------------------------------


class UserLogin(BaseModel):
    """
    Schema used for user login.

    Used in:
    --------
    POST /auth/login

    Fields:
    -------
    - email: User email address (validated as EmailStr)
    - password: Plain-text password (never stored — passed to verify_password)
    """

    email: EmailStr
    password: str


class UserCreate(BaseModel):
    """
    Schema used when registering a new user.

    Used in:
    --------
    POST /auth/register

    Fields:
    -------
    - email: User email (validated as EmailStr)
    - password: Plain-text password (will be hashed by auth API before storage)
    """

    email: EmailStr
    password: str

    # TODO (Validation Enhancements):
    # - minimum password length (e.g. 8 chars)
    # - password complexity rules


# -------------------------------------------------
# Response Schemas
# -------------------------------------------------


class UserResponse(BaseModel):
    """
    Schema returned when user information is sent to clients.

    IMPORTANT:
    ----------
    Never include sensitive fields such as:
    - hashed_password

    Used in:
    --------
    POST /auth/register (response)
    GET  /users/me (future)
    """

    id: int
    email: EmailStr
    role: str

    class Config:
        """Enables ORM mode so SQLAlchemy models can be serialised directly."""
        orm_mode = True


class Token(BaseModel):
    """
    Schema returned after a successful login.

    Contains a signed JWT access token that the client must send
    in the Authorization header as ``Bearer <token>`` for protected routes.

    Used in:
    --------
    POST /auth/login (response)

    Fields:
    -------
    - access_token: The signed JWT string
    - token_type:   Always "bearer" (OAuth 2.0 convention)

    Reference: Technical Spec § 10.1 (Authentication)
    """

    access_token: str
    token_type: str = "bearer"
