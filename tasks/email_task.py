from tasks.base_task import BaseTask
from utils.emailer import send_email


class EmailTask(BaseTask):
    def execute(self):
        subject = self.config.get("subject", "Python Automation Tool")
        body = self.config.get("body", "This is a test email from the automation tool.")
        send_email(subject, body)
