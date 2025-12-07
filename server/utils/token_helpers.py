import secrets
from datetime import datetime, timedelta
from typing import Dict, Any
import jwt

from server.config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def encode_access_token(subject: str) -> str:
    now = datetime.now()
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # jti: unique jwt token identifier
    jwt_token_identifier = secrets.token_urlsafe(16)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),  # issued at timestamp
        "exp": int(expire.timestamp()), # expiry timestamp (issued + 15 min)
        "jti": jwt_token_identifier
    }

    token = jwt.encode(payload=payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(jwt=token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM])
