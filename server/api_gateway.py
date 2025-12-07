from fastapi import FastAPI

api_router_app = FastAPI()

# ---------------------- methods and commands --------------------------

# POST - register new user
# POST - login new user
# POST - users/expenses -- create new expense
# PATCH -users/expenses -- update the expense
# DELETE - users/expenses -- delete the expense
# GET -- users/expenses -- list the expense

@api_router_app.post(path="/users/register")
def register_user():
    pass

@api_router_app.post(path="/users/login")
def login_user():
    pass

# this get is for a particular user and query params will define the what to get
@api_router_app.get(path="/users/{user_id}/expenses")
def list_expenses():
    pass

@api_router_app.post(path="/users/{user_id}/expenses")
def log_expenses():
    pass

@api_router_app.patch(path="users/{user_id}/expenses")
def update_expenses():
    pass

@api_router_app.delete(path="users/{user_id}/expenses")
def delete_expenses():
    pass