"""
config.py

Central configuration file for Sprint 2 synthetic data generation.

Contains:
- Database configuration
- Random seed
- Batch settings
- Row counts
- Date distributions
- Enumerations
- Business key prefixes
- Status constants
- Distribution weights
- Demo guarantee parameters

Approved Version: v1.0
"""

import random
from datetime import datetime, timedelta
from faker import Faker
from dotenv import load_dotenv
import os

# ============================================================
# REPRODUCIBILITY
# ============================================================

RANDOM_SEED = 42

random.seed(RANDOM_SEED)

fake = Faker()
Faker.seed(RANDOM_SEED)

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

# ============================================================
# BATCH CONFIGURATION
# ============================================================

BATCH_SIZE = 5000

# ============================================================
# ROW COUNTS
# ============================================================

ROW_COUNTS = {

    # Master tables

    "machines": 500,
    "employees": 1000,
    "suppliers": 200,
    "inventory": 1000,

    # Transaction tables
    "work_orders": 100000,
    "maintenance_logs": 100000,
    "downtime_events": 100000,
    "purchase_orders": 100000,
    "shift_logs": 100000

    # quality_checks intentionally omitted
    # generated dynamically from work orders
}

# ============================================================
# DATE CONFIGURATION
# ============================================================

DATE_END = datetime.now()

DATE_START = DATE_END - timedelta(days=540)

# (weight, start_month_back, end_month_back)

DATE_WEIGHTS = {

    "recent": (0.60, 0, 6),

    "mid": (0.30, 6, 12),

    "old": (0.10, 12, 18)

}

# ============================================================
# BUSINESS KEY PREFIXES
# ============================================================

KEY_PREFIXES = {

    "machine": "MCH",
    "employee": "EMP",
    "supplier": "SUP",
    "inventory": "ITM",
    "work_order": "WO",
    "maintenance_log": "ML",
    "downtime_event": "DE",
    "purchase_order": "PO",
    "shift_log": "SH",
    "quality_check": "QC"

}

# ============================================================
# STATUS CONSTANTS
# ============================================================

# Work Orders

WO_OPEN = "Open"
WO_IN_PROGRESS = "In Progress"
WO_COMPLETED = "Completed"
WO_CANCELLED = "Cancelled"

# Maintenance Logs

ML_OPEN = "Open"
ML_IN_PROGRESS = "In Progress"
ML_RESOLVED = "Resolved"

# Purchase Orders

PO_ORDERED = "Ordered"
PO_DELIVERED = "Delivered"
PO_CANCELLED = "Cancelled"

# Quality Checks

QC_PASS = "Pass"
QC_FAIL = "Fail"

# Defect Types

DEFECT_TYPE_NONE = "None"

# ============================================================
# MASTER TABLE ENUM VALUES
# ============================================================

MACHINE_TYPES = [
    "CNC",
    "Lathe",
    "Press",
    "Welder",
    "Conveyor",
    "Drill",
    "Milling",
    "Grinding",
    "Assembly Robot",
    "Laser Cutter"
]

MACHINE_STATUSES = [
    "Active",
    "Maintenance",
    "Retired"
]

MACHINE_STATUS_WEIGHTS = {

    "Active": 0.70,
    "Maintenance": 0.20,
    "Retired": 0.10

}


PRODUCTION_LINES = [
    "Line-1",
    "Line-2",
    "Line-3",
    "Line-4",
    "Line-5",
    "Line-6",
    "Line-7",
    "Line-8",
    "Line-9",
    "Line-10"
]

LOCATIONS = [
    "Zone-A Floor-1",
    "Zone-A Floor-2",
    "Zone-B Floor-1",
    "Zone-B Floor-2",
    "Zone-C Floor-1",
    "Zone-C Floor-2",
    "Zone-D Floor-1",
    "Zone-D Floor-2"
]



# ============================================================
# EMPLOYEE CONFIGURATION
# ============================================================

EMPLOYEE_ROLES = [
    "Technician",
    "Operator",
    "Supervisor",
    "Inspector",
    "Manager"
]

ROLE_WEIGHTS = {
    "Technician": 0.40,
    "Operator": 0.35,
    "Supervisor": 0.10,
    "Inspector": 0.10,
    "Manager": 0.05
}

ROLE_DEPARTMENTS = {
    "Technician": "Maintenance",
    "Operator": "Production",
    "Supervisor": "Operations",
    "Inspector": "Quality",
    "Manager": "Operations"
}

EMPLOYEE_STATUSES = [
    "Active",
    "Inactive"
]

EMPLOYEE_STATUS_WEIGHTS = {
    "Active": 0.90,
    "Inactive": 0.10
}

DEPARTMENTS = [
    "Production",
    "Maintenance",
    "Quality",
    "Warehouse",
    "Operations"
]

SUPPLIER_STATUSES = [
    "Active",
    "Inactive"
]

SUPPLIER_STATUS_WEIGHTS = {
    "Active": 0.90,
    "Inactive": 0.10
}

INVENTORY_STATUSES = [
    "Active",
    "Discontinued"
]

INVENTORY_STATUS_WEIGHTS = {
    "Active": 0.95,
    "Discontinued": 0.05
}

