from django.conf import settings
from loguru import logger

from odyn import BasicAuthSession, Odyn

logger.remove()
logger.add(settings.LOGS_DIR / "odyn.log", level="DEBUG")


def get_client() -> Odyn:
    """Get an authenticated instance of Odyn client."""
    session = BasicAuthSession(username=settings.ERP_USERNAME, password=settings.ERP_PASSWORD)
    return Odyn(base_url=settings.ERP_BASE_URL, session=session, logger=logger)
