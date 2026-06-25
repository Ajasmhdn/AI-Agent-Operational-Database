"""
shift_logs_generator.py

Generate shift log transactional data.
"""

import random

from tqdm import tqdm

from config import (
    ROW_COUNTS,
    BATCH_SIZE,
    KEY_PREFIXES,
    SHIFT_TYPES,
    SHIFT_NOTES
)

from utils.batch_insert import batch_insert
from utils.date_utils import (
    generate_random_date,
    generate_shift_times
)
from utils.logger import logger


# ============================================================
# SQL
# ============================================================

SQL = """
INSERT INTO shift_logs (
    shift_code,
    employee_id,
    shift_date,
    shift_type,
    start_time,
    end_time,
    notes
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""


# ============================================================
# FK FETCHER
# ============================================================

def _fetch_employee_ids(connection):
    """
    Fetch employee IDs once.
    """

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT employee_id
        FROM employees
        """
    )

    employee_ids = [
        row[0]
        for row in cursor.fetchall()
    ]

    cursor.close()

    return employee_ids


# ============================================================
# GENERATOR
# ============================================================

def generate_shift_logs(connection):
    """
    Generate shift log records.
    """

    logger.info(
        f"shift_logs_generator | Started | "
        f"Target: {ROW_COUNTS['shift_logs']} rows"
    )

    employee_ids = _fetch_employee_ids(
        connection
    )

    logger.info(
        f"shift_logs_generator | "
        f"Loaded {len(employee_ids)} employees"
    )

    batch = []

    inserted_rows = 0

    for i in tqdm(
        range(ROW_COUNTS["shift_logs"]),
        desc="Generating shift logs",
        unit="rows"
    ):

        shift_code = (
            f"{KEY_PREFIXES['shift_log']}-{i + 1:06d}"
        )

        employee_id = random.choice(
            employee_ids
        )

        shift_date = generate_random_date()

        shift_type = random.choice(
            SHIFT_TYPES
        )

        start_time, end_time = (
            generate_shift_times(
                shift_type=shift_type,
                shift_date=shift_date
            )
        )

        notes = (
            random.choice(SHIFT_NOTES)
            if random.random() < 0.20
            else None
        )

        row = (

            shift_code,

            employee_id,

            shift_date,

            shift_type,

            start_time,

            end_time,

            notes

        )

        batch.append(row)

        if len(batch) == BATCH_SIZE:

            rows_to_insert = len(batch)

            batch_insert(
                connection=connection,
                sql=SQL,
                data=batch,
                table_name="shift_logs"
            )

            inserted_rows += rows_to_insert

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
            table_name="shift_logs"
        )

        inserted_rows += remaining_rows

        logger.info(
            f"shift_logs_generator | "
            f"Flushed remaining rows: "
            f"{remaining_rows}"
        )

    logger.info(
        f"shift_logs_generator | Completed | "
        f"Rows inserted: "
        f"{inserted_rows}"
    )