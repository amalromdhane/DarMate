from fastapi import APIRouter

from app.presentation.api.v1.routers import (
    admin, auth, groups, health, messaging, notifications, properties, reference, rentals, reviews, roommates, users, visits,
)

api_router = APIRouter()
for module in (health, auth, users, reference, properties, roommates, groups, rentals, visits, messaging, notifications, reviews, admin):
    api_router.include_router(module.router)
