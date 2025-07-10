from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Customer


class CustomerAdmin(SimpleHistoryAdmin):
    """Custom admin built for SimpleHistoryAdmin."""

    list_display = ["code", "name"]
    search_fields = ["code", "name"]


admin.site.register(Customer, CustomerAdmin)
