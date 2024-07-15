__all__ = ("router", )
from aiogram import Router
from .callback import router as admin_refs_callback_router
router = Router()
router.include_routers(admin_refs_callback_router)