__all__ = ("router", )
from aiogram import Router

from .message import router as message_router
from .callback import router as callback_router
from .channels import router as channels_router
from .stats import router as stats_router
from .upload import router as upload_router
from .mailing import router as mailing_router
from .referals import router as ref_router
from .adv import router as adv_router
router = Router()

router.include_routers(message_router, callback_router, channels_router, stats_router, upload_router,
                       mailing_router, ref_router, adv_router)