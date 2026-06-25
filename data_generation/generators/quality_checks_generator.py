"""
quality_checks_generator.py

Generate quality check transactional data.
"""

import random
from datetime import datetime, timedelta

from tqdm import tqdm

from config import (
    BATCH_SIZE,
    KEY_PREFIXES,
    QC_INSPECTION_WEIGHTS,
    QUALITY_FAIL_RATE,
    EXPECTED_QC_MULTIPLIER,
    ROW_COUNTS,
    QC_PASS,
    QC_FAIL,
    RECENT_DEFECT_RATE
)

from utils.batch_insert import batch_insert
from utils.business_rules import (
    get_defect_type
)
from utils.logger import logger


# ============================================================
# SQL
# ============================================================

SQL = """
INSERT INTO quality_checks (
    qc_code,
    machine_id,
    work_order_id,
    product_name,
    result,
    defect_type,
    inspection_date
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""


# ============================================================
# CACHED VALUES
# ============================================================

_QC_INSPECTION_COUNTS = list(
    QC_INSPECTION_WEIGHTS.keys()
)

_QC_INSPECTION_PROBABILITIES = list(
    QC_INSPECTION_WEIGHTS.values()
)

_NOW = datetime.now()


# ============================================================
# FK FETCHER
# ============================================================

def _fetch_work_orders(connection):
    """
    Fetch work order information once.
    """

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            order_id,
            machine_id,
            product_name,
            start_time
        FROM work_orders
        """
    )

    work_orders = cursor.fetchall()

    cursor.close()

    return work_orders


# ============================================================
# GENERATOR
# ============================================================

def generate_quality_checks(connection):
    """
    Generate quality check records.
    """

    expected_rows = int(
        ROW_COUNTS["work_orders"]
        *
        EXPECTED_QC_MULTIPLIER
    )

    logger.info(
        f"quality_checks_generator | Started | "
        f"Expected rows: {expected_rows}"
    )

    work_orders = _fetch_work_orders(
        connection
    )

    logger.info(
        f"quality_checks_generator | "
        f"Loaded {len(work_orders)} work orders"
    )

    batch = []

    inserted_rows = 0

    qc_counter = 1

    for (
        work_order_id,
        machine_id,
        product_name,
        work_order_start_time
    ) in tqdm(
        work_orders,
        desc="Generating quality checks",
        unit="work_orders"
    ):

        inspection_count = random.choices(
            population=_QC_INSPECTION_COUNTS,
            weights=_QC_INSPECTION_PROBABILITIES,
            k=1
        )[0]

        for _ in range(inspection_count):

            qc_code = (
                f"{KEY_PREFIXES['quality_check']}-"
                f"{qc_counter:06d}"
            )

            qc_counter += 1

            if random.random() < QUALITY_FAIL_RATE:

                result = QC_FAIL

            else:

                result = QC_PASS

            defect_type = get_defect_type(
                result=result
            )

            # =================================================
            # Base inspection time
            # =================================================

            base_inspection_date = (
                work_order_start_time
                +
                timedelta(
                    minutes=random.randint(
                        30,
                        1440
                    )
                )
            )

            # =================================================
            # Q10 Demo Guarantee
            # =================================================

            if (
                result == QC_FAIL
                and random.random() < RECENT_DEFECT_RATE
            ):

                recent_candidate = (
                    _NOW
                    -
                    timedelta(
                        days=random.randint(
                            0,
                            180
                        )
                    )
                )

                inspection_date = max(
                    base_inspection_date,
                    recent_candidate
                )

            else:

                inspection_date = base_inspection_date

            row = (

                qc_code,

                machine_id,

                work_order_id,

                product_name,

                result,

                defect_type,

                inspection_date

            )

            batch.append(row)

            if len(batch) == BATCH_SIZE:

                rows_to_insert = len(batch)

                batch_insert(
                    connection=connection,
                    sql=SQL,
                    data=batch,
                    table_name="quality_checks"
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
            table_name="quality_checks"
        )

        inserted_rows += remaining_rows

        logger.info(
            f"quality_checks_generator | "
            f"Flushed remaining rows: "
            f"{remaining_rows}"
        )

    logger.info(
        f"quality_checks_generator | Completed | "
        f"Rows inserted: "
        f"{inserted_rows}"
    )