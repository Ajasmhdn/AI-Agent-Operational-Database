"""
validate.py

Sprint 2 — 7-layer validation framework.
Validates all tables, FK integrity, business rules,
and demo query guarantees.
"""

import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from config import (
    ROW_COUNTS,
    EXPECTED_QC_MULTIPLIER,
    WORST_SUPPLIER_CODE,
    TOP_TECHNICIAN_CODE,
    MACHINE_TYPES,
    WO_OPEN,
    WO_COMPLETED,
    ML_OPEN,
    ML_IN_PROGRESS,
    QC_FAIL,
    QC_PASS,
    DEFECT_TYPE_NONE
)
from utils.logger import logger


# ============================================================
# HELPERS
# ============================================================

def _query(connection, sql, params=None):
    cursor = connection.cursor()
    cursor.execute(sql, params or ())
    result = cursor.fetchall()
    cursor.close()
    return result


def _scalar(connection, sql, params=None):
    return _query(connection, sql, params)[0][0]


def _pass(msg):
    logger.info(f"PASS | {msg}")


def _fail(msg):
    logger.error(f"FAIL | {msg}")
    return False


# ============================================================
# LAYER 1 — ROW COUNTS
# ============================================================

def validate_row_counts(connection):
    logger.info("validate | Layer 1 | Row counts")

    tables = [
        ("machines",         ROW_COUNTS["machines"]),
        ("employees",        ROW_COUNTS["employees"]),
        ("suppliers",        ROW_COUNTS["suppliers"]),
        ("inventory",        ROW_COUNTS["inventory"]),
        ("work_orders",      ROW_COUNTS["work_orders"]),
        ("maintenance_logs", ROW_COUNTS["maintenance_logs"]),
        ("downtime_events",  ROW_COUNTS["downtime_events"]),
        ("purchase_orders",  ROW_COUNTS["purchase_orders"]),
        ("shift_logs",       ROW_COUNTS["shift_logs"]),
    ]

    passed = True

    for table, expected in tables:
        actual = _scalar(
            connection,
            f"SELECT COUNT(*) FROM {table}"
        )
        if actual != expected:
            _fail(f"{table} | Expected {expected} got {actual}")
            passed = False
        else:
            _pass(f"{table} | {actual} rows")

    # quality_checks — probabilistic target, use tolerance band
    qc_count = _scalar(
        connection,
        "SELECT COUNT(*) FROM quality_checks"
    )
    expected_qc = int(
        ROW_COUNTS["work_orders"] * EXPECTED_QC_MULTIPLIER
    )
    qc_lower = int(expected_qc * 0.95)
    qc_upper = int(expected_qc * 1.05)

    if not (qc_lower <= qc_count <= qc_upper):
        _fail(
            f"quality_checks | "
            f"Expected {qc_lower}–{qc_upper} "
            f"got {qc_count}"
        )
        passed = False
    else:
        _pass(
            f"quality_checks | {qc_count} rows "
            f"(target ~{expected_qc})"
        )

    return passed


# ============================================================
# LAYER 2 — BUSINESS KEY UNIQUENESS
# ============================================================

def validate_business_keys(connection):
    logger.info("validate | Layer 2 | Business key uniqueness")

    checks = [
        ("machines",         "machine_code"),
        ("employees",        "employee_code"),
        ("suppliers",        "supplier_code"),
        ("inventory",        "item_code"),
        ("work_orders",      "work_order_number"),
        ("maintenance_logs", "log_code"),
        ("downtime_events",  "event_code"),
        ("purchase_orders",  "po_number"),
        ("shift_logs",       "shift_code"),
        ("quality_checks",   "qc_code"),
    ]

    passed = True

    for table, col in checks:
        dupes = _scalar(
            connection,
            f"""
            SELECT COUNT(*) FROM (
                SELECT {col}
                FROM {table}
                GROUP BY {col}
                HAVING COUNT(*) > 1
            ) AS dupes
            """
        )
        if dupes > 0:
            _fail(f"{table}.{col} | {dupes} duplicates found")
            passed = False
        else:
            _pass(f"{table}.{col} | unique")

    return passed


