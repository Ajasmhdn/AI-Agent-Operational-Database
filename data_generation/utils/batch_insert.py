"""
batch_insert.py

Batch insert utility for synthetic data generation.
"""

from utils.logger import logger


def batch_insert(
    connection,
    sql: str,
    data: list,
    table_name: str
):
    """
    Insert a batch of records into a table.

    Parameters
    ----------
    connection : mysql connection
    sql : str
        Insert statement.
    data : list
        Batch rows.
    table_name : str
        Table name for logging.
    """

    if not data:
        return

    cursor = connection.cursor()

    try:

        cursor.executemany(
            sql,
            data
        )

        connection.commit()

    except Exception as error:

        connection.rollback()

        logger.exception(
            f"{table_name} batch insert failed: {error}"
        )

        raise

    finally:

        cursor.close()