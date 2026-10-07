from .sql_execution import QueryMixin


class QueryBase(QueryMixin):
    """Base query class containing behavior shared by employees and teams."""

    name = ""

    def names(self):
        """
        Return entity names and IDs.

        Subclasses override this method.
        """
        return []

    def event_counts(self, id):
        """
        Return positive and negative event totals grouped by date.
        """
        sql_query = f"""
            SELECT
                event_date,
                SUM(positive_events) AS positive_events,
                SUM(negative_events) AS negative_events
            FROM {self.name}
            JOIN employee_events
                USING ({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
            GROUP BY event_date
            ORDER BY event_date
        """

        return self.pandas_query(sql_query)

    def notes(self, id):
        """
        Return dated notes for an employee or team.
        """
        sql_query = f"""
            SELECT
                note_date,
                note
            FROM {self.name}
            JOIN notes
                USING ({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
            ORDER BY note_date
        """

        return self.pandas_query(sql_query)