# ============================================================
# LAYER 3 — FK ORPHAN CHECKS
# ============================================================

def validate_fk_integrity(connection):
    logger.info("validate | Layer 3 | FK integrity")

    checks = [
        ("work_orders",      "machine_id",    "machines",    "machine_id"),
        ("work_orders",      "item_id",        "inventory",   "item_id"),
        ("maintenance_logs", "machine_id",     "machines",    "machine_id"),
        ("maintenance_logs", "employee_id",    "employees",   "employee_id"),
        ("downtime_events",  "machine_id",     "machines",    "machine_id"),
        ("purchase_orders",  "supplier_id",    "suppliers",   "supplier_id"),
        ("purchase_orders",  "item_id",        "inventory",   "item_id"),
        ("shift_logs",       "employee_id",    "employees",   "employee_id"),
        ("quality_checks",   "machine_id",     "machines",    "machine_id"),
        ("quality_checks",   "work_order_id",  "work_orders", "order_id"),
    ]

    passed = True

    for child, fk, parent, pk in checks:
        orphans = _scalar(
            connection,
            f"""
            SELECT COUNT(*)
            FROM {child} c
            LEFT JOIN {parent} p ON c.{fk} = p.{pk}
            WHERE p.{pk} IS NULL
            """
        )
        if orphans > 0:
            _fail(f"{child}.{fk} | {orphans} orphan rows")
            passed = False
        else:
            _pass(f"{child}.{fk} → {parent}.{pk} | clean")

    return passed


# ============================================================
# LAYER 4 — BUSINESS RULES
# ============================================================

def validate_business_rules(connection):
    logger.info("validate | Layer 4 | Business rules")

    passed = True

    # quantity_completed never exceeds quantity_planned
    v = _scalar(
        connection,
        """
        SELECT COUNT(*) FROM work_orders
        WHERE quantity_completed > quantity_planned
        """
    )
    if v > 0:
        _fail(f"quantity_completed > quantity_planned | {v} violations")
        passed = False
    else:
        _pass("quantity_completed <= quantity_planned | clean")

    # Completed WOs — quantity_completed must equal quantity_planned
    v = _scalar(
        connection,
        f"""
        SELECT COUNT(*) FROM work_orders
        WHERE status = '{WO_COMPLETED}'
        AND quantity_completed != quantity_planned
        """
    )
    if v > 0:
        _fail(f"Completed WO quantity mismatch | {v} rows")
        passed = False
    else:
        _pass("Completed WO quantity = planned | clean")

    # Pass QC → defect_type must be None
    v = _scalar(
        connection,
        f"""
        SELECT COUNT(*) FROM quality_checks
        WHERE result = '{QC_PASS}'
        AND defect_type != '{DEFECT_TYPE_NONE}'
        """
    )
    if v > 0:
        _fail(f"Pass with non-None defect | {v} rows")
        passed = False
    else:
        _pass("Pass → defect_type = None | clean")

    # Fail QC → defect_type must not be None
    v = _scalar(
        connection,
        f"""
        SELECT COUNT(*) FROM quality_checks
        WHERE result = '{QC_FAIL}'
        AND defect_type = '{DEFECT_TYPE_NONE}'
        """
    )
    if v > 0:
        _fail(f"Fail with None defect | {v} rows")
        passed = False
    else:
        _pass("Fail → defect_type != None | clean")

    # Cancelled POs — no actual_delivery_date
    v = _scalar(
        connection,
        """
        SELECT COUNT(*) FROM purchase_orders
        WHERE status = 'Cancelled'
        AND actual_delivery_date IS NOT NULL
        """
    )
    if v > 0:
        _fail(f"Cancelled PO with delivery date | {v} rows")
        passed = False
    else:
        _pass("Cancelled PO → actual_delivery_date NULL | clean")

    # resolved_time never before reported_time
    v = _scalar(
        connection,
        """
        SELECT COUNT(*) FROM maintenance_logs
        WHERE resolved_time < reported_time
        """
    )
    if v > 0:
        _fail(f"resolved_time < reported_time | {v} rows")
        passed = False
    else:
        _pass("resolved_time >= reported_time | clean")

    # downtime end_time never before start_time
    v = _scalar(
        connection,
        """
        SELECT COUNT(*) FROM downtime_events
        WHERE end_time < start_time
        """
    )
    if v > 0:
        _fail(f"downtime end_time < start_time | {v} rows")
        passed = False
    else:
        _pass("downtime end_time >= start_time | clean")

    # Active downtime — end_time NULL but duration_minutes NOT NULL
    v = _scalar(
        connection,
        """
        SELECT COUNT(*) FROM downtime_events
        WHERE end_time IS NULL
        AND duration_minutes IS NOT NULL
        """
    )
    if v > 0:
        _fail(f"Active downtime with duration_minutes set | {v} rows")
        passed = False
    else:
        _pass("Active downtime NULL consistency | clean")

    return passed


