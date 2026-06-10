import time
from threading import Event

from scheduler.file_watcher import FileWatcher
from scheduler.task_scheduler import TaskScheduler


class AutomationApp:
    def __init__(self, tasks, logger):
        self.tasks = tasks
        self.logger = logger
        self.stop_event = Event()
        self.scheduler = TaskScheduler(tasks, self.stop_event, logger)
        self.file_watcher = FileWatcher(tasks, logger)

    def start(self):
        self.logger.info("Starting automation tool.")
        self.scheduler.start()
        self.file_watcher.start()

        try:
            self.logger.info("Press Ctrl+C to stop.")
            while not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Ctrl+C received. Shutting down.")
        finally:
            self.stop()

    def stop(self):
        self.stop_event.set()
        self.file_watcher.stop()
        self.scheduler.stop()
        self.logger.info("Automation tool stopped.")
