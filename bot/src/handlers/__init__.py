__all__ = ("router",)

from aiogram import Router

router = Router()
from .user import router as user_router
from .admin import router as admin_router

router.include_routers(user_router, admin_router)
