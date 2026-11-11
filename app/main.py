from fastapi import FastAPI

from app.routers.user_routes import router as user_router
from app.routers.address_routes import router as address_router

app = FastAPI(
    title="ShopEase User Management Service",
    description="Customer profile and address management",
    version="1.0.0",
)

app.include_router(user_router)
app.include_router(address_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "user-management",
    }