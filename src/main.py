from fastapi import FastAPI

from src.routers import accounts


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
