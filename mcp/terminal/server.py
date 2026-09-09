from mcp.server.fastmcp import FastMCP
from setup.services.litellm.mcp.terminal.client import TerminalClient
import os


mcp = FastMCP("Terminal")


def require_env(name):
    value = os.getenv(name)

    if value is None:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


client = TerminalClient(
    require_env("TERMINAL_WORKING_DIRECTORY")
)


@mcp.tool()
def execute(command: str):
    """
    Executes a terminal command.

    Args:
        command: Shell command to execute.
    """
    return client.execute(command)


if __name__ == "__main__":
    mcp.run()