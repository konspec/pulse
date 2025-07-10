from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Customer


class CustomerAdmin(SimpleHistoryAdmin):
    """Custom admin built for SimpleHistoryAdmin."""

    list_display = ["code", "name"]
    search_fields = ["code", "name"]

    def has_change_permission(self, request, obj=None):  # noqa: ARG002
        """Check if user has edit permission for the model."""
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ARG002
        """Check if user has delete permission for the model."""
        return False

    def has_add_permission(self, request, obj=None):  # noqa: ARG002
        """Check if user has create permission for the model."""
        return False


admin.site.register(Customer, CustomerAdmin)
