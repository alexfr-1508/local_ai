from mcp.server.fastmcp import FastMCP
from mcp.microsoft_sql.client import MicrosoftSQLClient
import os

mcp = FastMCP("MicrosoftSQL")

def require_env(name):
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

client = MicrosoftSQLClient(require_env("SQL_CONNECTION_STRING"))

@mcp.tool()
def get_users():
    """
    Returns all data from the 'users' table.
    """
    return client.get_users()

@mcp.tool()
def get_user(user_id: int):
    """
    Retrieves data for a specific user.

    Args:
        user_id: specific user identification number.
    """
    return client.get_user(user_id)

@mcp.tool()
def execute(query: str, params=None):
    """
    Executes a custom query on the db.
    
    Args:
        query: db query to be executed
        params: query parameters
    """
    return client.execute(query, params)

if __name__ == "__main__":
    mcp.run()