"""
suppliers_generator.py

Generate supplier master data.
"""

import random

from tqdm import tqdm

from config import (
    fake,
    ROW_COUNTS,
    BATCH_SIZE,
    KEY_PREFIXES,
    COUNTRIES,
    SUPPLIER_STATUS_WEIGHTS,
    GOOD_SUPPLIER_SCORE_RANGE,
    WORST_SUPPLIER_SCORE_RANGE,
    WORST_SUPPLIER_CODE
)

from utils.batch_insert import batch_insert
from utils.logger import logger


# ============================================================
# SQL
# ============================================================

SQL = """
INSERT INTO suppliers (
    supplier_code,
    supplier_name,
    contact_phone,
    contact_email,
    lead_time_days,
    reliability_score,
    country,
    status
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""


# ============================================================
# CACHED VALUES
# ============================================================

_SUPPLIER_STATUS_VALUES = list(
    SUPPLIER_STATUS_WEIGHTS.keys()
)

_SUPPLIER_STATUS_PROBABILITIES = list(
    SUPPLIER_STATUS_WEIGHTS.values()
)


# ============================================================
# GENERATOR
# ============================================================

def generate_suppliers(connection):
    """
    Generate supplier master records.
    """

    logger.info(
        f"suppliers_generator | Started | "
        f"Target: {ROW_COUNTS['suppliers']} rows"
    )

    batch = []

    for i in tqdm(
        range(ROW_COUNTS["suppliers"]),
        desc="Generating suppliers",
        unit="rows"
    ):

        supplier_code = (
            f"{KEY_PREFIXES['supplier']}-{i + 1:05d}"
        )

        status = random.choices(
            population=_SUPPLIER_STATUS_VALUES,
            weights=_SUPPLIER_STATUS_PROBABILITIES,
            k=1
        )[0]

        # ====================================================
        # Demo guarantee: one intentionally poor supplier
        # ====================================================

        if supplier_code == WORST_SUPPLIER_CODE:

            reliability_score = round(
                random.uniform(
                    *WORST_SUPPLIER_SCORE_RANGE
                ),
                2
            )

            logger.info(
                f"suppliers_generator | "
                f"Worst supplier seeded: {supplier_code} | "
                f"Score: {reliability_score}"
            )

        else:

            reliability_score = round(
                random.uniform(
                    *GOOD_SUPPLIER_SCORE_RANGE
                ),
                2
            )

        # ====================================================
        # Nullable columns
        # ====================================================

        contact_phone = (
            fake.numerify("+##-##########")
            if random.random() < 0.90
            else None
        )

        contact_email = (
            fake.company_email()[:100]
            if random.random() < 0.90
            else None
        )

        row = (

            supplier_code,

            fake.company()[:100],

            contact_phone,

            contact_email,

            random.randint(3, 30),

            reliability_score,

            random.choice(COUNTRIES),

            status

        )

        batch.append(row)

        if len(batch) == BATCH_SIZE:

            batch_insert(
                connection=connection,
                sql=SQL,
                data=batch,
                table_name="suppliers"
            )

            batch.clear()

    # ========================================================
    # Flush remaining rows
    # ========================================================

    if batch:

        remaining_rows = len(batch)

        batch_insert(
            connection=connection,
            sql=SQL,
            data=batch,
            table_name="suppliers"
        )

        logger.info(
            f"suppliers_generator | "
            f"Flushed remaining rows: {remaining_rows}"
        )

    logger.info(
        f"suppliers_generator | Completed | "
        f"Rows inserted: {ROW_COUNTS['suppliers']}"
    )