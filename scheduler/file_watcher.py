from pathlib import Path
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from scheduler.task_scheduler import safe_run


class SimpleFileHandler(FileSystemEventHandler):
    def __init__(self, tasks, logger):
        self.tasks = tasks
        self.logger = logger
        self.last_file = ""
        self.last_time = 0

    def on_modified(self, event):
        self.run_matching_tasks(event)

    def on_created(self, event):
        self.run_matching_tasks(event)

    def run_matching_tasks(self, event):
        if event.is_directory:
            return

        event_path = Path(event.src_path)
        now = time.time()

        if str(event_path) == self.last_file and now - self.last_time < 1:
            return

        self.last_file = str(event_path)
        self.last_time = now

        for task in self.tasks:
            path = Path(task.file_path).resolve()
            task_folder = path if path.is_dir() else path.parent

            if event_path.parent == task_folder:
                self.logger.info("File changed: %s", event_path)
                safe_run(task, self.logger)


def start_file_watcher(tasks, logger):
    observer = Observer()
    handler = SimpleFileHandler(tasks, logger)
    watched_folders = []

    for task in tasks:
        path = Path(task.file_path).resolve()
        folder = path if path.is_dir() else path.parent

        if folder.exists() and folder not in watched_folders:
            observer.schedule(handler, str(folder), recursive=False)
            watched_folders.append(folder)
            logger.info("Watching folder: %s", folder)

    observer.start()
    return observer
