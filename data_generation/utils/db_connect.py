"""
db_connect.py

Database connection utility.
"""

import pymysql

from config import DB_CONFIG
from utils.logger import logger


def get_connection():
    """
    Create and return a MySQL database connection.
    """

    try:
        connection = pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )

        logger.info(
            "Database connection established."
        )

        return connection

    except Exception as error:

        logger.exception(
            f"Database connection failed: {error}"
        )

        raise