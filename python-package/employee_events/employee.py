from .query_base import QueryBase
from .sql_execution import query


class Employee(QueryBase):
    """Queries that produce employee-level datasets."""

    name = "employee"

    @query
    def names(self):
        """
        Return all employee names and IDs.
        """
        return """
            SELECT
                first_name || ' ' || last_name AS employee_name,
                employee_id
            FROM employee
            ORDER BY first_name, last_name
        """

    @query
    def username(self, id):
        """
        Return the full name of one employee.
        """
        return f"""
            SELECT
                first_name || ' ' || last_name AS employee_name
            FROM employee
            WHERE employee_id = {id}
        """

    def model_data(self, id):
        """
        Return the employee-level data needed by the ML model.
        """
        sql_query = f"""
                    SELECT SUM(positive_events) positive_events
                         , SUM(negative_events) negative_events
                    FROM {self.name}
                    JOIN employee_events
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = {id}
                """

        return self.pandas_query(sql_query)