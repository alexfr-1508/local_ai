from mcp.server.fastmcp import FastMCP
from client import CustomClient
import os


mcp = FastMCP("Terminal")


def require_env(name):
    value = os.getenv(name)

    if value is None:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


client = CustomClient()


@mcp.tool()
def placeholder():
    """
    <tool_description>

    Args:
        <args>
    """
    return client.placeholder()


if __name__ == "__main__":
    mcp.run()