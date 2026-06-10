import logging
import time
from threading import Event, Thread

import schedule


def run_task(task):
    try:
        logging.info("Running: %s", task.task_name)
        task.execute()
        logging.info("Done: %s", task.task_name)
    except Exception as error:
        logging.error("Task failed: %s", error)


def add_task_to_schedule(task):
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


def start_scheduler(tasks):
    for task in tasks:
        add_task_to_schedule(task)

    stop_event = Event()
    thread = Thread(target=scheduler_loop, args=(stop_event,))
    thread.start()
    return stop_event, thread
