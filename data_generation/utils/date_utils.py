"""
date_utils.py

Date and time utilities for synthetic data generation.
"""

import random
from datetime import datetime, timedelta
from config import DATE_END, DATE_WEIGHTS, SHIFT_CONFIG

# ============================================================
# CACHE DATE BUCKETS
# ============================================================

_DATE_BUCKETS = list(DATE_WEIGHTS.keys())
_DATE_BUCKET_WEIGHTS = [
    value[0]
    for value in DATE_WEIGHTS.values()
]

# ============================================================
# FUNCTIONS
# ============================================================

def generate_weighted_datetime() -> datetime:
    """
    Generate datetime using 18-month weighted distribution.
    """
    bucket = random.choices(
        population=_DATE_BUCKETS,
        weights=_DATE_BUCKET_WEIGHTS,
        k=1
    )[0]

    _, start_month, end_month = DATE_WEIGHTS[bucket]

    start_date = DATE_END - timedelta(days=end_month * 30)
    end_date   = DATE_END - timedelta(days=start_month * 30)

    seconds = int(
        (end_date - start_date).total_seconds()
    )

    return start_date + timedelta(
        seconds=random.randint(0, seconds)
    )


def generate_random_date():
    """
    Return only date component.
    """
    return generate_weighted_datetime().date()


def generate_end_time(
    start_time: datetime,
    min_hours: int = 1,
    max_hours: int = 24
) -> datetime:
    """
    Generate end time after start time.
    """
    return start_time + timedelta(
        hours=random.randint(
            min_hours,
            max_hours
        )
    )


def generate_shift_times(
    shift_type: str,
    shift_date
):
    """
    Generate shift start and end times.
    Night shift correctly crosses midnight via timedelta.
    """
    if isinstance(shift_date, datetime):
        shift_date = shift_date.date()

    config = SHIFT_CONFIG[shift_type]

    start_time = datetime.combine(
        shift_date,
        datetime.min.time()
    ) + timedelta(
        hours=config["start_hour"]
    )

    end_time = start_time + timedelta(
        hours=config["duration_hours"]
    )

    return start_time, end_time


def generate_downtime_times(
    is_active: bool
):
    """
    Generate downtime timings.
    Active events return None for end_time and duration_minutes.
    Completed events derive end_time from start + duration.
    """
    start_time = generate_weighted_datetime()

    if is_active:
        return start_time, None, None

    duration_minutes = random.randint(15, 480)

    end_time = start_time + timedelta(
        minutes=duration_minutes
    )

    return (
        start_time,
        end_time,
        duration_minutes
    )