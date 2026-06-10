import argparse
import json
import logging
import sys
import time
from pathlib import Path
from threading import Event, Thread

import schedule
import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from tasks.email_task import EmailTask
from tasks.file_processing_task import FileProcessingTask
from tasks.log_task import LogTask


TASK_CLASSES = {
    "log": LogTask,
    "file": FileProcessingTask,
    "email": EmailTask,
}


def setup_logger():
    Path("logs").mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler(),
        ],
    )

    return logging.getLogger("automation_tool")


def load_config(file_path):
    path = Path(file_path)

    if not path.exists():
        raise ValueError("Config file not found")

    text = path.read_text()

    if path.suffix == ".json":
        return json.loads(text)

    if path.suffix in [".yaml", ".yml"]:
        return yaml.safe_load(text)

    raise ValueError("Use a .json, .yaml, or .yml config file")


def check_config(config):
    if "tasks" not in config:
        raise ValueError("Config needs a tasks list")

    for task in config["tasks"]:
        for key in ["task_name", "task_type", "schedule", "file_path"]:
            if key not in task:
                raise ValueError(f"Task is missing: {key}")

        if task["task_type"] not in TASK_CLASSES:
            raise ValueError(f"Unknown task type: {task['task_type']}")


def make_tasks(config):
    tasks = []

    for task_config in config["tasks"]:
        task_class = TASK_CLASSES[task_config["task_type"]]
        task = task_class(task_config)
        tasks.append(task)

    return tasks


def run_task(task, logger):
    try:
        logger.info("Running: %s", task.task_name)
        task.execute()
        logger.info("Done: %s", task.task_name)
    except Exception as error:
        logger.error("Task failed: %s", error)


def add_to_schedule(task, logger):
    task_schedule = task.config["schedule"]

    if task_schedule["type"] == "interval":
        minutes = task_schedule.get("minutes", 1)
        schedule.every(minutes).minutes.do(run_task, task, logger)
        logger.info("Scheduled %s every %s minute(s)", task.task_name, minutes)

    if task_schedule["type"] == "daily":
        run_time = task_schedule.get("time", "09:00")
        schedule.every().day.at(run_time).do(run_task, task, logger)
        logger.info("Scheduled %s every day at %s", task.task_name, run_time)


def scheduler_loop(stop_event):
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(1)


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, tasks, logger):
        self.tasks = tasks
        self.logger = logger
        self.last_file = ""
        self.last_time = 0

    def on_modified(self, event):
        self.handle_change(event)

    def on_created(self, event):
        self.handle_change(event)

    def handle_change(self, event):
        if event.is_directory:
            return

        changed_file = Path(event.src_path)
        now = time.time()

        if str(changed_file) == self.last_file and now - self.last_time < 1:
            return

        self.last_file = str(changed_file)
        self.last_time = now

        for task in self.tasks:
            task_path = Path(task.file_path).resolve()
            task_folder = task_path if task_path.is_dir() else task_path.parent

            if changed_file.parent == task_folder:
                self.logger.info("File changed: %s", changed_file)
                run_task(task, self.logger)


def start_app(config_file):
    logger = setup_logger()
    config = load_config(config_file)
    check_config(config)
    tasks = make_tasks(config)

    for task in tasks:
        add_to_schedule(task, logger)

    stop_event = Event()
    scheduler_thread = Thread(target=scheduler_loop, args=(stop_event,))
    scheduler_thread.start()

    observer = Observer()
    handler = ChangeHandler(tasks, logger)
    watched_folders = []

    for task in tasks:
        task_path = Path(task.file_path).resolve()
        folder = task_path if task_path.is_dir() else task_path.parent

        if folder.exists() and folder not in watched_folders:
            observer.schedule(handler, str(folder), recursive=False)
            watched_folders.append(folder)
            logger.info("Watching folder: %s", folder)

    observer.start()
    logger.info("App started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping app...")
        stop_event.set()
        observer.stop()
        observer.join()
        scheduler_thread.join()
        logger.info("App stopped.")


def list_tasks(config_file):
    config = load_config(config_file)
    check_config(config)

    print("Tasks:")
    for task in config["tasks"]:
        print(f"- {task['task_name']} ({task['task_type']})")


def main():
    parser = argparse.ArgumentParser(description="Simple Python automation tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("--config", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--config", required=True)

    subparsers.add_parser("stop")

    args = parser.parse_args()

    try:
        if args.command == "start":
            start_app(args.config)
        elif args.command == "list":
            list_tasks(args.config)
        elif args.command == "stop":
            print("Use Ctrl+C to stop the running app.")
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
