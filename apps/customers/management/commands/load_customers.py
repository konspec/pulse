from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command to load customers from the ERP."""

    def handle(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Handle the command call."""
