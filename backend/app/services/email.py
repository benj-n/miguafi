import smtplib
from email.message import EmailMessage

from ..core.config import settings


def send_email(to_email: str, subject: str, body: str) -> None:
    host = getattr(settings, "smtp_host", None) or "localhost"
    port = int(getattr(settings, "smtp_port", 1025))
    msg = EmailMessage()
    msg["From"] = "noreply@miguafi.local"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(host, port, timeout=3) as s:
            s.send_message(msg)
    except Exception:
        # In tests or local dev without SMTP, silently ignore.
        return
