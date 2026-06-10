from threading import Thread
import time

import schedule


class TaskScheduler:
    def __init__(self, tasks, stop_event, logger):
        self.tasks = tasks
        self.stop_event = stop_event
        self.logger = logger
        self.thread = Thread(target=self._run_loop, daemon=True)

    def start(self):
        schedule.clear()

        for task in self.tasks:
            schedule_config = task.config["schedule"]
            if schedule_config["type"] == "interval":
                minutes = schedule_config.get("minutes", 1)
                schedule.every(minutes).minutes.do(task.run)
                self.logger.info("Scheduled '%s' every %s minute(s).", task.task_name, minutes)
            elif schedule_config["type"] == "daily":
                run_time = schedule_config.get("time", "09:00")
                schedule.every().day.at(run_time).do(task.run)
                self.logger.info("Scheduled '%s' daily at %s.", task.task_name, run_time)

        self.thread.start()

    def _run_loop(self):
        while not self.stop_event.is_set():
            try:
                schedule.run_pending()
            except Exception:
                self.logger.exception("Scheduler error")
            time.sleep(1)

    def stop(self):
        schedule.clear()
        self.thread.join(timeout=3)
