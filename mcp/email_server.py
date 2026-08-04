from mcp.server.fastmcp import FastMCP
from email_client import EmailClient
import os
import markdown
from datetime import date

from zammad.zammad_client import ZammadClient

mcp = FastMCP("Email")

def require_env(name):
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

email_client = EmailClient(
    smtp_host=require_env("SMTP_HOST"),
    smtp_port=require_env("SMTP_PORT"),
    smtp_user=require_env("SMTP_USER"),
    smtp_password=require_env("SMTP_PASSWORD")
)

zammad_client = ZammadClient(
    base_url=require_env("ZAMMAD_URL"),
    token=require_env("ZAMMAD_TOKEN"),
)

@mcp.tool()
def send_email(recipient: str, subject: str, body: str):
    """
    Send an email.

    Args:
        recipient: Recipient email address.
        subject: Email subject.
        body: Email content.
    """
    return email_client.send_email(recipient, subject, body)

@mcp.tool()
def send_weekly_report_email(summary_markdown: str):
    """
    Sends the completed weekly support report.

    Args:
        summary_text:
            A short factual German summary of the support statistics.
    """
    REPORT_RECIPIENTS = [
        "xxx@xxx.de",
    ]
    html = zammad_client.summary_html()
    summary_html = markdown.markdown(summary_markdown)

    body = zammad_client.renderer.render_document(html, summary_html)

    results = []

    subject = f"Supportbericht {date.today():%d.%m.%Y}"

    for recipient in REPORT_RECIPIENTS:
        try:
            results.append(email_client.send_email(recipient, subject, body))
        except Exception:
            results.append("An error has occured when trying to send an e-mail to: ", recipient)

    return {
        "status": "e-mails succesfully sent",
        "recipients": results
    }

if __name__ == "__main__":
    mcp.run()
