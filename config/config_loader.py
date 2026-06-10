import json
from pathlib import Path


class ConfigError(Exception):
    """A friendly error for problems in the config file."""


REQUIRED_TASK_KEYS = ["task_name", "task_type", "schedule", "file_path"]


def load_config(config_path):
    path = Path(config_path)
    if not path.exists():
        raise ConfigError(f"Config file does not exist: {config_path}")

    try:
        if path.suffix.lower() == ".json":
            return json.loads(path.read_text(encoding="utf-8"))

        if path.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml
            except ImportError as error:
                raise ConfigError(
                    "PyYAML is required for YAML configs. Run: pip install -r requirements.txt"
                ) from error

            return yaml.safe_load(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ConfigError(f"Invalid JSON format: {error}") from error
    except Exception as error:
        if isinstance(error, ConfigError):
            raise
        raise ConfigError(f"Could not read config file: {error}") from error

    raise ConfigError("Config file must end with .json, .yaml, or .yml")


def validate_config(config, valid_task_types):
    if not isinstance(config, dict):
        raise ConfigError("Config must be a dictionary with a 'tasks' list.")

    tasks = config.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ConfigError("Config must contain a non-empty 'tasks' list.")

    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            raise ConfigError(f"Task #{index} must be a dictionary.")

        for key in REQUIRED_TASK_KEYS:
            if key not in task:
                raise ConfigError(f"Task #{index} is missing required key: {key}")

        task_type = task["task_type"]
        if task_type not in valid_task_types:
            valid = ", ".join(sorted(valid_task_types))
            raise ConfigError(
                f"Task '{task['task_name']}' has invalid task_type '{task_type}'. "
                f"Valid types are: {valid}"
            )

        _validate_schedule(task["task_name"], task["schedule"])


def _validate_schedule(task_name, schedule_config):
    if not isinstance(schedule_config, dict):
        raise ConfigError(f"Task '{task_name}' schedule must be a dictionary.")

    schedule_type = schedule_config.get("type")
    if schedule_type == "interval":
        minutes = schedule_config.get("minutes", 1)
        if not isinstance(minutes, int) or minutes < 1:
            raise ConfigError(
                f"Task '{task_name}' interval schedule needs minutes as a positive integer."
            )
        return

    if schedule_type == "daily":
        time_value = schedule_config.get("time", "09:00")
        if not isinstance(time_value, str) or len(time_value.split(":")) != 2:
            raise ConfigError(
                f"Task '{task_name}' daily schedule time must look like HH:MM."
            )
        return

    raise ConfigError(
        f"Task '{task_name}' schedule type must be either 'interval' or 'daily'."
    )
