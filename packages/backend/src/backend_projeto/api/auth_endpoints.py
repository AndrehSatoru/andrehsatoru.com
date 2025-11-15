"""
This module defines FastAPI endpoints for user authentication and token management.

It provides routes for:
- User login and generation of access and refresh tokens.
- Refreshing access tokens using a valid refresh token.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated

from backend_projeto.core.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    Token,
    User,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from backend_projeto.api.models.models import ApiErrorResponse

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """
    Authenticates a user and returns access and refresh tokens.

    Args:
        form_data (Annotated[OAuth2PasswordRequestForm, Depends()]): OAuth2 form data
                                                                     containing username and password.

    Returns:
        Token: A Pydantic model containing the access token, token type, and refresh token.

    Raises:
        HTTPException: 401 if authentication fails (incorrect username or password).
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str) -> Token:
    """
    Refreshes an access token using a valid refresh token.

    Args:
        refresh_token (str): The refresh token provided to the client.

    Returns:
        Token: A Pydantic model containing the new access token and token type.

    Raises:
        HTTPException: 401 if the refresh token is invalid.
    """
    username = verify_refresh_token(refresh_token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
