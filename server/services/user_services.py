from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from server.models.sql_models import User, RefreshToken
from server.models.user_schemas import (
    UserRegister, UserResponse,
    UserLogin, TokenResponse
)
from server.utils.token_helpers import (
    encode_access_token, store_hashed_refresh_token,
    generate_raw_refresh_token, hash_raw_refresh_token,
    refresh_token_expiry_datetime, revoke_all_refresh_tokens_for_user
)
from server.utils.user_helpers import hash_password, validate_password


# -------------------------------------------------------------------
# --------- Get User -> GET ------------------------------
def get_me_service(user: User) -> UserResponse:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get current user"
        )
    return UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        last_login=user.last_login
    )

# -------------------------------------------------------------------
# --------- Register User -> POST ------------------------------
def signup_user_service(
        register_user: UserRegister,
        db: Session
) -> UserResponse:

    # check if user exists in table using email address
    existing_user = (
        db.query(User).
        filter(User.email == register_user.email).
        one_or_none()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {register_user.email} found, User is already registered"
        )

    new_user = User(
        email = register_user.email,
        password_hash = hash_password(register_user.password)
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {register_user.email} found, User is already registered"
        ) from e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user."
        ) from e
    return new_user

# -------------------------------------------------------------------
# --------- Login User -> POST ------------------------------
def login_user_service(
        user: UserLogin,
        db: Session
) -> TokenResponse:
    if not user.email or not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email / password can not be blank. Please provide email address and password."
        )

    existing_user = (
        db.query(User).
        filter(User.email == user.email).
        one_or_none()
    )

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Email {user.email} not found, user is not registered, please signup first. "
        )

    if not existing_user.password_hash or not validate_password(password=user.password, password_hash=existing_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials."
        )

    existing_user.last_login = func.now()
    db.add(existing_user)

    try:
        db.commit()
        db.refresh(existing_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login user."
        )

    access_token = encode_access_token(subject=str(existing_user.id))

    # --- Generate and persist refresh token (raw -> hashed) ---
    # We will attempt a few times if a token_hash collision occurs (unique constraint)
    raw_refresh = None
    hashed_refresh = None
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        attempts += 1
        raw_refresh = generate_raw_refresh_token()
        hashed_refresh = hash_raw_refresh_token(raw_refresh)
        expires_at = refresh_token_expiry_datetime()

        try:
            refresh_token_obj = store_hashed_refresh_token(
                db=db,
                user_id=existing_user.id,
                token_hash=hashed_refresh,
                expires_at=expires_at,
                jti=None,
                user_agent=None,
                ip_addres=None
            )

            db.commit()
            db.refresh(refresh_token_obj)
            break
        except IntegrityError as e:
            db.rollback()
            if attempts >= max_attempts:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create refresh token."
                ) from e
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create refresh token."
            ) from e

    user_info = UserResponse(id=existing_user.id, email=existing_user.email)


    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        token_type="bearer",
        user_info=user_info
    )

# -------------------------------------------------------------------
# --------- Logout User -> POST ------------------------------
def logout_user_service(
        user: User,
        db: Session
) -> dict:
    user.last_logout = func.now()
    #db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User logout failed."
        )
    return {"email": user.email, "message": "user logged out successfully"}

# -------------------------------------------------------------------
# --------- refresh token -> POST ------------------------------
def refresh_token_service(
        raw_refresh_token: str,
        db: Session
) -> TokenResponse:
    if not raw_refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token required.")

    hashed = hash_raw_refresh_token(raw_refresh_token)

    # Find the refresh token (we store only hashed tokens)
    existing_rt = db.query(RefreshToken).filter(RefreshToken.token_hash == hashed).one_or_none()

    # Token not found
    if existing_rt is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

    # If the token is already revoked -> replay detected
    if existing_rt.revoked:
        # revoke all tokens for user as a safety measure
        revoke_all_refresh_tokens_for_user(db, existing_rt.user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token replay detected; all sessions revoked. Please login again.")

    # Check expiry
    now = datetime.now(timezone.utc)
    if existing_rt.expires_at.replace(tzinfo=timezone.utc) <= now:
        # Mark token revoked for hygiene
        try:
            existing_rt.revoked = True
            db.add(existing_rt)
            db.commit()
        except Exception:
            db.rollback()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token expired, please login again.")

    # All good -> rotate: mark old revoked and insert new one atomically
    # Use a DB transaction
    try:
        with db.begin():
            # mark old token revoked (optionally set revoked_at)
            existing_rt.revoked = True
            # If your model has revoked_at: existing_rt.revoked_at = func.now()

            # create new refresh token raw & hash
            new_raw = generate_raw_refresh_token()
            new_hashed = hash_raw_refresh_token(new_raw)
            new_expires = refresh_token_expiry_datetime()

            new_rt = RefreshToken(
                user_id=existing_rt.user_id,
                token_hash=new_hashed,
                expires_at=new_expires,
                revoked=False,
                jti=None,
                user_agent=None,
                ip_address=None,
            )
            db.add(new_rt)
            # transaction will commit at the end of `with db.begin()`

        # Refresh DB state
        db.refresh(new_rt)

    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to rotate refresh token.")

    # Build new access token
    access_token = encode_access_token(subject=str(existing_rt.user_id))

    # Optional: include user info
    user = db.query(User).filter(User.id == existing_rt.user_id).one_or_none()
    if user is None:
        # This should not happen, but handle defensively
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found for refresh token.")

    user_info = UserResponse(id=user.id, email=user.email)
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_raw,
        token_type="bearer",
        user_info=user_info
    )