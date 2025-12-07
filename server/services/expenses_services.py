from datetime import date
from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from server.models.schemas import ExpenseCreate, ExpenseOut, ExpenseUpdate
from server.models.sql_models import Expense
from server.utils import helpers as helpers


# -------------------------------------------------------------------
# --------- Create Expense -> POST ------------------------------
def log_expense_service(
        user_id: int,
        expense: ExpenseCreate,
        db: Session
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
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to log expense, {new_expense}"
        )
    db.refresh(new_expense)
    return new_expense

# -------------------------------------------------------------------
# --------- Replace Expense -> PUT -------------------------------
def replace_expense_service(
        user_id: int,
        expense_id: int,
        expense: ExpenseCreate,
        db: Session
) -> ExpenseOut:
    if expense.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Amount must be greater than 0, {expense.amount}"
        )

    replace_expense = (
        db.query(Expense).
        filter(Expense.user_id==user_id, Expense.id == expense_id, Expense.deleted_at == None).
        one_or_none()
    )

    if replace_expense is None:
        raise HTTPException(
            status_code=404,
            detail=f"Expense not found, {expense_id}"
        )

    replace_expense.category = expense.category
    replace_expense.amount = expense.amount
    replace_expense.description = expense.description
    replace_expense.date = expense.date

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to log expense, {replace_expense}"
        ) from e
    db.refresh(replace_expense)
    return replace_expense

# -------------------------------------------------------------------
# --------- Update Expense -> PATCH -------------------------------
def update_expense_service(
        user_id: int,
        expense_id: int,
        expense: ExpenseUpdate,
        db: Session
) -> ExpenseOut:
    if expense.amount <= 0 or not expense.category:
        raise HTTPException(
            status_code=400,
            detail=f"Either amount is 0 or less or category is not provided, {expense.amount}, {expense.category}"
        )

    update_expense = (
        db.query(Expense).
        filter(Expense.user_id==user_id, Expense.id == expense_id, Expense.deleted_at == None).
        one_or_none()
    )

    if update_expense is None:
        raise HTTPException(
            status_code=404,
            detail=f"Expense not found, {expense_id} is not present."
        )

    if expense.category:
        update_expense.category = expense.category
    if expense.amount:
        update_expense.amount = expense.amount
    if expense.description:
        update_expense.description = expense.description

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update the expense, {expense}"
        )
    db.refresh(update_expense)
    return update_expense

# -------------------------------------------------------------------
# --------- DELETE Expense -> DELETE -------------------------
def delete_expense_service(
        user_id: int,
        expense_id: int,
        db: Session
) -> ExpenseOut:
    expense = (
        db.query(Expense).
        filter(Expense.user_id == user_id, Expense.id == expense_id).
        one_or_none()
    )

    if expense is None:
        raise HTTPException(
            status_code=404,
            detail=f"Expense not found, {expense_id} is not present"
        )

    # already in deleted state
    if expense.deleted_at is not None:
        return expense

    # update deleted at
    expense.deleted_at = func.now()
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to delete expense, {expense}"
        ) from e

    db.refresh(expense)
    return expense

# -------------------------------------------------------------------
# --------- List Expense -> GET -----------------------------------
def list_expense_service(
        user_id: int,
        db: Session,
        category: Optional[str] = None,
        lt_amount: Optional[Decimal] = None, # less than amount
        gt_amount: Optional[Decimal] = None, # greater than amount
        duration: Optional[str] = None, # duration can be = week, month, quarter
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        sort_by: Optional[str] = None, # <-- this is sorting columns.. cols separated by comma
        sort_order: Optional[str] = None # <-- sort order, asc or desc
) -> List[ExpenseOut]:
    # Base query to filter non deleted expenses for a user
    exp_query = (
        db.query(Expense).
        filter(Expense.user_id == user_id, Expense.deleted_at == None)
    )
    print(f"Base Query:\n{exp_query}")

    # check category param
    exp_query = helpers.check_category_param(category=category, Expense=Expense, query=exp_query)

    # check ltamount & gtamount param
    exp_query = helpers.check_amount_param(lt_amount=lt_amount, gt_amount=gt_amount, Expense=Expense, query=exp_query)

    # check duration param
    exp_query = helpers.check_duration_param(duration=duration, Expense=Expense, query=exp_query)

    # check date param
    exp_query = helpers.check_date_param(from_date=from_date, to_date=to_date, Expense=Expense, query=exp_query)

    print(f"\nFilters Query:\n{[category, lt_amount, gt_amount, duration, from_date, to_date]} -> {exp_query}")

    # check sort param
    exp_query = helpers.check_sort_param(sort_by=sort_by, sort_order=sort_order, Expense=Expense, query=exp_query)

    print(f"\nSort Query\n{[sort_by, sort_order]} -> {exp_query}")
    result_set = exp_query.all()
    print(result_set)
    return result_set
