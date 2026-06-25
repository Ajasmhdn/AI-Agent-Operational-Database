"""
main.py

Sprint 2 synthetic data generation pipeline.
"""

import random
from faker import Faker

from config import RANDOM_SEED

from utils.db_connect import get_connection
from utils.logger import logger

from generators.machines_generator import (
    generate_machines
)

from generators.employees_generator import (
    generate_employees
)

from generators.suppliers_generator import (
    generate_suppliers
)

from generators.inventory_generator import (
    generate_inventory
)

from generators.work_orders_generator import (
    generate_work_orders
)

from generators.maintenance_logs_generator import (
    generate_maintenance_logs
)

from generators.downtime_events_generator import (
    generate_downtime_events
)

from generators.purchase_orders_generator import (
    generate_purchase_orders
)

from generators.shift_logs_generator import (
    generate_shift_logs
)

from generators.quality_checks_generator import (
    generate_quality_checks
)

from validate import validate_all


# ============================================================
# MAIN
# ============================================================

def main():
    """
    Execute complete Sprint 2 generation pipeline.
    """

    logger.info(
        "main | Pipeline started"
    )

    # ========================================================
    # RESET RANDOM SEEDS FOR REPRODUCIBILITY
    # ========================================================

    random.seed(
        RANDOM_SEED
    )

    Faker.seed(
        RANDOM_SEED
    )

    logger.info(
        f"main | Random seed reset to "
        f"{RANDOM_SEED}"
    )

    connection = get_connection()

    try:

        # ====================================================
        # MASTER TABLES
        # ====================================================

        logger.info(
            "main | Generating master tables"
        )

        generate_machines(connection)

        generate_employees(connection)

        generate_suppliers(connection)

        generate_inventory(connection)

        logger.info(
            "main | Master tables completed"
        )

        # ====================================================
        # TRANSACTION TABLES
        # ====================================================

        logger.info(
            "main | Generating transactional tables"
        )

        generate_work_orders(connection)

        generate_maintenance_logs(connection)

        generate_downtime_events(connection)

        generate_purchase_orders(connection)

        generate_shift_logs(connection)

        generate_quality_checks(connection)

        logger.info(
            "main | Transactional tables completed"
        )

        # ====================================================
        # VALIDATION
        # ====================================================

        logger.info(
            "main | Starting validation"
        )

        validate_all(connection)

        logger.info(
            "main | Validation completed"
        )

        logger.info(
            "main | Pipeline completed successfully"
        )

    except Exception as e:

        logger.exception(
            f"main | Pipeline failed: {e}"
        )

        raise

    finally:

        connection.close()

        logger.info(
            "main | Database connection closed"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()