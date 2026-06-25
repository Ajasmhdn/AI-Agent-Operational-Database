"""
purchase_orders_generator.py

Generate purchase order transactional data.
"""

import random
from datetime import timedelta

from tqdm import tqdm

from config import (
    ROW_COUNTS,
    BATCH_SIZE,
    KEY_PREFIXES,
    PO_STATUS_WEIGHTS,
    WORST_SUPPLIER_CODE,
    PO_QUANTITY_RANGE
)

from utils.batch_insert import batch_insert
from utils.business_rules import (
    get_actual_delivery_date
)
from utils.date_utils import (
    generate_random_date
)
from utils.logger import logger


# ============================================================
# SQL
# ============================================================

SQL = """
INSERT INTO purchase_orders (
    po_number,
    supplier_id,
    item_id,
    quantity,
    order_date,
    expected_delivery_date,
    actual_delivery_date,
    status
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""


# ============================================================
# CACHED STATUS VALUES
# ============================================================

_PO_STATUS_VALUES = list(
    PO_STATUS_WEIGHTS.keys()
)

_PO_STATUS_PROBABILITIES = list(
    PO_STATUS_WEIGHTS.values()
)


# ============================================================
# FK FETCHERS
# ============================================================

def _fetch_suppliers(connection):
    """
    Fetch supplier information once.
    """

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            supplier_id,
            supplier_code,
            lead_time_days
        FROM suppliers
        """
    )

    suppliers = cursor.fetchall()

    cursor.close()

    return suppliers


def _fetch_item_ids(connection):
    """
    Fetch inventory item IDs once.
    """

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT item_id
        FROM inventory
        """
    )

    item_ids = [
        row[0]
        for row in cursor.fetchall()
    ]

    cursor.close()

    return item_ids


# ============================================================
# GENERATOR
# ============================================================

def generate_purchase_orders(connection):
    """
    Generate purchase order records.
    """

    logger.info(
        f"purchase_orders_generator | Started | "
        f"Target: {ROW_COUNTS['purchase_orders']} rows"
    )

    suppliers = _fetch_suppliers(connection)

    item_ids = _fetch_item_ids(connection)



    batch = []

    inserted_rows = 0

    for i in tqdm(
        range(ROW_COUNTS["purchase_orders"]),
        desc="Generating purchase orders",
        unit="rows"
    ):

        po_number = (
            f"{KEY_PREFIXES['purchase_order']}-{i + 1:06d}"
        )

        supplier_id, supplier_code, lead_time_days = (
            random.choice(suppliers)
        )

        item_id = random.choice(
            item_ids
        )

        status = random.choices(
            population=_PO_STATUS_VALUES,
            weights=_PO_STATUS_PROBABILITIES,
            k=1
        )[0]

        quantity = random.randint(
            *PO_QUANTITY_RANGE
        )

        order_date = generate_random_date()

        expected_delivery_date = (
            order_date +
            timedelta(
                days=lead_time_days
            )
        )

        is_worst_supplier = (
            supplier_code ==
            WORST_SUPPLIER_CODE
        )

        actual_delivery_date = (
            get_actual_delivery_date(
                expected_delivery_date=expected_delivery_date,
                status=status,
                is_worst_supplier=is_worst_supplier
            )
        )

        row = (

            po_number,

            supplier_id,

            item_id,

            quantity,

            order_date,

            expected_delivery_date,

            actual_delivery_date,

            status

        )

        batch.append(row)

        if len(batch) == BATCH_SIZE:

            rows_to_insert = len(batch)

            batch_insert(
                connection=connection,
                sql=SQL,
                data=batch,
                table_name="purchase_orders"
            )

            inserted_rows += rows_to_insert

            batch.clear()

    # ========================================================
    # FLUSH REMAINING ROWS
    # ========================================================

    if batch:

        remaining_rows = len(batch)

        batch_insert(
            connection=connection,
            sql=SQL,
            data=batch,
            table_name="purchase_orders"
        )

        inserted_rows += remaining_rows

        logger.info(
            f"purchase_orders_generator | "
            f"Flushed remaining rows: "
            f"{remaining_rows}"
        )

    logger.info(
        f"purchase_orders_generator | Completed | "
        f"Rows inserted: "
        f"{inserted_rows}"
    )
