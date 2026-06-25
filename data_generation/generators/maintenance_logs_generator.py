"""
maintenance_logs_generator.py

Generate maintenance log transactional data.
"""

import random

from tqdm import tqdm

from config import (
    ROW_COUNTS,
    BATCH_SIZE,
    KEY_PREFIXES,
    ISSUE_TYPES,
    ML_STATUS_WEIGHTS,
    TOP_TECHNICIAN_CODE,
    TOP_TECHNICIAN_PROBABILITY
)

from utils.batch_insert import batch_insert
from utils.business_rules import (
    get_maintenance_resolution
)
from utils.date_utils import (
    generate_weighted_datetime
)
from utils.logger import logger


# ============================================================
# SQL
# ============================================================

SQL = """
INSERT INTO maintenance_logs (
    log_code,
    machine_id,
    employee_id,
    issue_type,
    issue_description,
    reported_time,
    resolved_time,
    resolution_notes,
    status
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


# ============================================================
# CACHED STATUS VALUES
# ============================================================

_ML_STATUS_VALUES = list(
    ML_STATUS_WEIGHTS.keys()
)

_ML_STATUS_PROBABILITIES = list(
    ML_STATUS_WEIGHTS.values()
)


# ============================================================
# ISSUE DESCRIPTION TEMPLATES
# ============================================================

_ISSUE_DESCRIPTION_TEMPLATES = [
    "{} fault detected on machine. Reported for inspection and corrective action.",
    "{} issue observed during routine maintenance inspection.",
    "{} anomaly reported by operator during production.",
    "{} malfunction requiring immediate maintenance intervention.",
    "{} problem identified and escalated to maintenance team."
]


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


def _fetch_technician_ids(connection):
    """
    Fetch technician IDs once.
    """

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT employee_id
        FROM employees
        WHERE role = 'Technician'
        """
    )

    technician_ids = [
        row[0]
        for row in cursor.fetchall()
    ]

    cursor.close()

    return technician_ids


def _fetch_top_technician_id(connection):
    """
    Fetch top technician ID.
    """

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT employee_id
        FROM employees
        WHERE employee_code = %s
        """,
        (TOP_TECHNICIAN_CODE,)
    )

    result = cursor.fetchone()

    cursor.close()

    if result is None:

        raise ValueError(
            f"Top technician not found: "
            f"{TOP_TECHNICIAN_CODE}"
        )

    return result[0]


# ============================================================
# GENERATOR
# ============================================================

def generate_maintenance_logs(connection):
    """
    Generate maintenance log records.
    """

    logger.info(
        f"maintenance_logs_generator | Started | "
        f"Target: {ROW_COUNTS['maintenance_logs']} rows"
    )

    machine_ids = _fetch_machine_ids(connection)

    technician_ids = _fetch_technician_ids(connection)

    top_technician_id = (
        _fetch_top_technician_id(connection)
    )

    logger.info(
        f"maintenance_logs_generator | "
        f"Top technician loaded: "
        f"{TOP_TECHNICIAN_CODE}"
    )

    batch = []

    inserted_rows = 0

    for i in tqdm(
        range(ROW_COUNTS["maintenance_logs"]),
        desc="Generating maintenance logs",
        unit="rows"
    ):

        log_code = (
            f"{KEY_PREFIXES['maintenance_log']}-{i + 1:06d}"
        )

        # ====================================================
        # Q6 Demo Guarantee
        # ====================================================

        if random.random() < TOP_TECHNICIAN_PROBABILITY:

            employee_id = top_technician_id

        else:

            employee_id = random.choice(
                technician_ids
            )

        issue_type = random.choice(
            ISSUE_TYPES
        )

        status = random.choices(
            population=_ML_STATUS_VALUES,
            weights=_ML_STATUS_PROBABILITIES,
            k=1
        )[0]

        reported_time = (
            generate_weighted_datetime()
        )

        resolved_time, resolution_notes = (
            get_maintenance_resolution(
                status=status,
                reported_time=reported_time
            )
        )

        issue_description = random.choice(
            _ISSUE_DESCRIPTION_TEMPLATES
        ).format(
            issue_type
        )

        row = (

            log_code,

            random.choice(machine_ids),

            employee_id,

            issue_type,

            issue_description,

            reported_time,

            resolved_time,

            resolution_notes,

            status

        )

        batch.append(row)

        if len(batch) == BATCH_SIZE:

            batch_insert(
                connection=connection,
                sql=SQL,
                data=batch,
                table_name="maintenance_logs"
            )

            inserted_rows += len(batch)

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
            table_name="maintenance_logs"
        )

        inserted_rows += remaining_rows

        logger.info(
            f"maintenance_logs_generator | "
            f"Flushed remaining rows: "
            f"{remaining_rows}"
        )

    logger.info(
        f"maintenance_logs_generator | Completed | "
        f"Rows inserted: "
        f"{inserted_rows}"
    )