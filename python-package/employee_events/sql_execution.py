from sqlite3 import connect
from pathlib import Path
from functools import wraps

import pandas as pd


# Absolute path to employee_events.db
db_path = Path(__file__).resolve().parent / "employee_events.db"


class QueryMixin:
    """Provide reusable methods for executing SQLite queries."""

    def pandas_query(self, sql_query):
        """
        Execute an SQL query and return the result as a pandas DataFrame.
        """
        with connect(db_path) as connection:
            return pd.read_sql_query(sql_query, connection)

    def query(self, sql_query):
        """
        Execute an SQL query and return the result as a list of tuples.
        """
        with connect(db_path) as connection:
            cursor = connection.cursor()
            result = cursor.execute(sql_query).fetchall()

        return result


# Leave this code unchanged
def query(func):
    """
    Decorator that runs a standard SQL execution
    and returns a list of tuples.
    """

    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result

    return run_query