# MCP Server for accessing Zammad Data and possibly answer them in the future
from mcp.server.fastmcp import FastMCP
from zammad.zammad_client import ZammadClient
from datetime import datetime, timedelta, timezone
import os

mcp = FastMCP("Zammad")

def require_env(name):
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

client = ZammadClient(
    base_url=require_env("ZAMMAD_URL"),
    token=require_env("ZAMMAD_TOKEN"),
)

@mcp.tool()
def who_am_i():
    """Return the Zammad user used by this MCP server."""
    return client.get_current_user()

@mcp.tool()
def list_groups():
    return client.list_groups()

@mcp.tool()
def list_organizations():
    return client.list_organizations()

@mcp.tool()
def sample_ticket():
    """
    Returns one ticket object for inspecting Zammad structure.
    """
    tickets = client.list_tickets(page=1, per_page=1)

    if not tickets:
        return {"message": "No tickets found"}

    return client.get_ticket(tickets[0]["id"])

@mcp.tool()
def sample_recent_ticket():
    """
    Returns one recent ticket object for inspecting Zammad structure.
    """
    tickets = client.search_tickets(
        "created_at:>now-1d"
    )

    if not tickets:
        return {"message": "No recent tickets found"}

    return client.get_ticket(tickets[0]["id"])

@mcp.tool()
def list_tickets(page: int = 1, per_page: int = 25):
    """
    List tickets from Zammad.

    Args:
        page: Page number for pagination. Starts at 1.
        per_page: Number of tickets to return. Maximum value is 200. Default is 25.

    Returns:
        A list of tickets including ticket ID, title, state, priority,
        customer, group, owner, and timestamps.
    """
    return client.list_tickets(page, per_page)

@mcp.tool()
def list_recent_tickets(days: int = 7, per_page=25):
    """
    List tickets from the last n days from Zammad.

    Args:
        days: Number of days. Default 7, for last week.
        per_page: Optional parameter. Decides amount of tickets queried at once. Maximum value is 200. Default is 25.

    Returns:
        A list of tickets including ticket ID, title, state, priority,
        customer, group, owner, and timestamps.
    """
    return client.tickets_past_days(days, per_page)

@mcp.tool()
def summary():
    """
    Returns ticket statistics for tickets in our Zammad ticket system. IT-Helpdesk.

    Field meanings:
    - summary: 
        Total tickets in all categories.
    - categories:
        Tickets per category.
    - last_7_days: 
        Tickets created in the last week and their current status.
    - last_30_days:
        Tickets created in the last month and their current status.
    - opened:
        Number of newly opened tickets in the timespan.
    - closed:
        Number of the tickets that were opened in the timespan, that have been worked on and have been closed.
    - still_open:
        Number of tickets that remain open, meaning they couldn't be closed, since they aren't finished yet.
    """
    return client.summary()

# Debug functions, to be used via litellm
@mcp.tool()
def summary_last_week():
    """
    Returns ticket statistics for the previous 7 days.

    Field meanings:
    opened:
        Number of newly opened tickets.
    closed:
        Number of closed tickets.
    still_open:
        Number of tickets that remain open.
    """
    return client.summary_last_week()

@mcp.tool()
def summary_last_month():
    """
    Returns ticket statistics for the previous month.

    Field meanings:
    opened:
        Number of newly opened tickets.
    closed:
        Number of closed tickets.
    still_open:
        Number of tickets that remain open.
    """
    return client.summary_last_month()

@mcp.tool()
def summary_year(year: int):
    """
    Returns ticket statistics for the specified year.

    Args:
        year: Year whose statistics should be returned.

    Field meanings:
    opened:
        Number of newly opened tickets.
    closed:
        Number of closed tickets.
    still_open:
        Number of tickets that remain open.
    """
    return client.summary_year(year)

@mcp.tool()
def summary_month(year: int, month: int):
    """
    Returns ticket statistics for the specified month in a specified year.

    Args:
        year: Year whose statistics should be returned.
        month: Month in that year.

    Field meanings:
    opened:
        Number of newly opened tickets.
    closed:
        Number of closed tickets.
    still_open:
        Number of tickets that remain open.
    """
    return client.summary_month(year, month)

@mcp.tool()
def summary_open():
    """
    Returns ticket statistics for all open tickets.

    Field meanings:
    opened:
        Number of newly opened tickets.
    closed:
        Number of closed tickets.
    still_open:
        Number of tickets that remain open.
    """
    return client.summary_open()

@mcp.tool()
def test():
    return client.test()

@mcp.tool()
def tags_past_week():
    """
    Returns the tag statistics for the most comman tags for tickets created in the last week.
    """
    return client.tag_statistics(client.tickets_past_days(7))

@mcp.tool()
def tags_past_month():
    """
    Returns the tag statistics for the most comman tags for tickets created in the last month.
    """
    return client.tag_statistics(client.tickets_past_days(30))

@mcp.tool()
def tags_past_year():
    """
    Returns the tag statistics for the most comman tags for tickets created in the last year.
    """
    return client.tag_statistics(client.tickets_past_days(365))


if __name__ == "__main__":
    mcp.run()