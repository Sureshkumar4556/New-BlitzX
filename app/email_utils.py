"""
Lightweight email sending helper.

By default this just logs the email (so the app works out-of-the-box with
zero config). To send real emails, set SMTP_* environment variables and the
functions below will use smtplib automatically.
"""

import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger("blitzx.email")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", "hello@blitzx.com")


def _send_email(to_email: str, subject: str, body: str) -> None:
    if not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD):
        logger.info("[EMAIL:SKIPPED-NO-SMTP-CONFIG] to=%s subject=%s\n%s", to_email, subject, body)
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception:
        logger.exception("Failed to send email to %s", to_email)


def send_order_confirmation_email(to_email: str, name: str, order_id: str, service: str) -> None:
    subject = "We've received your project order — BlitzXCreatives"
    body = (
        f"Hi {name},\n\n"
        f"Thanks for submitting your project request for {service}.\n"
        f"Your order ID is: {order_id}\n\n"
        "Our team will review it and reach out within 24 hours.\n\n"
        "— BlitzXCreatives"
    )
    _send_email(to_email, subject, body)


def send_lead_notification_email(name: str, email: str, service: str, message: str) -> None:
    # Internal notification to the business inbox about a new contact lead.
    subject = f"New contact lead: {name} ({service})"
    body = f"Name: {name}\nEmail: {email}\nService: {service}\n\nMessage:\n{message}"
    _send_email(FROM_EMAIL, subject, body)
