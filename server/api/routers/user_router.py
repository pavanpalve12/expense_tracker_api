from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from server.db.connect_db import get_db_session
from server.models.sql_models import User
from server.models.user_schemas import (
    UserResponse, UserRegister,
    UserLogin, TokenResponse,
    RefreshTokenRequest
)
from server.services.user_services import (
    signup_user_service,
    login_user_service,
    logout_user_service,
    get_me_service,
    refresh_token_service
)
from server.utils.user_helpers import get_current_user

user_router = APIRouter(prefix="/users", tags=["Users"])

# -------------------------------------------------------------------
# --------- Register User -> POST -------------------------------
# -------------------------------------------------------------------
@user_router.get(
    path="/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def get_me(
        current_user: User = Depends(get_current_user)
) -> UserResponse:
    return get_me_service(user = current_user)
# -------------------------------------------------------------------
# --------- Register User -> POST -------------------------------
# -------------------------------------------------------------------
@user_router.post(
    path="/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def signup_user(
        user: UserRegister,
        db: Session = Depends(get_db_session)
) -> UserResponse:
    return signup_user_service(register_user=user, db=db)

# -------------------------------------------------------------------
# --------- Login User -> POST -------------------------------
# -------------------------------------------------------------------
@user_router.post(
    path="/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
def login_user(
        user: UserLogin,
        db: Session = Depends(get_db_session)
) -> TokenResponse:
    return login_user_service(user=user, db=db)

# -------------------------------------------------------------------
# --------- Logout User -> POST -------------------------------
# -------------------------------------------------------------------
@user_router.post(
    path="/logout",
    status_code=status.HTTP_200_OK
)
def logout_user(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db_session)
) -> dict:
    return logout_user_service(user = current_user, db = db)

# -------------------------------------------------------------------
# --------- Token REFRESH -> POST -------------------------------
# -------------------------------------------------------------------
@user_router.post(
    path = "/token/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
def refresh_token(
        raw_refresh_token: RefreshTokenRequest,
        db: Session = Depends(get_db_session)
):
    return refresh_token_service(raw_refresh_token=raw_refresh_token, db=db)