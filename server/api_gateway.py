from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from requests import Session
from sqlalchemy import inspect, func
from server.models.sql_models import Expense, User
from server.db.connect_db import Base, engine, get_db_session
from server.models.schemas import ExpenseCreate, ExpenseOut
from server.utils.tabulate_data import display_data_table
from server.utils.fastapi_app_lifespan import lifespan
from decimal import Decimal
from typing import List, Optional
from datetime import date, datetime

#from contextlib import contextmanager

router = APIRouter()
# ---------------------- methods and commands --------------------------

# POST - register new user
# POST - login new user
# POST - users/expenses -- create new expense
# PATCH -users/expenses -- update the expense
# DELETE - users/expenses -- delete the expense
# GET -- users/expenses -- list the expense


api_router_app = FastAPI(lifespan=lifespan)
"""
@api_router_app.post(path="/users/register")
def register_user():
    pass

@api_router_app.post(path="/users/login")
def login_user():
    pass
"""

# -------------------------------------------------------------------
# --------- Get Expense ---------------------------------------------
# Path Param: user_id
# Query Params: optional {category, from_date, to_date, amount}
# -------------------------------------------------------------------
@api_router_app.get(
    path="/users/{user_id}/expenses",
    response_model=List[ExpenseOut],
    status_code=status.HTTP_200_OK
)
def list_expenses(
        user_id: int,
        category: Optional[str] = None,
        lt_amount: Optional[Decimal] = None, # less than amount
        gt_amount: Optional[Decimal] = None, # greater than amount
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        sort_by: Optional[str] = None, # <-- this is sorting columns.. cols separated by comma
        sort_order: Optional[str] = None, # <-- sort order, asc or desc
        db: Session = Depends(get_db_session)
) -> List[ExpenseOut]:
    allowed_sort_cols = {
        "date": Expense.date,
        "amount": Expense.amount,
        "category": Expense.category,
        "created_at": Expense.created_at,
    }
    # Base query to filter non deleted expenses for a user
    exp_query = (
        db.query(Expense).
        filter(Expense.user_id == user_id, Expense.deleted_at == None)
    )
    print(f"Base Query:\n{exp_query}")
    # category filter: if category in query param
    if category:
        exp_query = exp_query.filter(Expense.category == category)

    # amount filter: if lt_amount / gt_amount in query param
    if lt_amount:
        exp_query = exp_query.filter(Expense.amount < lt_amount)
    if gt_amount:
        exp_query = exp_query.filter(Expense.amount > gt_amount)

    # date filter: if from_date / to_date in query param
    if from_date:
        exp_query = exp_query.filter(Expense.date >= from_date)
    if to_date:
        exp_query = exp_query.filter(Expense.date <= to_date)

    print(f"\nFilters Query:\n{[category, lt_amount, gt_amount, from_date, to_date]} -> {exp_query}")
    # ------------------------ Sorting Logic -------------------------------
    # if user specifies sort oder for each col like amount:desc&date:asc
    # if user specifies sort order with sort_order field like amount,date&asc
    if sort_by:
        sort_cols = [sort_col.strip() for sort_col in sort_by.split(",")]
        order_by_clauses = []

        for col_order in sort_cols:
            if ":" in col_order:
                col, order = col_order.split(":")
                col = col.strip()
                order = order.strip()
            else:
                col = col_order
                order = sort_order

            column = allowed_sort_cols.get(col)
            if not column:
                raise HTTPException(status_code=400, detail=f"{column} is invalid sort column, should be from {str(allowed_sort_cols)}")

            if order == "asc":
                order_by_clauses.append(column.asc())
            else:
                order_by_clauses.append(column.desc())

        exp_query = exp_query.order_by(*order_by_clauses)
    else:
        exp_query = exp_query.order_by(Expense.date.desc(), Expense.amount.desc())

    print(f"\nSort Query\n{[sort_by, sort_order]} -> {exp_query}")
    result_set = exp_query.all()
    print(result_set)
    return result_set

# -------------------------------------------------------------------
# --------- Create Expense ------------------------------------------
# Path Param: user id -> since each user owns resource (Expense)
# -------------------------------------------------------------------
@api_router_app.post(
    path="/users/{user_id}/expenses",
    response_model=ExpenseOut,
    status_code=status.HTTP_201_CREATED
)
def log_expenses(
        user_id: int,
        expense: ExpenseCreate,
        db: Session = Depends(get_db_session)
) -> ExpenseOut:
    if expense.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount should be greater than 0")

    new_expense = Expense(
        user_id=int(user_id), # <---- path parameter is inserted
        description=expense.description,
        category=expense.category,
        date=expense.date,
        amount=Decimal(str(expense.amount))
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

"""
@api_router_app.patch(path="users/{user_id}/expenses")
def update_expenses():
    pass

@api_router_app.delete(path="users/{user_id}/expenses")
def delete_expenses():
    pass

"""