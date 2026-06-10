from tasks.base_task import BaseTask


class LogTask(BaseTask):
    task_type = "log"

    def execute(self):
        message = self.config.get("message", "Hello from LogTask!")
        self.logger.info("LogTask message: %s", message)
