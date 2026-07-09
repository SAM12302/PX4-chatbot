import os
from datetime import datetime, timedelta
from typing import Optional
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 24 * 60  # 24 hours

def create_access_token(user_id: str = "anonymous") -> str:
    """Generate a JWT token for WebSocket auth."""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES),
        "iat": datetime.utcnow(),
    }
    token = encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token. Returns payload if valid, None otherwise."""
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        return None
    except InvalidTokenError:
        return None
