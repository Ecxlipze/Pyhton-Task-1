from abc import ABC, abstractmethod
import logging


class BaseTask(ABC):
    task_type = "base"

    def __init__(self, config):
        self.config = config
        self.task_name = config["task_name"]
        self.file_path = config["file_path"]
        self.retry_count = config.get("retry_count", 0)
        self.logger = logging.getLogger("automation_tool")

    def run(self):
        for attempt in range(self.retry_count + 1):
            try:
                self.logger.info("Running task: %s", self.task_name)
                self.execute()
                self.logger.info("Finished task: %s", self.task_name)
                return
            except Exception:
                self.logger.exception(
                    "Task failed: %s (attempt %s of %s)",
                    self.task_name,
                    attempt + 1,
                    self.retry_count + 1,
                )

    @abstractmethod
    def execute(self):
        """Run the task."""
