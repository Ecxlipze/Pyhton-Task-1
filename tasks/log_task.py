from tasks.base_task import BaseTask
class LogTask(BaseTask):
    def execute(self):
        message = self.config.get("message", "Hello")
        self.logger.info(message)
