"""
employees_generator.py

Generate employee master data.
"""

import random

from tqdm import tqdm

from config import (
    fake,
    ROW_COUNTS,
    BATCH_SIZE,
    KEY_PREFIXES,
    ROLE_WEIGHTS,
    ROLE_DEPARTMENTS,
    EMPLOYEE_STATUS_WEIGHTS
)

from utils.batch_insert import batch_insert
from utils.logger import logger


# ============================================================
# SQL
# ============================================================

SQL = """
INSERT INTO employees (
    employee_code,
    employee_name,
    role,
    department,
    hire_date,
    status
)
VALUES (%s, %s, %s, %s, %s, %s)
"""


# ============================================================
# CACHED VALUES
# ============================================================

_ROLE_VALUES = list(
    ROLE_WEIGHTS.keys()
)

_ROLE_PROBABILITIES = list(
    ROLE_WEIGHTS.values()
)

_EMPLOYEE_STATUS_VALUES = list(
    EMPLOYEE_STATUS_WEIGHTS.keys()
)

_EMPLOYEE_STATUS_PROBABILITIES = list(
    EMPLOYEE_STATUS_WEIGHTS.values()
)


# ============================================================
# GENERATOR
# ============================================================

def generate_employees(connection):
    """
    Generate employee master records.
    """

    logger.info(
        f"employees_generator | Started | "
        f"Target: {ROW_COUNTS['employees']} rows"
    )

    batch = []

    for i in tqdm(
        range(ROW_COUNTS["employees"]),
        desc="Generating employees",
        unit="rows"
    ):

        employee_code = (
            f"{KEY_PREFIXES['employee']}-{i + 1:05d}"
        )

        role = random.choices(
            population=_ROLE_VALUES,
            weights=_ROLE_PROBABILITIES,
            k=1
        )[0]

        status = random.choices(
            population=_EMPLOYEE_STATUS_VALUES,
            weights=_EMPLOYEE_STATUS_PROBABILITIES,
            k=1
        )[0]

        row = (

            employee_code,

            fake.name(),

            role,

            ROLE_DEPARTMENTS[role],

            fake.date_between(
                start_date="-15y",
                end_date="-30d"
            ),

            status

        )

        batch.append(row)

        if len(batch) == BATCH_SIZE:

            batch_insert(
                connection=connection,
                sql=SQL,
                data=batch,
                table_name="employees"
            )

            batch.clear()

    # Flush remaining rows

    if batch:

        remaining_rows = len(batch)

        batch_insert(
            connection=connection,
            sql=SQL,
            data=batch,
            table_name="employees"
        )

        logger.info(
            f"employees_generator | "
            f"Flushed remaining rows: {remaining_rows}"
        )

    logger.info(
        f"employees_generator | Completed | "
        f"Rows inserted: {ROW_COUNTS['employees']}"
    )

    