from django.db import models
from simple_history.models import HistoricalRecords


class Customer(models.Model):
    """Customer model. Synced with ERP."""

    code = models.CharField(max_length=20, unique=True, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)

    history = HistoricalRecords()

    class Meta:
        """Meta class for customer object."""

        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ["code"]

    def __str__(self) -> None:
        """Return a string representation of the customer object."""
        return f"({self.code}) {self.name}"
