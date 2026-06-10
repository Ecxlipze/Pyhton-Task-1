import json
from pathlib import Path
import yaml

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
