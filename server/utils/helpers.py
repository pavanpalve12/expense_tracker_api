from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Any
from decimal import Decimal

from server.models.sql_models import Expense
from fastapi import HTTPException

def check_category_param(
        category: str,
        Expense: Expense,
        query: Any
) -> Any:
    if category:
        return query.filter(Expense.category == category)
    return query

def check_duration_param(
        duration: str,
        Expense: Expense,
        query: Any
) -> Any:
    allowed_duration = ["day", "week", "month", "quarter", "year"]
    # duration filter: if duration is specifies in query param
    if duration:
        if duration.lower() in allowed_duration:
            time_delta = None
            if duration.lower() == "day":
                time_delta = datetime.today() - timedelta(days=1)
            if duration.lower() == "week":
                time_delta = datetime.today() - timedelta(weeks=1)
            if duration.lower() == "month":
                time_delta = datetime.today() - relativedelta(months = 1)
            if duration.lower() == "quarter":
                time_delta = datetime.today() - relativedelta(months = 3)
            if duration.lower() == "year":
                time_delta = datetime.today() - relativedelta(years = 1)

            return query.filter(Expense.date > time_delta)
        else:
            raise HTTPException(status_code=400, detail=f"Duration value: {duration} is invalid, must be from {allowed_duration}")
    else:
        return query

def check_amount_param(
        lt_amount: Decimal,
        gt_amount: Decimal,
        Expense: Expense,
        query: Any
) -> Any:
    # amount filter: if lt_amount / gt_amount in query param
    if lt_amount:
        query = query.filter(Expense.amount < lt_amount)
    if gt_amount:
        query = query.filter(Expense.amount > gt_amount)

    return query

def check_date_param(
        from_date: date,
        to_date: date,
        Expense: Expense,
        query: Any
) -> Any:

    # date filter: if from_date / to_date in query param
    if from_date:
        return query.filter(Expense.date >= from_date)
    if to_date:
        return query.filter(Expense.date <= to_date)

    return query

def check_sort_param(
        sort_by: str,
        sort_order: str,
        Expense: Expense,
        query: Any
) -> Any:
    # ------------------------ Sorting Logic -------------------------------
    # if user specifies sort oder for each col like amount:desc&date:asc
    # if user specifies sort order with sort_order field like amount,date&asc
    allowed_sort_cols = {
        "id": Expense.id,
        "date": Expense.date,
        "amount": Expense.amount,
        "category": Expense.category,
        "created_at": Expense.created_at,
    }

    allowed_sort_order_values = ["asc", "desc"]

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
                raise HTTPException(status_code=400, detail=f"{column} is invalid sort column, must be from {str(allowed_sort_cols)}")

            if not order in allowed_sort_order_values:
                raise HTTPException(status_code=400, detail=f"{order} is invalid sort value, must be from {allowed_sort_order_values}")

            if order == "asc":
                order_by_clauses.append(column.asc())
            else:
                order_by_clauses.append(column.desc())

        return query.order_by(*order_by_clauses)
    else:
        return query.order_by(Expense.date.desc(), Expense.amount.desc())