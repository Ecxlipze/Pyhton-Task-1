# Python Automation Tool

This is a beginner-level Python mini project. It shows how to combine Python basics, OOP, config files, CLI commands, logging, scheduling, file monitoring, and simple email automation in one small app.

The app reads tasks from a JSON or YAML config file. It can run tasks on a schedule and also run tasks when watched files change.

## Features

- CLI commands with `argparse`
- JSON and YAML configuration loading
- Simple validation with friendly error messages
- OOP task classes using an abstract `BaseTask`
- Logging to terminal and `logs/app.log`
- Scheduled jobs using `schedule`
- Background scheduler thread using `threading`
- File monitoring using `watchdog`
- Email preparation using `smtplib` and `email.mime`
- Safe email dry-run mode when SMTP credentials are missing
- Simple task factory using `importlib`

## Project Structure

```text
main.py
cli/
scheduler/
tasks/
utils/
config/
examples/
```

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Show help:

```bash
python main.py --help
```

List configured tasks:

```bash
python main.py list --config examples/config.yaml
```

Start the automation tool:

```bash
python main.py start --config examples/config.yaml
```

Stop the running app:

```bash
python main.py stop
```

The app runs in the foreground, so the real shutdown command is `Ctrl+C` in the terminal where `start` is running.

## YAML Config Example

```yaml
tasks:
  - task_name: Count sample file
    task_type: file
    schedule:
      type: interval
      minutes: 1
    file_path: examples/sample.txt
```

## JSON Config Example

```json
{
  "tasks": [
    {
      "task_name": "Write demo log",
      "task_type": "log",
      "schedule": {
        "type": "interval",
        "minutes": 1
      },
      "file_path": "examples/watch_folder",
      "message": "The scheduled log task is working."
    }
  ]
}
```

## Task Types

`log`

Writes a message to the log.

`file`

Reads a file and logs simple details such as line count and word count. If the path is a folder, it logs the number of files in the folder.

`email`

Prepares an email message. If SMTP environment variables are missing, it logs a dry-run message instead of sending.

## Email Environment Variables

To send real email, set these variables:

```bash
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USER="your-user"
export SMTP_PASSWORD="your-password"
export SMTP_FROM="sender@example.com"
export SMTP_TO="receiver@example.com"
```

If these are not set, the email task still works in dry-run mode.

## Testing the Demo

Run the app:

```bash
python main.py start --config examples/config.yaml
```

In another terminal, edit `examples/sample.txt` or add a file inside `examples/watch_folder`. The watchdog monitor should detect the change and run the related task.

Check the log file:

```bash
cat logs/app.log
```

Try a broken config:

```bash
python main.py list --config examples/broken_config.yaml
```

## Python Topics Used

- Python basics: functions, dictionaries, lists, strings, and files
- Exception handling: friendly errors and task failure logging
- File handling: reading text files and writing logs
- OOP: task classes that inherit from `BaseTask`
- Modules and packages: code is split into folders
- `argparse`: CLI commands
- JSON/YAML: config file support
- `logging`: terminal and file logs
- `threading`: scheduler runs in the background
- `schedule`: interval and daily jobs
- `watchdog`: file monitoring
- `smtplib`: email sending support
- Git/GitHub: project is organized for meaningful commits and pushing
