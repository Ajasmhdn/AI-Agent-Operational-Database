"""
machines_generator.py

Generate machine master data.
"""

import random

from tqdm import tqdm

from config import (
    ROW_COUNTS,
    BATCH_SIZE,
    KEY_PREFIXES,
    MACHINE_TYPES,
    MACHINE_STATUSES,
    MACHINE_STATUS_WEIGHTS,
    PRODUCTION_LINES,
    LOCATIONS
)

from utils.batch_insert import batch_insert
from utils.date_utils import generate_random_date
from utils.logger import logger


# ============================================================
# SQL
# ============================================================

SQL = """
INSERT INTO machines (
    machine_code,
    machine_name,
    machine_type,
    production_line,
    location,
    installation_date,
    status
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""


# ============================================================
# CACHED VALUES
# ============================================================

_MACHINE_STATUS_VALUES = list(
    MACHINE_STATUS_WEIGHTS.keys()
)

_MACHINE_STATUS_PROBABILITIES = list(
    MACHINE_STATUS_WEIGHTS.values()
)


# ============================================================
# GENERATOR
# ============================================================

def generate_machines(connection):
    """
    Generate machine master records.
    """

    logger.info(
        f"machines_generator | Started | "
        f"Target: {ROW_COUNTS['machines']} rows"
    )

    batch = []

    for i in tqdm(
        range(ROW_COUNTS["machines"]),
        desc="Generating machines",
        unit="rows"
    ):

        machine_code = (
            f"{KEY_PREFIXES['machine']}-{i + 1:05d}"
        )

        machine_type = random.choice(
            MACHINE_TYPES
        )

        status = random.choices(
            population=_MACHINE_STATUS_VALUES,
            weights=_MACHINE_STATUS_PROBABILITIES,
            k=1
        )[0]

        row = (

            machine_code,

            f"{machine_type} Machine {i + 1}",

            machine_type,

            random.choice(PRODUCTION_LINES),

            random.choice(LOCATIONS),

            generate_random_date(),

            status

        )

        batch.append(row)

        if len(batch) == BATCH_SIZE:

            batch_insert(
                connection=connection,
                sql=SQL,
                data=batch,
                table_name="machines"
            )

            batch.clear()

    # Flush remaining rows

    if batch:

        remaining_rows = len(batch)

        batch_insert(
            connection=connection,
            sql=SQL,
            data=batch,
            table_name="machines"
        )

        logger.info(
            f"machines_generator | "
            f"Flushed remaining rows: {remaining_rows}"
        )

    logger.info(
        f"machines_generator | Completed | "
        f"Rows inserted: {ROW_COUNTS['machines']}"
    )