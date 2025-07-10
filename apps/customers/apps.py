from django.apps import AppConfig


class CustomersConfig(AppConfig):
    """Initialize the customers application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.customers"
