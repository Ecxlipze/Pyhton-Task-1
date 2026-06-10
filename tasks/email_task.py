import os
import smtplib
from email.mime.text import MIMEText

from tasks.base_task import BaseTask


class EmailTask(BaseTask):
    def execute(self):
        subject = self.config.get("subject", "Python Automation Tool")
        body = self.config.get("body", "This is a test email from the automation tool.")

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
            self.logger.info("Email dry run. No SMTP settings found.")
            self.logger.info("To: %s", recipient)
            self.logger.info("Subject: %s", subject)
            self.logger.info("Body: %s", body)
            return

        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(message)

        self.logger.info("Email sent to %s", recipient)
