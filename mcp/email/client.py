import smtplib
from email.message import EmailMessage


class EmailClient:
    def __init__(self, smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str):
        self.smtp_host = smtp_host
        self.smtp_port = int(smtp_port)
        self.smtp_user = smtp_user
        self.smtp_password= smtp_password

    def send_email(self, recipient: str, subject: str, body: str):
        if not recipient.strip():
            raise ValueError("Email recipient cannot be empty")

        if not subject.strip():
            raise ValueError("Email subject cannot be empty")

        if not body.strip():
            raise ValueError("Email body cannot be empty")
        
        message = EmailMessage()

        message["From"] = self.smtp_user
        message["To"] = recipient
        message["Subject"] = subject

        message.set_content("Ihr E-Mail-Client unterstützt keine HTML-E-Mails.")

        message.add_alternative(body, subtype="html")

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.send_message(message)

        return {
            "status": "sent",
            "recipient": recipient,
            "subject": subject,
        }
