from __future__ import annotations
from typing import Final
import os

from dotenv import load_dotenv
load_dotenv()

# Token Settings
JWT_SECRET: Final[str] = os.getenv(key="JWT_SECRET", default="change_this_in_prod")
JWT_ALGORITHM: Final[str] = os.getenv(key="JWT_ALGORITHM", default="HS256")

# Set Access Token expiry
ACCESS_TOKEN_EXPIRE_MINUTES: Final[str] = int(os.getenv(key="ACCESS_TOKEN_EXPIRE_MINUTES", default="15"))

# Set Refresh Token expiry
REFRESH_TOKEN_EXPIRE_DAYS: Final[str] = int(os.getenv(key="REFRESH_TOKEN_EXPIRE_DAYS", default="30"))
