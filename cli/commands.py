import argparse
import sys
import time
from threading import Event

from config.config_loader import ConfigError, load_config, validate_config
from scheduler.file_watcher import start_file_watcher
from scheduler.task_scheduler import start_scheduler
from tasks.task_factory import create_task, get_task_types
from utils.logger import setup_logger


def build_parser():
    parser = argparse.ArgumentParser(description="Simple Python automation tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("--config", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--config", required=True)

    subparsers.add_parser("stop")
    return parser


def read_config(config_path):
    config = load_config(config_path)
    validate_config(config, get_task_types())
    return config


def list_tasks(config_path):
    config = read_config(config_path)

    print("Configured tasks:")
    for task in config["tasks"]:
        print(f"- {task['task_name']} ({task['task_type']})")


def start_app(config_path):
    logger = setup_logger()
    config = read_config(config_path)
    tasks = []

    for task_config in config["tasks"]:
        tasks.append(create_task(task_config))

    stop_event = Event()
    scheduler_thread = start_scheduler(tasks, stop_event, logger)
    observer = start_file_watcher(tasks, logger)

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


def stop_app():
    print("This simple app stops with Ctrl+C.")


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "list":
            list_tasks(args.config)
        elif args.command == "start":
            start_app(args.config)
        elif args.command == "stop":
            stop_app()
    except ConfigError as error:
        print(f"Config error: {error}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopped by user.")
