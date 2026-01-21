import smtplib
from email.mime.text import MIMEText
import os

def send_email(recipient: str, subject: str, body: str) -> str:
    """
    Sends a real email using SMTP configuration from environment variables.
    """
    # Default to Gmail, but allow override
    smtp_server = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("EMAIL_PORT", "587"))
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        return "Error: EMAIL_USER and EMAIL_PASSWORD not found in environment. Please set them in .env"

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
        return f"Successfully sent email to {recipient}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"
