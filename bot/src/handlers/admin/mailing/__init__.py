__all__ = ("router", )
from aiogram import Router
from .callback import router as admin_send_all_callback_router
from .message import router as admin_send_all_message_router
router = Router()
router.include_routers(admin_send_all_message_router, admin_send_all_callback_router)