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
- Validate incoming user data
- Shape API responses
- Protect sensitive fields (e.g., passwords)

DO NOT:
-------
- Access database here
- Hash passwords here
- Implement authentication logic here
"""

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """
    Schema used when creating a new user.

    Used in:
    --------
    POST /auth/register

    Fields:
    -------
    - email: User email (validated)
    - password: Plain password (will be hashed later)
    """

    email: EmailStr
    password: str

    # TODO (Validation Enhancements):
    # - minimum password length
    # - password complexity rules


class UserLogin(BaseModel):
    """
    Schema used for user login.

    Used in:
    --------
    POST /auth/login
    """

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Schema used when returning user information to clients.

    IMPORTANT:
    ----------
    Never include sensitive fields like:
    - hashed_password
    """

    id: int
    email: EmailStr
    role: str

    class Config:
        """
        Enables ORM compatibility.
        """
        orm_mode = True
