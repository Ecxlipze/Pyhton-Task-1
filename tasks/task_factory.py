from tasks.email_task import EmailTask
from tasks.file_processing_task import FileProcessingTask
from tasks.log_task import LogTask


TASK_CLASSES = {
    "log": LogTask,
    "file": FileProcessingTask,
    "email": EmailTask,
}


def get_task_types():
    return set(TASK_CLASSES)


def create_task(task_config):
    task_class = TASK_CLASSES[task_config["task_type"]]
    return task_class(task_config)
