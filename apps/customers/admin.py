from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Customer, CustomerLedgerEntry


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


class CustomerLedgerEntryAdmin(SimpleHistoryAdmin):
    """Custom admin built for Customer Ledger Entries."""

    list_display = ["customer", "posting_date", "document_no", "amount", "remaining_amount"]

    search_fields = ["document_no"]

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
admin.site.register(CustomerLedgerEntry, CustomerLedgerEntryAdmin)
