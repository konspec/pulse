from django.conf import settings

from odyn import BasicAuthSession, Odyn


def get_client() -> Odyn:
    """Get an authenticated instance of Odyn client."""
    session = BasicAuthSession(username=settings.ERP_USERNAME, password=settings.ERP_PASSWORD)
    return Odyn(base_url=settings.ERP_BASE_URL, session=session)
