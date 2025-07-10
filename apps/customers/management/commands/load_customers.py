import logging
from typing import Any

import polars as pl
from django.core.management.base import BaseCommand

from apps.common.erp import get_client
from apps.customers.models import Customer

# Get logger for this module
logger = logging.getLogger(__name__)


def get_customers() -> dict[str, str]:
    """Get query parameters for the API request."""
    logger.info("Starting to fetch customers from ERP")

    try:
        client = get_client()
        # Endpoint to get customers data
        endpoint = "ksppl_customers"
        # Get parameters
        params = {"$select": "No,Name"}

        logger.debug(f"Making API request to endpoint: {endpoint} with params: {params}")

        # Get data
        data = client.get(endpoint, params)

        logger.info(f"Successfully fetched {len(data)} customers from ERP")

        # Add prefix to customer code
        processed_data = [{"code": "C" + customer["No"], "name": customer["Name"]} for customer in data]

        logger.debug(f"Processed {len(processed_data)} customer records with code prefix")

    except Exception:
        logger.exception("Failed to fetch customers from ERP.")
        raise
    else:
        return processed_data


def process_customers_data(data: list[dict[str, Any]]) -> pl.DataFrame:
    """Process the raw response from the ERP API."""
    logger.info(f"Processing {len(data)} customer records")

    try:
        dataframe = pl.DataFrame(data)

        # Rename and type cast
        processed_df = dataframe.select(pl.col("code").cast(pl.Utf8), pl.col("name").cast(pl.Utf8))

        logger.info(f"Successfully processed {len(processed_df)} customer records into DataFrame")
        logger.debug(f"DataFrame shape: {processed_df.shape}")

    except Exception:
        logger.exception("Failed to process customer data.")
        raise

    else:
        return processed_df


def write_to_database(dataframe: pl.DataFrame) -> None:
    """Upsert customer data."""
    logger.info(f"Writing {len(dataframe)} customers to database")

    try:
        customers = [Customer(code=row["code"], name=row["name"]) for row in dataframe.to_dicts()]

        logger.debug(f"Created {len(customers)} Customer objects")

        result = Customer.objects.bulk_create(
            customers, update_conflicts=True, unique_fields=["code"], update_fields=["name"]
        )

        logger.info(f"Successfully upserted {len(result)} customers to database")

    except Exception:
        logger.exception("Failed to write customers to database.")
        raise


class Command(BaseCommand):
    """Command to load customers from the ERP."""

    def handle(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, ARG002
        """Handle the command call."""
        logger.info("Starting customer synchronization command")

        try:
            # Get customer data
            data = get_customers()

            # Process data and get dataframe
            dataframe = process_customers_data(data)

            # Write to DataBase
            write_to_database(dataframe)

            success_message = f"{len(dataframe)} customers updated successfully."
            logger.info(f"Customer synchronization completed: {success_message}")
            self.stdout.write(self.style.SUCCESS(success_message))

        except Exception:
            error_message = "Customer synchronization failed."
            logger.exception(error_message)
            self.stdout.write(self.style.ERROR(error_message))
            raise
