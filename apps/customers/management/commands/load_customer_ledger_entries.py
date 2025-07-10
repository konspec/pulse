import logging
from typing import Any

import polars as pl
from django.core.management.base import BaseCommand

from apps.common.erp import get_client
from apps.customers.models import Customer, CustomerLedgerEntry

# Set up logger
logger = logging.getLogger(__name__)


def get_customer_code_mapping():
    """Get all customer objects."""
    logger.info("Starting to fetch customer code mappings")
    try:
        customers = Customer.objects.all()
        mappings = {}
        for customer in customers:
            mappings[customer.code] = customer.id
        logger.info(f"Successfully created {len(mappings)} customer code mappings")

    except Exception:
        logger.exception("Error creating customer code mappings.")
        raise
    else:
        return mappings


def get_customer_ledger_entries_data():
    """Get customer ledger entries from the database."""
    logger.info("Starting to fetch customer ledger entries from ERP")
    try:
        # Get Odyn client instance
        client = get_client()
        logger.debug("Successfully obtained ERP client")

        # Endpoint for customer ledger entries
        endpoint = "ksppl_customer_ledger_entries"

        # Parameters for the API call
        params = {
            "$select": (
                "Entry_No,Posting_Date,Document_Type,Document_No,Customer_No,Block_Reason,Amount_LCY,Remaining_Amt_LCY"
            )
        }

        logger.debug(f"Making API call to endpoint: {endpoint}")
        # Get data from ERP
        data = client.get(endpoint, params)
        logger.info(f"Successfully fetched {len(data)} customer ledger entries from ERP")

        # Get mappings
        mappings = get_customer_code_mapping()

        # Sanitize customer code
        mapped_entries = 0
        unmapped_entries = 0

        for entry in data:
            customer_code = "C" + entry["Customer_No"]
            if customer_code in mappings:
                entry["Customer_No"] = mappings[customer_code]
                mapped_entries += 1
            else:
                entry["Customer_No"] = None
                unmapped_entries += 1
                logger.warning(
                    f"Customer code '{customer_code}' not found in "
                    f"mappings for entry {entry.get('Entry_No', 'unknown')}"
                )

        logger.info(f"Customer mapping complete: {mapped_entries} mapped, {unmapped_entries} unmapped")

    except Exception:
        logger.exception("Error fetching customer ledger entries.")
        raise
    else:
        return data


def process_customer_ledger_entries_data(data: list[dict[str, Any]]) -> pl.DataFrame:
    """Process customer ledger entries data."""
    logger.info(f"Starting to process {len(data)} customer ledger entries")
    try:
        # Create dataframe
        dataframe = pl.DataFrame(data)
        logger.debug("Successfully created Polars DataFrame")

        # Rename columns and cast types
        processed_df = dataframe.select(
            pl.col("Entry_No").cast(pl.Int32).alias("entry_no"),
            pl.col("Posting_Date").cast(pl.Date).alias("posting_date"),
            pl.col("Document_Type").cast(pl.Utf8).alias("document_type"),
            pl.col("Document_No").cast(pl.Utf8).alias("document_no"),
            pl.col("Customer_No").cast(pl.Int32).alias("customer_no"),
            pl.col("Block_Reason").cast(pl.Utf8).alias("block_reason"),
            pl.col("Amount_LCY").cast(pl.Decimal).alias("amount"),
            pl.col("Remaining_Amt_LCY").cast(pl.Decimal).alias("remaining_amount"),
        )

        # Filter out entries with null customer_no
        initial_count = processed_df.height
        processed_df = processed_df.filter(pl.col("customer_no").is_not_null())
        final_count = processed_df.height

        if initial_count != final_count:
            logger.warning(f"Filtered out {initial_count - final_count} entries with null customer_no")

        logger.info(f"Successfully processed {final_count} customer ledger entries")

    except Exception:
        logger.exception("Error processing customer ledger entries data.")
        raise

    else:
        return processed_df


def write_to_database(dataframe: pl.DataFrame) -> None:
    """Bulk write customer ledger entries to database."""
    logger.info(f"Starting to write {dataframe.height} entries to database")
    try:
        entries = [
            CustomerLedgerEntry(
                customer_id=entry["customer_no"],
                entry_no=entry["entry_no"],
                posting_date=entry["posting_date"],
                document_no=entry["document_no"],
                document_type=entry["document_type"],
                block_reason=entry["block_reason"],
                amount=entry["amount"],
                remaining_amount=entry["remaining_amount"],
            )
            for entry in dataframe.to_dicts()
        ]

        logger.debug(f"Created {len(entries)} CustomerLedgerEntry objects")

        result = CustomerLedgerEntry.objects.bulk_create(
            entries,
            update_conflicts=True,
            unique_fields=["entry_no"],
            update_fields=["remaining_amount", "block_reason"],
        )

        logger.info(f"Successfully wrote {len(result)} entries to database")

    except Exception:
        logger.exception("Error writing to database.")
        raise


class Command(BaseCommand):
    """Load customer ledger entries from the ERP."""

    help = "Load customer ledger entries from the ERP system"

    def add_arguments(self, parser):
        """Add arguments to django command."""
        parser.add_argument(
            "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Set the logging level"
        )

        parser.add_argument("--skip-csv", action="store_true", help="Skip writing CSV file")

    def handle(self, *args, **kwargs):  # noqa: ARG002
        """Handle the command call."""
        # Set up logging level
        log_level = getattr(logging, kwargs.get("log_level", "INFO"))
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(), logging.FileHandler("customer_ledger_sync.log")],
        )

        logger.info("=" * 50)
        logger.info("Starting customer ledger entries synchronization")
        logger.info("=" * 50)

        try:
            # Get data from ERP
            data = get_customer_ledger_entries_data()

            # Process the data
            dataframe = process_customer_ledger_entries_data(data)

            # Write to database
            write_to_database(dataframe)

            logger.info("=" * 50)
            logger.info("Customer ledger entries synchronization completed successfully")
            logger.info("=" * 50)

        except Exception:
            logger.exception("=" * 50)
            logger.exception("Customer ledger entries synchronization failed.")
            logger.exception("=" * 50)
            raise
