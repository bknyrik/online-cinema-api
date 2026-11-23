from fastapi import FastAPI

from src.routers import (
    accounts,
    cinema,
    rating,
    notifications,
    shopping
)


app = FastAPI(
    title="Online Cinema API",
    version="1.0.0",
    description="Manage your purchased movies, user credentials and more.",
)

api_prefix = "/api"

app.include_router(
    accounts.router,
    prefix=f"{api_prefix}/accounts",
    tags=["accounts",]
)
app.include_router(
    cinema.router,
    prefix=f"{api_prefix}/cinema",
    tags=["cinema"]
)
app.include_router(
    rating.router,
    prefix=f"{api_prefix}/rating",
    tags=["rating"]
)
app.include_router(
    notifications.router,
    prefix=f"{api_prefix}/notifications",
    tags=["notifications"]
)
app.include_router(
    shopping.router,
    prefix=f"{api_prefix}/shopping",
    tags=["shopping"]
)
