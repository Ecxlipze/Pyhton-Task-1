import time
from threading import Thread

import schedule


def safe_run(task, logger):
    try:
        logger.info("Running task: %s", task.task_name)
        task.execute()
        logger.info("Finished task: %s", task.task_name)
    except Exception as error:
        logger.error("Task failed: %s - %s", task.task_name, error)


def add_task_to_schedule(task, logger):
    task_schedule = task.config["schedule"]

    if task_schedule["type"] == "interval":
        minutes = task_schedule.get("minutes", 1)
        schedule.every(minutes).minutes.do(safe_run, task, logger)
        logger.info("Scheduled %s every %s minute(s)", task.task_name, minutes)

    if task_schedule["type"] == "daily":
        run_time = task_schedule.get("time", "09:00")
        schedule.every().day.at(run_time).do(safe_run, task, logger)
        logger.info("Scheduled %s every day at %s", task.task_name, run_time)


def scheduler_loop(stop_event, logger):
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(1)


def start_scheduler(tasks, stop_event, logger):
    schedule.clear()

    for task in tasks:
        add_task_to_schedule(task, logger)

    thread = Thread(target=scheduler_loop, args=(stop_event, logger), daemon=True)
    thread.start()
    return thread
