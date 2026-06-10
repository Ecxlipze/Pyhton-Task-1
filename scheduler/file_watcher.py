from pathlib import Path
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class TaskEventHandler(FileSystemEventHandler):
    def __init__(self, task, logger):
        self.task = task
        self.logger = logger
        self.last_event_time = {}

    def on_modified(self, event):
        self._handle_event(event)

    def on_created(self, event):
        self._handle_event(event)

    def _handle_event(self, event):
        if event.is_directory:
            return

        watched_path = Path(self.task.file_path)
        event_path = Path(event.src_path)

        if watched_path.is_file() and event_path != watched_path:
            return

        # Some systems report both "created" and "modified" for one save.
        event_key = str(event_path)
        now = time.time()
        if now - self.last_event_time.get(event_key, 0) < 1:
            return
        self.last_event_time[event_key] = now

        self.logger.info("File change detected for task '%s': %s", self.task.task_name, event_path)
        self.task.run()


class FileWatcher:
    def __init__(self, tasks, logger):
        self.tasks = tasks
        self.logger = logger
        self.observer = Observer()

    def start(self):
        watched_count = 0

        for task in self.tasks:
            path = Path(task.file_path)
            watch_path = path if path.is_dir() else path.parent
            if not watch_path.exists():
                self.logger.warning("Watch path does not exist: %s", watch_path)
                continue

            handler = TaskEventHandler(task, self.logger)
            key = str(watch_path.resolve())
            self.observer.schedule(handler, key, recursive=False)
            watched_count += 1
            self.logger.info("Watching path: %s", key)

        if watched_count:
            self.observer.start()
        else:
            self.logger.warning("No valid paths found for file monitoring.")

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join(timeout=3)
