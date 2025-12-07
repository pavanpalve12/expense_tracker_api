from fastapi import FastAPI

from server.api.routers.expense_router import expense_router
from server.api.routers.user_router import user_router
from server.utils.fastapi_app_lifespan import lifespan

api_router_app = FastAPI(lifespan=lifespan)

# -------------------------------------------------------
# ------------ User Router ------------------------------
api_router_app.include_router(user_router)

# -------------------------------------------------------
# ------------ Expense Router ---------------------------
api_router_app.include_router(expense_router)

