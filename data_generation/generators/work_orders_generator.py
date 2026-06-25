"""
work_orders_generator.py

Generate work order transactional data.
"""

import random
from datetime import datetime, timedelta

from tqdm import tqdm

from config import (
    ROW_COUNTS,
    BATCH_SIZE,
    KEY_PREFIXES,
    PRIORITIES,
    WO_STATUS_WEIGHTS,
    WO_OPEN,
    WO_IN_PROGRESS,
    WO_COMPLETED
)

from utils.batch_insert import batch_insert
from utils.business_rules import get_quantity_completed
from utils.date_utils import (
    generate_weighted_datetime,
    generate_end_time
)
from utils.logger import logger


# ============================================================
# SQL
# ============================================================

SQL = """
INSERT INTO work_orders (
    work_order_number,
    machine_id,
    item_id,
    product_name,
    quantity_planned,
    quantity_completed,
    priority,
    start_time,
    end_time,
    status
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


# ============================================================
# CACHED STATUS VALUES
# ============================================================

_WO_STATUS_VALUES = list(
    WO_STATUS_WEIGHTS.keys()
)

_WO_STATUS_PROBABILITIES = list(
    WO_STATUS_WEIGHTS.values()
)


# ============================================================
# DEMO GUARANTEE CONSTANTS
# ============================================================

_NOW = datetime.now()

# Q3: Open work orders older than 7 days
_Q3_CUTOFF = _NOW - timedelta(days=8)

# Q9: Completed vs Pending last week
_Q9_WEEK_START = _NOW - timedelta(days=7)
_Q9_GUARANTEE_COUNT = 200


# ============================================================
# FK FETCHERS
# ============================================================

def _fetch_machine_ids(connection):
    """
    Fetch machine IDs once.
    """

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT machine_id
        FROM machines
        """
    )

    machine_ids = [
        row[0]
        for row in cursor.fetchall()
    ]

    cursor.close()

    return machine_ids


def _fetch_inventory_items(connection):
    """
    Fetch item_id and item_name once.
    """

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            item_id,
            item_name
        FROM inventory
        """
    )

    inventory_items = cursor.fetchall()

    cursor.close()

    return inventory_items


# ============================================================
# GENERATOR
# ============================================================

def generate_work_orders(connection):
    """
    Generate work order records.
    """

    logger.info(
        f"work_orders_generator | Started | "
        f"Target: {ROW_COUNTS['work_orders']} rows"
    )

    machine_ids = _fetch_machine_ids(connection)

    inventory_items = _fetch_inventory_items(connection)

    logger.info(
        f"work_orders_generator | "
        f"Loaded {len(machine_ids)} machines and "
        f"{len(inventory_items)} inventory items"
    )

    batch = []

    for i in tqdm(
        range(ROW_COUNTS["work_orders"]),
        desc="Generating work orders",
        unit="rows"
    ):

        work_order_number = (
            f"{KEY_PREFIXES['work_order']}-{i + 1:06d}"
        )

        machine_id = random.choice(
            machine_ids
        )

        item_id, product_name = random.choice(
            inventory_items
        )

        quantity_planned = random.randint(
            50,
            1000
        )

        # ----------------------------------------------------
        # Q9 Guarantee
        # ----------------------------------------------------

        if i < _Q9_GUARANTEE_COUNT:

            start_time = (
                _Q9_WEEK_START
                + timedelta(
                    hours=random.randint(0, 167)
                )
            )

            if i % 4 == 0:

                status = WO_COMPLETED

            elif i % 4 == 1:

                status = WO_COMPLETED

            elif i % 4 == 2:

                status = WO_OPEN

            else:

                status = WO_IN_PROGRESS

        else:

            status = random.choices(
                population=_WO_STATUS_VALUES,
                weights=_WO_STATUS_PROBABILITIES,
                k=1
            )[0]

            start_time = generate_weighted_datetime()

        # ----------------------------------------------------
        # Q3 Guarantee
        # ----------------------------------------------------

        if (
            status == WO_OPEN
            and start_time > _Q3_CUTOFF
        ):

            start_time = (
                _Q3_CUTOFF
                - timedelta(
                    hours=random.randint(1, 72)
                )
            )

        quantity_completed = (
            get_quantity_completed(
                quantity_planned=quantity_planned,
                status=status
            )
        )

        # ----------------------------------------------------
        # Duration Logic
        # ----------------------------------------------------

        if quantity_planned <= 200:

            max_hours = 24

        elif quantity_planned <= 500:

            max_hours = 48

        else:

            max_hours = 72

        # ----------------------------------------------------
        # End Time
        # ----------------------------------------------------

        if status in (
            WO_OPEN,
            WO_IN_PROGRESS
        ):

            end_time = None

        else:

            end_time = generate_end_time(
                start_time=start_time,
                min_hours=1,
                max_hours=max_hours
            )

        row = (

            work_order_number,

            machine_id,

            item_id,

            product_name,

            quantity_planned,

            quantity_completed,

            random.choice(
                PRIORITIES
            ),

            start_time,

            end_time,

            status

        )

        batch.append(row)

        if len(batch) == BATCH_SIZE:

            batch_insert(
                connection=connection,
                sql=SQL,
                data=batch,
                table_name="work_orders"
            )

            batch.clear()

    # ========================================================
    # Flush Remaining Rows
    # ========================================================

    if batch:

        remaining_rows = len(batch)

        batch_insert(
            connection=connection,
            sql=SQL,
            data=batch,
            table_name="work_orders"
        )

        logger.info(
            f"work_orders_generator | "
            f"Flushed remaining rows: {remaining_rows}"
        )

    logger.info(
        f"work_orders_generator | Completed | "
        f"Rows inserted: {ROW_COUNTS['work_orders']}"
    )