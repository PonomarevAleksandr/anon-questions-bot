__all__ = ("router", )
from aiogram import Router
from .callback import router as callback_router
router = Router()

router.include_routers(callback_router)