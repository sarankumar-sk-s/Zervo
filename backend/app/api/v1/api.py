from fastapi import APIRouter
from app.api.v1 import auth, users, food, volunteer, notifications, ai

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(food.router, prefix="/food", tags=["food"])
api_router.include_router(volunteer.router, prefix="/volunteer", tags=["volunteer"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])

