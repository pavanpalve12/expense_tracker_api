import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from http.client import HTTPException
from typing import Dict, Any, Optional
import hmac
import jwt
from sqlalchemy.orm import Session
from server.db.connect_db import get_db_session
from server.models.sql_models import RefreshToken

from server.config import (
    JWT_SECRET, JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
)

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


# generate raw refresh token
def generate_raw_refresh_token(length: int = 64) -> str:
    return secrets.token_urlsafe(length)

# hash refresh token
def hash_raw_refresh_token(raw_token: str) -> str:
    hex_encode_data = hmac.new(
        JWT_SECRET.encode('utf-8'),
        raw_token.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return hex_encode_data

# refresh token expiry datetime
def refresh_token_expiry_datetime(now: datetime | None = None) -> datetime:
    if now is None:
        now = datetime.now(timezone.utc)
    else:
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        else:
            now = now.astimezone(timezone.utc)
    expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return expires

# store hashed refresh token while login
def store_hashed_refresh_token(
        db: Session,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        jti: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
) -> RefreshToken:
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        jti=jti,
        user_agent=user_agent,
        ip_address=ip_address
    )
    db.add(refresh_token)
    db.flush()
    return refresh_token

def revoke_all_refresh_tokens_for_user(db: Session, user_id: int) -> None:
    """Helper to revoke all refresh tokens for a user (used on replay detection)."""
    try:
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id, RefreshToken.revoked == False).update(
            {RefreshToken.revoked: True}, synchronize_session=False
        )
        db.commit()
    except Exception:
        db.rollback()

