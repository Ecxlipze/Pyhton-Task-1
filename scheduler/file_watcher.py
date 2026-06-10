import logging
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from scheduler.task_scheduler import run_task


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, tasks):
        self.tasks = tasks

    def on_modified(self, event):
        if event.is_directory:
            return

        changed_file = Path(event.src_path)

        for task in self.tasks:
            task_path = Path(task.file_path).resolve()
            task_folder = task_path if task_path.is_dir() else task_path.parent

            if changed_file.parent == task_folder:
                logging.info("File changed: %s", changed_file)
                run_task(task)


def start_file_watcher(tasks):
    observer = Observer()
    handler = ChangeHandler(tasks)
    watched_folders = []

    for task in tasks:
        task_path = Path(task.file_path).resolve()
        folder = task_path if task_path.is_dir() else task_path.parent

        if folder.exists() and folder not in watched_folders:
            observer.schedule(handler, str(folder), recursive=False)
            watched_folders.append(folder)
            logging.info("Watching folder: %s", folder)

    observer.start()
    return observer
