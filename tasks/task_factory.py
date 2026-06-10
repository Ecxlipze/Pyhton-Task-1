import importlib


TASK_MODULES = [
    "tasks.log_task",
    "tasks.file_processing_task",
    "tasks.email_task",
]


def load_task_classes():
    task_classes = {}

    for module_name in TASK_MODULES:
        module = importlib.import_module(module_name)
        for value in module.__dict__.values():
            task_type = getattr(value, "task_type", None)
            if task_type and task_type != "base":
                task_classes[task_type] = value

    return task_classes


def get_task_types():
    return set(load_task_classes())


def create_task(task_config):
    task_classes = load_task_classes()
    task_type = task_config["task_type"]
    task_class = task_classes[task_type]
    return task_class(task_config)
