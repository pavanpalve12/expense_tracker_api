from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# -------------------------------------------
# -- Request Schema: Client ----> Server
# -------------------------------------------
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# -------------------------------------------
# -- Response Schema: Server ----> Client
# -------------------------------------------
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: Optional[datetime]
    last_login: Optional[datetime]

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"



