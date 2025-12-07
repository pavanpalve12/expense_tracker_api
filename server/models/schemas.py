from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional

# -------------------------------------------
# --- Request Schema: Client ----> Server
# -------------------------------------------
class ExpenseCreate(BaseModel):
    user_id: int
    category: str
    amount: float
    description: Optional[str] = None
    date: date

# -------------------------------------------
# -- Response Schema: Server ----> Client
# -------------------------------------------
class ExpenseOut(BaseModel):
    id: int
    user_id: int
    category: str
    amount: float
    description: Optional[str] = None
    date: date
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    model_config = {"from_attributes": True}