from datetime import datetime, timedelta, timezone
from jose import jwt
from pwdlib import PasswordHash

# Modern Argon2 hasher - better than bcrypt for high-end hardware
password_hash = PasswordHash.recommended()

SECRET_KEY = "your-ultra-secret-key" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against a hash."""
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generates a secure hash using Argon2ID."""
    return password_hash.hash(password)

def create_access_token(user_id: int) -> str:
    """Creates a stateless JWT."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(user_id)}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)