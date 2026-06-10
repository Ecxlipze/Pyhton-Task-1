import argparse
import sys

from config.config_loader import ConfigError, load_config, validate_config
from scheduler.automation_app import AutomationApp
from tasks.task_factory import create_task, get_task_types
from utils.logger import setup_logger


def build_parser():
    parser = argparse.ArgumentParser(
        description="Beginner Python automation tool with CLI, scheduler, monitoring, and tasks."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start tasks from a config file")
    start_parser.add_argument("--config", required=True, help="Path to JSON or YAML config")
    start_parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    list_parser = subparsers.add_parser("list", help="List tasks from a config file")
    list_parser.add_argument("--config", required=True, help="Path to JSON or YAML config")

    subparsers.add_parser("stop", help="Show how to stop the foreground app")
    return parser


def _load_validated_config(config_path):
    config = load_config(config_path)
    validate_config(config, get_task_types())
    return config


def list_tasks(config_path):
    config = _load_validated_config(config_path)
    tasks = config["tasks"]

    print("Configured tasks:")
    for task_config in tasks:
        schedule_config = task_config["schedule"]
        if schedule_config["type"] == "interval":
            schedule_text = f"every {schedule_config.get('minutes', 1)} minute(s)"
        else:
            schedule_text = f"daily at {schedule_config.get('time', '09:00')}"

        print(
            f"- {task_config['task_name']} "
            f"({task_config['task_type']}) - {schedule_text}"
        )


def start_app(config_path, log_level):
    logger = setup_logger(log_level)
    config = _load_validated_config(config_path)

    tasks = [create_task(task_config) for task_config in config["tasks"]]
    app = AutomationApp(tasks, logger)
    app.start()


def stop_app():
    print("This beginner project runs in the foreground.")
    print("Use Ctrl+C in the running terminal to stop it cleanly.")


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "list":
            list_tasks(args.config)
        elif args.command == "start":
            start_app(args.config, args.log_level)
        elif args.command == "stop":
            stop_app()
    except ConfigError as error:
        print(f"Config error: {error}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopped by user.")
