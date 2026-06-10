from pathlib import Path

from tasks.base_task import BaseTask


class FileProcessingTask(BaseTask):
    task_type = "file"

    def execute(self):
        path = Path(self.file_path)
        if not path.exists():
            self.logger.warning("File does not exist yet: %s", path)
            return

        if path.is_dir():
            files = [item for item in path.iterdir() if item.is_file()]
            self.logger.info("Folder '%s' contains %s file(s).", path, len(files))
            return

        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        words = text.split()
        self.logger.info(
            "File '%s' has %s line(s) and %s word(s).",
            path,
            len(lines),
            len(words),
        )