# ============================================================
# LAYER 5 — TEMPORAL INTEGRITY
# ============================================================

def validate_temporal_integrity(connection):
    logger.info("validate | Layer 5 | Temporal integrity")

    passed = True

    # inspection_date must be after work_order start_time
    v = _scalar(
        connection,
        """
        SELECT COUNT(*)
        FROM quality_checks qc
        JOIN work_orders wo ON qc.work_order_id = wo.order_id
        WHERE qc.inspection_date < wo.start_time
        """
    )
    if v > 0:
        _fail(f"inspection_date < work_order start_time | {v} rows")
        passed = False
    else:
        _pass("inspection_date >= work_order start_time | clean")

    # WO end_time must be after start_time for closed orders
    v = _scalar(
        connection,
        """
        SELECT COUNT(*) FROM work_orders
        WHERE end_time IS NOT NULL
        AND end_time < start_time
        """
    )
    if v > 0:
        _fail(f"WO end_time < start_time | {v} rows")
        passed = False
    else:
        _pass("WO end_time >= start_time | clean")

    return passed


# ============================================================
# LAYER 6 — NULL LOGIC
# ============================================================

def validate_null_logic(connection):
    logger.info("validate | Layer 6 | NULL logic")

    passed = True

    # Open and In Progress WOs — end_time must be NULL
    v = _scalar(
        connection,
        f"""
        SELECT COUNT(*) FROM work_orders
        WHERE status IN ('{WO_OPEN}', 'In Progress')
        AND end_time IS NOT NULL
        """
    )
    if v > 0:
        _fail(f"Open/InProgress WO with end_time set | {v} rows")
        passed = False
    else:
        _pass("Open/InProgress WO end_time = NULL | clean")

    # Resolved maintenance logs — resolved_time must NOT be NULL
    v = _scalar(
        connection,
        """
        SELECT COUNT(*) FROM maintenance_logs
        WHERE status = 'Resolved'
        AND resolved_time IS NULL
        """
    )
    if v > 0:
        _fail(f"Resolved log missing resolved_time | {v} rows")
        passed = False
    else:
        _pass("Resolved log has resolved_time | clean")

    # Open and In Progress maintenance logs — resolved_time must be NULL
    v = _scalar(
        connection,
        f"""
        SELECT COUNT(*) FROM maintenance_logs
        WHERE status IN ('{ML_OPEN}', '{ML_IN_PROGRESS}')
        AND resolved_time IS NOT NULL
        """
    )
    if v > 0:
        _fail(f"Open/InProgress log with resolved_time set | {v} rows")
        passed = False
    else:
        _pass("Open/InProgress log resolved_time = NULL | clean")

    # Open and In Progress maintenance logs — resolution_notes must be NULL
    v = _scalar(
        connection,
        f"""
        SELECT COUNT(*) FROM maintenance_logs
        WHERE status IN ('{ML_OPEN}', '{ML_IN_PROGRESS}')
        AND resolution_notes IS NOT NULL
        """
    )
    if v > 0:
        _fail(f"Open/InProgress log with resolution_notes set | {v} rows")
        passed = False
    else:
        _pass("Open/InProgress log resolution_notes = NULL | clean")

    # Active downtime — both end_time and duration_minutes must be NULL
    v = _scalar(
        connection,
        """
        SELECT COUNT(*) FROM downtime_events
        WHERE end_time IS NULL
        AND duration_minutes IS NOT NULL
        """
    )
    if v > 0:
        _fail(f"Active downtime with duration_minutes set | {v} rows")
        passed = False
    else:
        _pass("Active downtime duration_minutes = NULL | clean")

    # Non-delivered POs — actual_delivery_date must be NULL
    v = _scalar(
        connection,
        """
        SELECT COUNT(*) FROM purchase_orders
        WHERE status != 'Delivered'
        AND actual_delivery_date IS NOT NULL
        """
    )
    if v > 0:
        _fail(f"Non-delivered PO with actual_delivery_date | {v} rows")
        passed = False
    else:
        _pass("Non-delivered PO actual_delivery_date = NULL | clean")

    return passed


