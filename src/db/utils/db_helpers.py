"""
db_helpers.py

Utility functions for database operations, including:
- printing all rows from a specified table for debugging purposes.
"""
from psycopg2 import sql

from src.db.connection import db_connection



def get_tbl_contents_as_str(table_name: str) -> str:
    """
    Connects to the database, retrieves all rows from the specified table,
    and returns a formatted string.

    Args:
        table_name (str): name of the table to print.

    Returns:
        str: formatted string containing all table rows.
    """
    conn = db_connection()
    cur = conn.cursor()

    q = sql.SQL("SELECT * FROM {}").format(
        sql.Identifier(table_name),
    )
    cur.execute(q)
    rows = cur.fetchall()

    result_string = f"Table: {table_name}\n"
    for row in rows:
        result_string += f"{row}\n"

    cur.close()
    conn.close()

    return result_string

def get_tbl_contents_as_str_sorted_by(table_name: str, sort_by: str) -> str:
    """
    Connects to the database, retrieves all rows from the specified table,
    and returns a formatted string.

    Args:
        table_name (str): name of the table to print.

    Returns:
        str: formatted string containing all table rows.
    """
    conn = db_connection()
    cur = conn.cursor()

    q = sql.SQL("SELECT * FROM {} ORDER BY {}").format(
        sql.Identifier(table_name),
        sql.Identifier(sort_by),
    )
    cur.execute(q)
    rows = cur.fetchall()

    result_string = f"Table: {table_name}\n"
    for row in rows:
        result_string += f"{row}\n"

    cur.close()
    conn.close()

    return result_string