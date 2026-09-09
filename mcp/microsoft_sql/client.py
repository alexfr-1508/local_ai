from mssql_python import connect

# will be kept read only for now, can be expanded later
class MicrosoftSQLClient:
    def __init__(self, conn_str: str):
        self.conn = connect(conn_str)

    def _sql_query(self, query: str, params=None):
        cursor = self.conn.cursor()

        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)

        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        return [
            dict(zip(columns, row))
            for row in rows
        ]
    
    # example query, still working on actual use cases
    def get_users(self):
        return self._sql_query("SELECT * FROM users;")

    def get_user(self, user_id):
        return self._sql_query("SELECT * FROM users WHERE id = ?;", (user_id,))

    def execute(self, query: str, params=None):
        cursor = self.conn.cursor()
    
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
    
        self.conn.commit()
        