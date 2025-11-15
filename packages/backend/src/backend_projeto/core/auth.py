"""
This module provides core authentication functionalities for the FastAPI application.

It handles:
- Password hashing and verification using `passlib`.
- JSON Web Token (JWT) creation and verification for access and refresh tokens.
- Storage and validation of refresh tokens using Redis.
- A dummy user database for demonstration purposes.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import redis # Import redis
from ..utils.config import settings

# Initialize Redis client for refresh token storage
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True # Decode responses to Python strings
)
# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings loaded from application configuration
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password.

    Args:
        plain_password (str): The plain-text password provided by the user.
        hashed_password (str): The stored hashed password.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a new JWT access token.

    Args:
        data (dict): The payload to encode into the token (e.g., {"sub": username}).
        expires_delta (Optional[timedelta]): The timedelta for token expiration.
                                             If None, uses ACCESS_TOKEN_EXPIRE_MINUTES from settings.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """
    Creates a new JWT refresh token and stores it in Redis.

    The refresh token is stored in Redis with a time-to-live (TTL)
    matching its expiration time, ensuring it can only be used once
    and is automatically invalidated.

    Args:
        data (dict): The payload to encode into the token (e.g., {"sub": username}).

    Returns:
        str: The encoded JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Store refresh token in Redis with a TTL
    # The key can be a combination of username and a hash of the token for uniqueness
    username = data.get("sub")
    if username:
        # Using the encoded_jwt itself as part of the key to ensure uniqueness per token
        redis_key = f"refresh_token:{username}:{encoded_jwt}"
        redis_client.setex(redis_key, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "true")
    
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """
    Verifies a JWT token and extracts the username from its payload.

    Args:
        token (str): The JWT token string.

    Returns:
        Optional[str]: The username if the token is valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

def verify_refresh_token(token: str) -> Optional[str]:
    """
    Verifies a JWT refresh token and checks its presence in Redis.

    This function decodes the refresh token and then verifies if it exists
    in the Redis store, ensuring it hasn't been revoked or expired.

    Args:
        token (str): The JWT refresh token string.

    Returns:
        Optional[str]: The username if the token is valid and present in Redis, otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        
        # Check if refresh token exists in Redis
        redis_key = f"refresh_token:{username}:{token}"
        if not redis_client.exists(redis_key):
            return None # Token not found or expired in Redis
            
        return username
    except JWTError:
        return None

# Dummy user database (replace with actual DB in a real application)
class User:
    """
    Represents a user in the system.

    This class is used for demonstration purposes as a dummy user database.
    In a real application, this would typically interact with a persistent database.
    """
    def __init__(self, username: str, email: str, hashed_password: str, disabled: bool = False):
        """
        Initializes a new User instance.

        Args:
            username (str): The unique username of the user.
            email (str): The email address of the user.
            hashed_password (str): The hashed password of the user.
            disabled (bool): A flag indicating if the user account is disabled. Defaults to False.
        """
        self.username: str = username
        self.email: str = email
        self.hashed_password: str = hashed_password
        self.disabled: bool = disabled

# For demonstration purposes, create a dummy user and database
dummy_user_password = get_password_hash("testpass")
dummy_users_db = {
    "testuser": User("testuser", "test@example.com", dummy_user_password),
}

def get_user(username: str) -> Optional[User]:
    """
    Retrieves a user from the dummy database by username.

    Args:
        username (str): The username of the user to retrieve.

    Returns:
        Optional[User]: The User object if found, otherwise None.
    """
    return dummy_users_db.get(username)

def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticates a user by verifying their username and password.

    Args:
        username (str): The username provided by the user.
        password (str): The plain-text password provided by the user.

    Returns:
        Optional[User]: The User object if authentication is successful, otherwise None.
    """
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# Pydantic models for token and user (can be moved to api/models.py if preferred)
from pydantic import BaseModel

class Token(BaseModel):
    """
    Pydantic model for JWT tokens.

    Attributes:
        access_token (str): The JWT access token.
        token_type (str): The type of the token (e.g., "bearer").
        refresh_token (Optional[str]): The JWT refresh token, if provided.
    """
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    """
    Pydantic model for data contained within a JWT token.

    Attributes:
        username (Optional[str]): The username extracted from the token's subject claim.
    """
    username: Optional[str] = None
