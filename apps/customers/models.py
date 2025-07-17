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

    def __str__(self) -> str:
        """Return a string representation of the customer object."""
        return f"({self.code}) {self.name}"


class CustomerLedgerEntry(models.Model):
    """Customer ledger entry model. Synced with ERP."""

    # FOREIGN KEY
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, null=False, blank=False, related_name="ledger_entries"
    )

    # UNIQUE FIELD
    entry_no = models.CharField(max_length=20, null=False, blank=False, unique=True)

    # DOCUMENT DATA
    posting_date = models.DateField(blank=False, null=False)
    document_no = models.CharField(max_length=30, null=False, blank=False)
    document_type = models.CharField(max_length=30, null=False, blank=True)

    # BLOCK CUSTOMER LEDGER ENTRIES
    block_reason = models.CharField(max_length=255, null=False, blank=True, default="")

    # AMOUNT RELATED DATA
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=20, decimal_places=2)

    history = HistoricalRecords()

    def __str__(self) -> str:
        """String representation of the customer ledger entry."""
        return f"({self.document_no}) - {self.amount}"

    class Meta:
        """Meta class for CustomerLedgerEntry model."""

        verbose_name = "Customer Ledger Entry"
        verbose_name_plural = "Customer Ledger Entries"
        ordering = ["-entry_no"]
