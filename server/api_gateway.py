from unicodedata import category

from fastapi import FastAPI

api_gateway = FastAPI()

#
# {"user_id": 1, "category": "groceries", "amount": 250.00,
#   "description": "Milk, bread, eggs", "date": "2025-01-03"
# }
sample_expenses = [
    {"expense_id": 1, "user_id": 1, "category": "groceries", "amount": 250.00, "description": "Milk, bread, eggs",
     "date": "2025-01-03"},
    {"expense_id": 2, "user_id": 1, "category": "food", "amount": 1200.00, "description": "Lunch at local restaurant",
     "date": "2025-01-04"},
    {"expense_id": 3, "user_id": 2, "category": "groceries", "amount": 450.00, "description": "Vegetables & fruits",
     "date": "2025-01-05"},
    {"expense_id": 4, "user_id": 2, "category": "food", "amount": 899.00, "description": "Swiggy dinner order",
     "date": "2025-01-06"},
    {"expense_id": 5, "user_id": 1, "category": "transport", "amount": 150.00, "description": "Auto to work",
     "date": "2025-01-03"},
    {"expense_id": 6, "user_id": 1, "category": "fuel", "amount": 2400.00, "description": "Bike petrol refill",
     "date": "2025-01-08"},
    {"expense_id": 7, "user_id": 3, "category": "transport", "amount": 60.00, "description": "Bus ticket",
     "date": "2025-01-02"},
    {"expense_id": 8, "user_id": 2, "category": "electricity", "amount": 1350.00,
     "description": "Monthly electricity bill", "date": "2025-01-01"},
    {"expense_id": 9, "user_id": 1, "category": "mobile", "amount": 599.00, "description": "Prepaid recharge",
     "date": "2025-01-07"},
    {"expense_id": 10, "user_id": 3, "category": "internet", "amount": 950.00, "description": "JioFiber monthly bill",
     "date": "2025-01-05"},
    {"expense_id": 11, "user_id": 2, "category": "entertainment", "amount": 399.00,
     "description": "Netflix monthly subscription", "date": "2025-01-01"},
    {"expense_id": 12, "user_id": 3, "category": "movies", "amount": 1200.00, "description": "Movie night with friends",
     "date": "2025-01-10"},
    {"expense_id": 13, "user_id": 1, "category": "entertainment", "amount": 350.00, "description": "Arcade games",
     "date": "2025-01-06"},
    {"expense_id": 14, "user_id": 3, "category": "shopping", "amount": 2200.00,
     "description": "Clothes - T-shirt & jeans", "date": "2025-01-08"},
    {"expense_id": 15, "user_id": 3, "category": "shopping", "amount": 799.00, "description": "New headphones",
     "date": "2025-01-09"},
    {"expense_id": 16, "user_id": 1, "category": "household", "amount": 300.00, "description": "Cleaning supplies",
     "date": "2025-01-04"},
    {"expense_id": 17, "user_id": 2, "category": "health", "amount": 150.00, "description": "Paracetamol + ORS",
     "date": "2025-01-03"},
    {"expense_id": 18, "user_id": 1, "category": "health", "amount": 2000.00, "description": "Doctor consultation",
     "date": "2025-01-09"},
    {"expense_id": 19, "user_id": 3, "category": "misc", "amount": 50.00, "description": "Tea with colleague",
     "date": "2025-01-02"},
    {"expense_id": 20, "user_id": 2, "category": "gift", "amount": 500.00, "description": "Birthday gift for friend",
     "date": "2025-01-07"},
    {"expense_id": 21, "user_id": 1, "category": "food", "amount": 180.00, "description": "Evening snacks",
     "date": "2025-01-12"},
    {"expense_id": 22, "user_id": 1, "category": "food", "amount": 220.00, "description": "Breakfast at canteen",
     "date": "2025-01-14"},
    {"expense_id": 23, "user_id": 1, "category": "food", "amount": 450.00, "description": "Lunch thali",
     "date": "2025-01-16"},
    {"expense_id": 24, "user_id": 1, "category": "food", "amount": 600.00, "description": "Dinner at local dhaba",
     "date": "2025-01-19"}
]
# get method to retrieve all expenses
@api_gateway.get(path="/expenses/")
async def get_all_expenses():
    return sample_expenses
# get method to retrieve all expenses for a user - path param

# get method to retrieve food expenses for a user - query param
@api_gateway.get("/users/{user_id}/expenses")
def get_expenses(
        user_id: int,
        category: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None
):
    expenses = []

    for idx, exp in enumerate(sample_expenses):
        category_match = False
        date_match = False

        if exp["user_id"] != user_id:
            continue
        if category:
            category_match = exp["category"] == category
        if from_date and to_date:
            date_match = from_date <= exp["date"] <= to_date
        elif from_date:
            date_match = exp["date"] >= from_date
        elif to_date:
            date_match = exp["date"] <= to_date

        if category_match or date_match:
            expenses.append(exp)
    return expenses

@api_gateway.post("/users/{user_id}/expenses")
async def post_expenses(
        user_id: int,
        category: str,
        amount: float,
        description: str,
        date: str
):
    return sample_expenses.append({
        "user_id": user_id,
        "category": category,
        "amount": amount,
        "description": description,
        "date": date
    })[-1]

@api_gateway.delete("/users/{user_id}/expenses")
async def delete_expense(user_id: int, date: str):
    return [
        sample_expenses.pop(idx) for idx, exp in enumerate(sample_expenses)
        if exp["user_id"] == user_id and exp["date"] == date
    ]

@api_gateway.patch("/users/{user_id}/expenses")
async def update_expenses(user_id: int, expense_id: int, amount: float, description: str):
    return list((
        ({**exp, "amount": amount, "description": description}
        if exp["user_id"] == user_id and exp["expense_id"] == expense_id else exp
        for exp in sample_expenses),
        None
    ))