"""
downtime_events_generator.py

Generate downtime event transactional data.
"""

import random
from datetime import timedelta

from tqdm import tqdm

from config import (
    ROW_COUNTS,
    BATCH_SIZE,
    KEY_PREFIXES,
    DOWNTIME_SEVERITY_WEIGHTS,
    DOWNTIME_REASON_SEVERITY_MAP,
    DOWNTIME_ACTIVE_RATE,
    HIGH_DOWNTIME_MACHINE_RATE
)

from utils.batch_insert import batch_insert
from utils.date_utils import (
    generate_weighted_datetime
)
from utils.logger import logger


# ============================================================
# SQL
# ============================================================

SQL = """
INSERT INTO downtime_events (
    event_code,
    machine_id,
    start_time,
    end_time,
    duration_minutes,
    reason,
    severity
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""


# ============================================================
# CACHED VALUES
# ============================================================

_DOWNTIME_SEVERITY_VALUES = list(
    DOWNTIME_SEVERITY_WEIGHTS.keys()
)

_DOWNTIME_SEVERITY_PROBABILITIES = list(
    DOWNTIME_SEVERITY_WEIGHTS.values()
)

_REASON_MAP = DOWNTIME_REASON_SEVERITY_MAP


# ============================================================
# DURATION RANGES (MINUTES)
# ============================================================

_DURATION_RANGES = {

    "Low": (
        30,
        120
    ),

    "Medium": (
        120,
        480
    ),

    "High": (
        480,
        1440
    )

}


# ============================================================
# FK FETCHER
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


# ============================================================
# GENERATOR
# ============================================================

def generate_downtime_events(connection):
    """
    Generate downtime event records.
    """

    logger.info(
        f"downtime_events_generator | Started | "
        f"Target: {ROW_COUNTS['downtime_events']} rows"
    )

    machine_ids = _fetch_machine_ids(connection)

    logger.info(
        f"downtime_events_generator | "
        f"Loaded {len(machine_ids)} machines"
    )

    # ========================================================
    # Q1 Demo Guarantee
    # ========================================================

    high_downtime_machine_id = machine_ids[0]

    logger.info(
        f"downtime_events_generator | "
        f"High downtime machine seeded: "
        f"{high_downtime_machine_id}"
    )

    batch = []

    inserted_rows = 0

    for i in tqdm(
        range(ROW_COUNTS["downtime_events"]),
        desc="Generating downtime events",
        unit="rows"
    ):

        event_code = (
            f"{KEY_PREFIXES['downtime_event']}-{i + 1:06d}"
        )

        if random.random() < HIGH_DOWNTIME_MACHINE_RATE:

            machine_id = high_downtime_machine_id

        else:

            machine_id = random.choice(
                machine_ids
            )

        severity = random.choices(
            population=_DOWNTIME_SEVERITY_VALUES,
            weights=_DOWNTIME_SEVERITY_PROBABILITIES,
            k=1
        )[0]

        reason = random.choice(
            _REASON_MAP[severity]
        )

        start_time = (
            generate_weighted_datetime()
        )

        is_active = (
            random.random() < DOWNTIME_ACTIVE_RATE
        )

        if is_active:

            duration_minutes = None

            end_time = None

        else:

            duration_minutes = random.randint(
                *_DURATION_RANGES[severity]
            )

            end_time = (
                start_time +
                timedelta(
                    minutes=duration_minutes
                )
            )

        row = (

            event_code,

            machine_id,

            start_time,

            end_time,

            duration_minutes,

            reason,

            severity

        )

        batch.append(row)

        if len(batch) == BATCH_SIZE:

            rows_to_insert = len(batch)

            batch_insert(
                connection=connection,
                sql=SQL,
                data=batch,
                table_name="downtime_events"
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
            table_name="downtime_events"
        )

        inserted_rows += remaining_rows

        logger.info(
            f"downtime_events_generator | "
            f"Flushed remaining rows: "
            f"{remaining_rows}"
        )

    logger.info(
        f"downtime_events_generator | Completed | "
        f"Rows inserted: "
        f"{inserted_rows}"
    )