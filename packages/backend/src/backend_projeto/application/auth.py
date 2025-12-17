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
import os
import hashlib
from jose import JWTError, jwt
from passlib.context import CryptContext
import redis # Import redis
from backend_projeto.infrastructure.utils.config import settings

class MockRedis:
    def __init__(self):
        self.store = {}
    
    def setex(self, name, time, value):
        self.store[name] = value
    
    def exists(self, name):
        return 1 if name in self.store else 0
        
    def get(self, name):
        return self.store.get(name)
        
    def delete(self, name):
        if name in self.store:
            del self.store[name]
            
    def ping(self):
        return True

# Initialize Redis client for refresh token storage
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True # Decode responses to Python strings
    )
    redis_client.ping()
except (redis.ConnectionError, redis.TimeoutError):
    print("Warning: Redis not available. Using in-memory mock for tokens.")
    redis_client = MockRedis()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings loaded from application configuration
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# JWT Issuer and Audience for validation
JWT_ISSUER = "andrehsatoru.com"
JWT_AUDIENCE = "andrehsatoru.com"

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
    Creates a new JWT access token with security claims (iss, aud).

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
    
    # Add standard claims for security
    to_encode.update({
        "exp": expire,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": datetime.utcnow(),
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def _hash_token(token: str) -> str:
    """Gera hash SHA-256 do token para armazenamento seguro."""
    return hashlib.sha256(token.encode()).hexdigest()

def create_refresh_token(data: dict) -> str:
    """
    Creates a new JWT refresh token and stores its hash in Redis.

    The refresh token hash is stored in Redis with a time-to-live (TTL)
    matching its expiration time. Storing only the hash prevents
    token leakage if Redis is compromised.

    Args:
        data (dict): The payload to encode into the token (e.g., {"sub": username}).

    Returns:
        str: The encoded JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": datetime.utcnow(),
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Store refresh token hash in Redis with a TTL
    username = data.get("sub")
    if username:
        # Store hash instead of raw token for security
        token_hash = _hash_token(encoded_jwt)
        redis_key = f"refresh_token:{username}:{token_hash}"
        redis_client.setex(redis_key, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "valid")
    
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """
    Verifies a JWT token and extracts the username from its payload.
    Validates signature, expiration, issuer, and audience.

    Args:
        token (str): The JWT token string.

    Returns:
        Optional[str]: The username if the token is valid, otherwise None.
    """
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={"require": ["exp", "sub", "iss", "aud"]}
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

def verify_refresh_token(token: str) -> Optional[str]:
    """
    Verifies a JWT refresh token and checks its hash presence in Redis.

    Args:
        token (str): The JWT refresh token string.

    Returns:
        Optional[str]: The username if the token is valid and present in Redis, otherwise None.
    """
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={"require": ["exp", "sub", "iss", "aud"]}
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        
        # Check if refresh token hash exists in Redis
        token_hash = _hash_token(token)
        redis_key = f"refresh_token:{username}:{token_hash}"
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
# Only create test user in development environment
if os.getenv("ENVIRONMENT", "development") == "development":
    dummy_user_password = get_password_hash("testpass")
    dummy_users_db = {
        "testuser": User("testuser", "test@example.com", dummy_user_password),
    }
else:
    dummy_users_db = {}

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