# ============================================================
# LAYER 7 — DEMO GUARANTEES
# ============================================================

def validate_demo_guarantees(connection):
    logger.info("validate | Layer 7 | Demo guarantees")

    passed = True
    now = datetime.now()

    # Q1 — downtime events exist last month
    last_month = (now - timedelta(days=30)).strftime('%Y-%m-%d')
    v = _scalar(
        connection,
        f"""
        SELECT COUNT(*) FROM downtime_events
        WHERE start_time >= '{last_month}'
        AND duration_minutes IS NOT NULL
        """
    )
    if v == 0:
        _fail("Q1 | No completed downtime events last month")
        passed = False
    else:
        _pass(f"Q1 | {v} downtime events last month")

    # Q2 — inventory below reorder level
    v = _scalar(
        connection,
        """
        SELECT COUNT(*) FROM inventory
        WHERE quantity_in_stock < reorder_level
        """
    )
    if v == 0:
        _fail("Q2 | No items below reorder level")
        passed = False
    else:
        _pass(f"Q2 | {v} items below reorder level")

    # Q3 — open WOs older than 7 days
    seven_days_ago = (now - timedelta(days=7)).strftime('%Y-%m-%d')
    v = _scalar(
        connection,
        f"""
        SELECT COUNT(*) FROM work_orders
        WHERE status = '{WO_OPEN}'
        AND start_time < '{seven_days_ago}'
        """
    )
    if v == 0:
        _fail("Q3 | No open WOs older than 7 days")
        passed = False
    else:
        _pass(f"Q3 | {v} open WOs older than 7 days")

    # Q4 — worst supplier has late deliveries
    v = _scalar(
        connection,
        f"""
        SELECT COUNT(*) FROM purchase_orders po
        JOIN suppliers s ON po.supplier_id = s.supplier_id
        WHERE s.supplier_code = '{WORST_SUPPLIER_CODE}'
        AND po.actual_delivery_date > po.expected_delivery_date
        """
    )
    if v == 0:
        _fail("Q4 | Worst supplier has no late deliveries")
        passed = False
    else:
        _pass(f"Q4 | Worst supplier has {v} late deliveries")

    # Q5 — quality failures this quarter
    quarter_start = now.replace(
        month=((now.month - 1) // 3) * 3 + 1,
        day=1
    )
    v = _scalar(
        connection,
        f"""
        SELECT COUNT(*) FROM quality_checks
        WHERE result = '{QC_FAIL}'
        AND inspection_date >= '{quarter_start.strftime('%Y-%m-%d')}'
        """
    )
    if v == 0:
        _fail("Q5 | No quality failures this quarter")
        passed = False
    else:
        _pass(f"Q5 | {v} quality failures this quarter")

    # Q6 — top technician has resolved logs
    v = _scalar(
        connection,
        f"""
        SELECT COUNT(*) FROM maintenance_logs ml
        JOIN employees e ON ml.employee_id = e.employee_id
        WHERE e.employee_code = '{TOP_TECHNICIAN_CODE}'
        AND ml.status = 'Resolved'
        """
    )
    if v == 0:
        _fail("Q6 | Top technician has no resolved logs")
        passed = False
    else:
        _pass(f"Q6 | Top technician has {v} resolved logs")

    # Q7 — all machine types have downtime records
    v = _scalar(
        connection,
        """
        SELECT COUNT(DISTINCT m.machine_type)
        FROM downtime_events de
        JOIN machines m ON de.machine_id = m.machine_id
        WHERE de.duration_minutes IS NOT NULL
        """
    )
    expected_types = len(MACHINE_TYPES)
    if v < expected_types:
        _fail(f"Q7 | Only {v}/{expected_types} machine types have downtime")
        passed = False
    else:
        _pass(f"Q7 | All {v} machine types have downtime")

    # Q8 — all 4 warehouse locations have stock
    v = _scalar(
        connection,
        "SELECT COUNT(DISTINCT warehouse_location) FROM inventory"
    )
    if v < 4:
        _fail(f"Q8 | Only {v}/4 warehouses have inventory")
        passed = False
    else:
        _pass(f"Q8 | {v} warehouse locations present")

    # Q9 — completed + pending WOs exist in last 7 days
    statuses = _query(
        connection,
        f"""
        SELECT status, COUNT(*) FROM work_orders
        WHERE start_time >= '{seven_days_ago}'
        GROUP BY status
        """
    )
    status_dict = {row[0]: row[1] for row in statuses}
    completed_count = status_dict.get(WO_COMPLETED, 0)
    pending_count = (
        status_dict.get(WO_OPEN, 0) +
        status_dict.get("In Progress", 0)
    )
    if completed_count == 0:
        _fail("Q9 | No completed WOs last week")
        passed = False
    elif pending_count == 0:
        _fail("Q9 | No pending WOs last week")
        passed = False
    else:
        _pass(
            f"Q9 | Last week — "
            f"Completed: {completed_count} "
            f"Pending: {pending_count}"
        )

    # Q10 — defect trend covers last 6 calendar months
    six_months_ago = (
        now - relativedelta(months=6)
    ).replace(day=1)

    v = _scalar(
        connection,
        f"""
        SELECT COUNT(DISTINCT DATE_FORMAT(inspection_date, '%%Y-%%m'))
        FROM quality_checks
        WHERE result = '{QC_FAIL}'
        AND inspection_date >= '{six_months_ago.strftime('%Y-%m-%d')}'
        """
    )
    if v < 6:
        _fail(f"Q10 | Only {v}/6 months have defect data")
        passed = False
    else:
        _pass(f"Q10 | Defect trend covers {v} months")

    return passed


# ============================================================
# VALIDATE ALL
# ============================================================

def validate_all(connection):
    logger.info("validate | Starting full validation")

    results = {
        "Layer 1 Row Counts":      validate_row_counts(connection),
        "Layer 2 Business Keys":   validate_business_keys(connection),
        "Layer 3 FK Integrity":    validate_fk_integrity(connection),
        "Layer 4 Business Rules":  validate_business_rules(connection),
        "Layer 5 Temporal":        validate_temporal_integrity(connection),
        "Layer 6 NULL Logic":      validate_null_logic(connection),
        "Layer 7 Demo Guarantees": validate_demo_guarantees(connection),
    }

    logger.info("validate | ── Summary ──")

    all_passed = True

    for layer, passed in results.items():
        if passed:
            logger.info(f"validate | ✓ {layer}")
        else:
            logger.error(f"validate | ✗ {layer}")
            all_passed = False

    if all_passed:
        logger.info(
            "validate | ALL LAYERS PASSED — "
            "data generation complete"
        )
    else:
        logger.error(
            "validate | VALIDATION FAILED — "
            "check errors.log"
        )
        sys.exit(1)


# ============================================================
# STANDALONE ENTRY POINT
# ============================================================

if __name__ == "__main__":

    from utils.db_connect import get_connection

    connection = get_connection()

    try:
        validate_all(connection)
    finally:
        connection.close()
        logger.info(
            "validate | Database connection closed"
        )