"""
business_rules.py

Central business rules for synthetic data generation.
"""

import random

from datetime import datetime, timedelta

from config import (
    WO_OPEN,
    WO_IN_PROGRESS,
    WO_COMPLETED,
    WO_CANCELLED,
    ML_RESOLVED,
    PO_DELIVERED,
    QC_PASS,
    DEFECT_TYPE_NONE,
    DEFECT_TYPES
)

# -------------------------------------------------------
# Resolution note templates
# -------------------------------------------------------

_RESOLUTION_NOTES = [
    "Component replaced and machine tested.",
    "Issue resolved after calibration.",
    "Electrical fault corrected and verified.",
    "Lubrication completed and operation restored.",
    "Sensor alignment adjusted successfully.",
    "Hydraulic pressure restored after inspection.",
    "Preventive maintenance completed.",
    "Fault isolated and repaired."
]


# -------------------------------------------------------
# Work Orders
# -------------------------------------------------------

def get_quantity_completed(
    quantity_planned: int,
    status: str
) -> int:
    """
    Determine quantity completed based on work order status.
    """

    if status == WO_OPEN:
        return 0

    if status == WO_IN_PROGRESS:
        return random.randint(
            1,
            max(1, int(quantity_planned * 0.99))
        )

    if status == WO_COMPLETED:
        return quantity_planned

    if status == WO_CANCELLED:
        return random.randint(
            0,
            max(0, int(quantity_planned * 0.90))
        )

    raise ValueError(
        f"Unsupported work order status: {status}"
    )


# -------------------------------------------------------
# Maintenance Logs
# -------------------------------------------------------

def get_resolution_details(
    reported_time: datetime
):
    """
    Generate resolved_time and resolution notes.
    """

    resolved_time = reported_time + timedelta(
        hours=random.randint(1, 72)
    )

    resolution_note = random.choice(
        _RESOLUTION_NOTES
    )

    return resolved_time, resolution_note

def get_maintenance_resolution(
    status: str,
    reported_time: datetime
):
    """
    Return resolution details based on maintenance status.

    Open and In Progress records do not have a
    resolved timestamp or resolution note.
    """

    if status != ML_RESOLVED:
        return None, None

    return get_resolution_details(
        reported_time=reported_time
    )


# -------------------------------------------------------
# Quality Checks
# -------------------------------------------------------

def get_defect_type(
    result: str
) -> str:
    """
    Determine defect type based on QC result.
    """

    if result == QC_PASS:
        return DEFECT_TYPE_NONE

    return random.choice(
        DEFECT_TYPES
    )


# -------------------------------------------------------
# Purchase Orders
# -------------------------------------------------------

def get_actual_delivery_date(
    expected_delivery_date,
    status: str,
    is_worst_supplier: bool = False
):
    """
    Determine actual delivery date.
    """

    if status != PO_DELIVERED:
        return None

    if is_worst_supplier:
        delay_days = random.randint(
            3,
            14
        )

    else:

        delay_days = random.choice([
            -2,
            -1,
            0,
            0,
            0,
            1,
            2,
            3
        ])

    return expected_delivery_date + timedelta(
        days=delay_days
    )