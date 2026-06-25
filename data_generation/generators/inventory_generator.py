"""
inventory_generator.py

Generate inventory master data.
"""

import random

from tqdm import tqdm

from config import (
    ROW_COUNTS,
    BATCH_SIZE,
    KEY_PREFIXES,
    CATEGORIES,
    WAREHOUSES,
    INVENTORY_STATUS_WEIGHTS,
    INVENTORY_BELOW_REORDER_RATE
)

from utils.batch_insert import batch_insert
from utils.logger import logger


# ============================================================
# SQL
# ============================================================

SQL = """
INSERT INTO inventory (
    item_code,
    item_name,
    category,
    quantity_in_stock,
    warehouse_location,
    reorder_level,
    unit_of_measure,
    status
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""


# ============================================================
# CACHED VALUES
# ============================================================

_INVENTORY_STATUS_VALUES = list(
    INVENTORY_STATUS_WEIGHTS.keys()
)

_INVENTORY_STATUS_PROBABILITIES = list(
    INVENTORY_STATUS_WEIGHTS.values()
)


_CATEGORY_UNITS = {

    "Raw Material": [
        "Kg",
        "Litres",
        "Metres"
    ],

    "Component": [
        "Pieces",
        "Units"
    ],

    "Finished Good": [
        "Pieces",
        "Units"
    ]
}


_ITEM_NAMES = {

    "Raw Material": [
        "Steel Sheet",
        "Aluminum Rod",
        "Copper Wire",
        "Carbon Fiber",
        "Rubber Sheet",
        "PVC Pipe",
        "Hydraulic Oil",
        "Lubricant",
        "Coolant Fluid"
    ],

    "Component": [
        "Bearing Assembly",
        "Gear Set",
        "Hydraulic Pump",
        "Control Valve",
        "Sensor Module",
        "Drive Belt",
        "Circuit Board",
        "Motor Controller",
        "Pressure Gauge"
    ],

    "Finished Good": [
        "CNC Spindle Unit",
        "Conveyor Belt Module",
        "Welding Assembly",
        "Press Die Set",
        "Lathe Chuck",
        "Drill Head Assembly",
        "Grinding Wheel Kit",
        "Laser Module",
        "Robot Arm Unit"
    ]
}


# ============================================================
# GENERATOR
# ============================================================

def generate_inventory(connection):
    """
    Generate inventory master records.
    """

    logger.info(
        f"inventory_generator | Started | "
        f"Target: {ROW_COUNTS['inventory']} rows"
    )

    batch = []

    for i in tqdm(
        range(ROW_COUNTS["inventory"]),
        desc="Generating inventory",
        unit="rows"
    ):

        item_code = (
            f"{KEY_PREFIXES['inventory']}-{i + 1:05d}"
        )

        category = random.choice(CATEGORIES)

        reorder_level = random.randint(
            100,
            500
        )

        # Demo guarantee for Q2
        if random.random() < INVENTORY_BELOW_REORDER_RATE:

            quantity_in_stock = random.randint(
                0,
                reorder_level - 1
            )

        else:

            quantity_in_stock = random.randint(
                reorder_level,
                reorder_level * 3
            )

        row = (

            item_code,

            f"{random.choice(_ITEM_NAMES[category])} {item_code}",

            category,

            quantity_in_stock,

            random.choice(WAREHOUSES),

            reorder_level,

            random.choice(
                _CATEGORY_UNITS[category]
            ),

            random.choices(
                population=_INVENTORY_STATUS_VALUES,
                weights=_INVENTORY_STATUS_PROBABILITIES,
                k=1
            )[0]

        )

        batch.append(row)

        if len(batch) == BATCH_SIZE:

            batch_insert(
                connection=connection,
                sql=SQL,
                data=batch,
                table_name="inventory"
            )

            batch.clear()

    # Flush remaining rows

    if batch:

        remaining_rows = len(batch)

        batch_insert(
            connection=connection,
            sql=SQL,
            data=batch,
            table_name="inventory"
        )

        logger.info(
            f"inventory_generator | "
            f"Flushed remaining rows: {remaining_rows}"
        )

    logger.info(
        f"inventory_generator | Completed | "
        f"Rows inserted: {ROW_COUNTS['inventory']}"
    )