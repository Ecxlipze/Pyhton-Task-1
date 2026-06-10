import logging
import os
import smtplib
from email.mime.text import MIMEText


def send_email(subject, body):
    sender = os.getenv("SMTP_FROM")
    recipient = os.getenv("SMTP_TO")
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")

    if not sender:
        sender = "dry-run@example.com"
    if not recipient:
        recipient = "student@example.com"

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient

    if not host or not username or not password:
        logging.info("Email notification dry run. No SMTP settings found.")
        logging.info("To: %s", recipient)
        logging.info("Subject: %s", subject)
        logging.info("Body: %s", body)
        return

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)

    logging.info("Email notification sent to %s", recipient)
