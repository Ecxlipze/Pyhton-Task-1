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

        if task["task_type"] not in ["log", "file", "email"]:
            raise ValueError(f"Unknown task type: {task['task_type']}")

        if task["schedule"]["type"] not in ["interval", "daily"]:
            raise ValueError("Schedule type must be interval or daily")


def make_tasks(config):
    tasks = []

    for task_config in config["tasks"]:
        if task_config["task_type"] == "log":
            tasks.append(LogTask(task_config))
        elif task_config["task_type"] == "file":
            tasks.append(FileProcessingTask(task_config))
        elif task_config["task_type"] == "email":
            tasks.append(EmailTask(task_config))

    return tasks


def run_task(task):
    try:
        logging.info("Running: %s", task.task_name)
        task.execute()
        logging.info("Done: %s", task.task_name)
    except Exception as error:
        logging.error("Task failed: %s", error)


def add_to_schedule(task):
    task_schedule = task.config["schedule"]

    if task_schedule["type"] == "interval":
        minutes = task_schedule.get("minutes", 1)
        schedule.every(minutes).minutes.do(run_task, task)
        logging.info("Scheduled %s every %s minute(s)", task.task_name, minutes)

    if task_schedule["type"] == "daily":
        run_time = task_schedule.get("time", "09:00")
        schedule.every().day.at(run_time).do(run_task, task)
        logging.info("Scheduled %s every day at %s", task.task_name, run_time)


def scheduler_loop(stop_event):
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(1)


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, tasks):
        self.tasks = tasks

    def on_modified(self, event):
        self.handle_change(event)

    def handle_change(self, event):
        if event.is_directory:
            return

        changed_file = Path(event.src_path)

        for task in self.tasks:
            task_path = Path(task.file_path).resolve()
            task_folder = task_path if task_path.is_dir() else task_path.parent

            if changed_file.parent == task_folder:
                logging.info("File changed: %s", changed_file)
                run_task(task)


def start_app(config_file):
    setup_logger()
    config = load_config(config_file)
    check_config(config)
    tasks = make_tasks(config)

    for task in tasks:
        add_to_schedule(task)

    stop_event = Event()
    scheduler_thread = Thread(target=scheduler_loop, args=(stop_event,))
    scheduler_thread.start()

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
    logging.info("App started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping app...")
        stop_event.set()
        observer.stop()
        observer.join()
        scheduler_thread.join()
        logging.info("App stopped.")


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
