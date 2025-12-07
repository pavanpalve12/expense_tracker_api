# --------- Imports ---------------------------------------------
from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import Depends, APIRouter, status
from requests import Session

from server.db.connect_db import get_db_session
from server.models.schemas import ExpenseCreate, ExpenseOut, ExpenseUpdate
from server.services.expenses_services import (
    log_expense_service,
    list_expense_service,
    delete_expense_service,
    replace_expense_service,
    update_expense_service
)

# -------------------------------------------------------------------
# --------- Create Router ------------------------------------------
expense_router = APIRouter(prefix="/users", tags=["Expenses"])

# -------------------------------------------------------------------
# --------- List Expense -> GET ---------------------------------
# Path Param: user id -> since each user owns resource (Expense)
# Query Params: optional {category, from_date, to_date, amount}
# -------------------------------------------------------------------
@expense_router.get(
    path="/{user_id}/expenses"
)
def list_expense(
        user_id: int,
        db: Session = Depends(get_db_session),
        category: Optional[str] = None,
        lt_amount: Optional[Decimal] = None, # less than amount
        gt_amount: Optional[Decimal] = None, # greater than amount
        duration: Optional[str] = None, # duration can be = week, month, quarter
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        sort_by: Optional[str] = None, # <-- this is sorting columns.. cols separated by comma
        sort_order: Optional[str] = None # <-- sort order, asc or desc
) -> List[ExpenseOut]:
    return list_expense_service(
        user_id=user_id,
        db=db,
        category=category,
        lt_amount=lt_amount, gt_amount=gt_amount,
        duration=duration, from_date=from_date, to_date=to_date,
        sort_by=sort_by, sort_order=sort_order
    )

# -------------------------------------------------------------------
# --------- Create Expense -> POST -------------------------------
# Path Param: user id -> since each user owns resource (Expense)
# -------------------------------------------------------------------
@expense_router.post(
    path="/{user_id}/expenses",
    response_model=ExpenseOut,
    status_code=status.HTTP_201_CREATED
)
def log_expense(
        user_id: int,
        expense: ExpenseCreate,
        db: Session = Depends(get_db_session)
) -> ExpenseOut:
    return log_expense_service(user_id=user_id, expense=expense, db=db)

# -------------------------------------------------------------------
# --------- Replace Expense -> REPLACE -------------------------
# Path Param: user_id
# -------------------------------------------------------------------
@expense_router.put(
    path="/{user_id}/expenses/{expense_id}",
    response_model=ExpenseOut,
    status_code=status.HTTP_200_OK
)
def replace_expense(
        user_id: int,
        expense_id: int,
        expense: ExpenseCreate,
        db: Session = Depends(get_db_session)
) -> ExpenseOut:
    return replace_expense_service(user_id=user_id, expense_id=expense_id, expense=expense, db = db)

# -------------------------------------------------------------------
# --------- Update Expense -> PATCH -------------------------
# Path Param: user_id
# -------------------------------------------------------------------
@expense_router.patch(
    path="/{user_id}/expenses/{expense_id}"
)
def update_expense(
        user_id: int,
        expense_id: int,
        expense: ExpenseUpdate,
        db: Session = Depends(get_db_session)
) -> ExpenseOut:
    return update_expense_service(
        user_id=user_id, expense_id=expense_id,
        expense=expense,
        db = db
    )

# -------------------------------------------------------------------
# --------- Delete Expense -> DELETE ------------------------------
# Path Param: user_id
# -------------------------------------------------------------------
@expense_router.delete(
    path="/{user_id}/expenses/{expense_id}",
    response_model=ExpenseOut,
    status_code=status.HTTP_200_OK
)
def delete_expense(
        user_id: int,
        expense_id: int,
        db: Session = Depends(get_db_session)
) -> ExpenseOut:
    return delete_expense_service(user_id=user_id, expense_id=expense_id, db=db)