CATEGORIES = [
    "Raw Material",
    "Component",
    "Finished Good"
]

WAREHOUSES = [
    "WH-A",
    "WH-B",
    "WH-C",
    "WH-D"
]

UNITS = [
    "Pieces",
    "Kg",
    "Litres",
    "Metres",
    "Units"
]

COUNTRIES = [
    "India",
    "China",
    "Germany",
    "USA",
    "Japan",
    "UK",
    "France"
]

# ============================================================
# TRANSACTIONAL ENUM VALUES
# ============================================================

PRIORITIES = [
    "Low",
    "Medium",
    "High",
    "Critical"
]

ISSUE_TYPES = [
    "Mechanical",
    "Electrical",
    "Hydraulic",
    "Pneumatic",
    "Electronic",
    "Software",
    "Calibration",
    "Thermal",
    "Lubrication",
    "Safety",
    "Structural",
    "Network"
]

DOWNTIME_REASONS = [
    "Mechanical Failure",
    "Electrical Issue",
    "Operator Error",
    "Material Shortage",
    "Power Outage",
    "Network Failure",
    "Calibration Error",
    "Scheduled Maintenance"
]

SEVERITIES = [
    "Low",
    "Medium",
    "High"
]

SHIFT_TYPES = [
    "Day",
    "Evening",
    "Night"
]

SHIFT_CONFIG = {

    "Day": {
        "start_hour": 6,
        "duration_hours": 8
    },

    "Evening": {
        "start_hour": 14,
        "duration_hours": 8
    },

    "Night": {
        "start_hour": 22,
        "duration_hours": 8
    }

}

DEFECT_TYPES = [

    "Dimensional Deviation",
    "Surface Scratch",
    "Material Crack",
    "Structural Warp"

]

# ============================================================
# DOWNTIME CONFIGURATION
# ============================================================

DOWNTIME_SEVERITY_WEIGHTS = {

    "Low": 0.50,
    "Medium": 0.35,
    "High": 0.15

}

DOWNTIME_REASON_SEVERITY_MAP = {

    "Low": [
        "Calibration Error",
        "Operator Error",
        "Scheduled Maintenance"
    ],

    "Medium": [
        "Electrical Issue",
        "Network Failure",
        "Material Shortage"
    ],

    "High": [
        "Mechanical Failure",
        "Power Outage"
    ]

}


# ============================================================
# SHIFT LOG CONFIGURATION
# ============================================================

SHIFT_NOTES = [
    "Routine shift completed.",
    "Overtime required for production target.",
    "Temporary machine stoppage handled.",
    "Additional quality inspection performed.",
    "Maintenance support provided during shift.",
    "Operator replacement arranged."
]

# ============================================================
# PURCHASE ORDER CONFIGURATION
# ============================================================

PO_QUANTITY_RANGE = (
    50,
    1000
)


# ============================================================
# STATUS DISTRIBUTIONS
# ============================================================

WO_STATUS_WEIGHTS = {

    WO_OPEN: 0.10,
    WO_IN_PROGRESS: 0.15,
    WO_COMPLETED: 0.70,
    WO_CANCELLED: 0.05

}

ML_STATUS_WEIGHTS = {

    ML_OPEN: 0.10,
    ML_IN_PROGRESS: 0.20,
    ML_RESOLVED: 0.70

}

PO_STATUS_WEIGHTS = {

    PO_ORDERED: 0.15,
    PO_DELIVERED: 0.75,
    PO_CANCELLED: 0.10

}

# ============================================================
# SUPPLIER CONFIGURATION
# ============================================================

GOOD_SUPPLIER_SCORE_RANGE = (
    65.00,
    99.00
)

WORST_SUPPLIER_SCORE_RANGE = (
    20.00,
    44.99
)

WORST_SUPPLIER_CODE = "SUP-00001"

# ============================================================
# TOP TECHNICIAN CONFIGURATION
# ============================================================

TOP_TECHNICIAN_CODE = "EMP-00001"

TOP_TECHNICIAN_MULTIPLIER = 3.0

TOP_TECHNICIAN_PROBABILITY = 0.05

# ============================================================
# DEMO GUARANTEES
# ============================================================

QUALITY_FAIL_RATE = 0.20

INVENTORY_BELOW_REORDER_RATE = 0.30

DOWNTIME_ACTIVE_RATE = 0.05

LATE_SUPPLIER_RATE = 0.55

HIGH_DOWNTIME_MACHINE_RATE = 0.15

# ============================================================
# QUALITY CHECK CONFIGURATION
# ============================================================

QC_INSPECTION_WEIGHTS = {

    1: 0.60,
    2: 0.30,
    3: 0.10

}

# ============================================================
# QUALITY CHECK DEMO GUARANTEE
# ============================================================

RECENT_DEFECT_RATE = 0.05

# ============================================================
# EXPECTED QUALITY CHECK ROWS
# ============================================================

EXPECTED_QC_MULTIPLIER = 1.5

# Expected quality_checks rows:
# ROW_COUNTS['work_orders'] * EXPECTED_QC_MULTIPLIER
# 100,000 * 1.5 = ~150,000 rows