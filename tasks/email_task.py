import os
import smtplib
from email.mime.text import MIMEText

from tasks.base_task import BaseTask


class EmailTask(BaseTask):
    task_type = "email"

    def execute(self):
        subject = self.config.get("subject", "Python Automation Tool")
        body = self.config.get("body", "This is a test email from the automation tool.")

        sender = os.getenv("SMTP_FROM")
        recipient = os.getenv("SMTP_TO")
        host = os.getenv("SMTP_HOST")
        port = int(os.getenv("SMTP_PORT", "587"))
        username = os.getenv("SMTP_USER")
        password = os.getenv("SMTP_PASSWORD")

        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = sender or "dry-run@example.com"
        message["To"] = recipient or "student@example.com"

        missing_credentials = not all([sender, recipient, host, username, password])
        if missing_credentials:
            self.logger.info("Email dry-run mode. SMTP credentials are not configured.")
            self.logger.info("Prepared email subject: %s", subject)
            self.logger.info("Prepared email body: %s", body)
            return

        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(message)

        self.logger.info("Email sent to %s", recipient)
