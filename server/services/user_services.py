from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from server.models.sql_models import User
from server.models.user_schemas import (
    UserRegister, UserResponse,
    UserLogin, TokenResponse
)
from server.utils.token_helpers import encode_access_token
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

    return TokenResponse(access_token=access_token, token_type="bearer")

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