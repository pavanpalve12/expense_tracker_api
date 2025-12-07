from curses import wrapper

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, tzinfo
from passlib.context import CryptContext
from functools import wraps

from server.db.connect_db import get_db_session
from server.models.sql_models import User
from server.utils.token_helpers import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")
def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db_session)
) -> User:

    try:
        payload = decode_access_token(token=token)
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired."
        ) from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is invalid."
        )

    user_id = int(payload.get("sub"))
    token_iat = int(payload.get("iat", 0))

    user = db.query(User).filter(User.id == user_id).one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found."
        )

    # checking of token has expired / user logged out
    # check if last logout of user exists and logout is later tokem issued at, then token has expired
    if user.last_logout is not None:
        if hasattr(user.last_logout, "timestamp"):
            last_logout_ts = int(user.last_logout.replace(tzinfo = None).timestamp())
        else:
            last_logout_ts = int(user.last_logout.timestamp())

        if token_iat <= last_logout_ts:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked (user logged out)."
            )

    return user

def hash_password(password: str) -> str:
    password_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password can not be blank. Please provide password."
        )

    return password_context.hash(secret=password)

def validate_password(password: str, password_hash: str) -> bool:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return password_context.verify(secret=password, hash=password_hash)

def owner_required(func):
    """
        Decorator that enforces:
        - Request must include a valid user token
        - The authenticated user.id must match the 'user_id' path parameter
    """
    @wraps(func)
    def wrapper(
            user_id: int,
            *args,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db_session),
            **kwargs
    ):
        # Authorization check
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this resource."
            )
        # Call original endpoint with injected deps
        return func(
            user_id=user_id,
            *args,
            current_user=current_user,
            db=db,
            **kwargs
        )
    return wrapper
