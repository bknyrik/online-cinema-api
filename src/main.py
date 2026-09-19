from fastapi import FastAPI

from src.routers import accounts, profiles, movies, genres, certifications


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
    profiles.router,
    prefix=f"{api_prefix}/profiles",
    tags=["profiles",]
)
app.include_router(
    movies.router,
    prefix=f"{api_prefix}/movies",
    tags=["movies"]
)
app.include_router(
    genres.router,
    prefix=f"{api_prefix}/genres",
    tags=["genres"]
)
app.include_router(
    certifications.router,
    prefix=f"{api_prefix}/certifications",
    tags=["certifications"]
)
