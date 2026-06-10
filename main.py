import sys
import time
from cli.commands import get_args
from config.config_loader import check_config, load_config
from scheduler.file_watcher import start_file_watcher
from scheduler.task_scheduler import start_scheduler
from tasks.email_task import EmailTask
from tasks.file_processing_task import FileProcessingTask
from tasks.log_task import LogTask
from utils.logger import setup_logger

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

def list_tasks(config_file):
    config = load_config(config_file)
    check_config(config)
    print("Tasks:")
    for task in config["tasks"]:
        print(f"- {task['task_name']} ({task['task_type']})")

def start_app(config_file):
    setup_logger()
    config = load_config(config_file)
    check_config(config)
    tasks = make_tasks(config)
    stop_event, scheduler_thread = start_scheduler(tasks)
    observer = start_file_watcher(tasks)

    print("App is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
        observer.stop()
        observer.join()
        scheduler_thread.join()
        print("App stopped.")

def main():
    args = get_args()
    try:
        if args.command == "list":
            list_tasks(args.config)
        elif args.command == "start":
            start_app(args.config)
        elif args.command == "stop":
            print("Use Ctrl+C to stop the running app.")
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
