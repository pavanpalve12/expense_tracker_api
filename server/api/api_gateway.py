from fastapi import FastAPI

from server.api.routers.expenses_router import expense_router
from server.utils.fastapi_app_lifespan import lifespan

api_router_app = FastAPI(lifespan=lifespan)

api_router_app.include_router(expense_router)

